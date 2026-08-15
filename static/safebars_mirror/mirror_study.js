/* SafeBARS StressLens — refined companion frontend with motion layer */

(function () {
  'use strict';

  const API_BASE = window.SAFEBARS_API_BASE || '/api/safebars/mirror-study';
  const REDUCED_MOTION = window.matchMedia && window.matchMedia('(prefers-reduced-motion: reduce)').matches;

  // UI state
  let state = {
    config: null,
    session: null,
    issue: null,
    issueTheme: null,
    currentView: 'entry',
    frameIndex: 0,
    roleIndex: 0,
    selectedFixes: [],
    fixRanks: {},
    responses: {},
  };

  // DOM helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));
  const show = (el) => el && el.removeAttribute('hidden');
  const hide = (el) => el && el.setAttribute('hidden', '');

  function api(path, opts = {}) {
    const url = `${API_BASE}${path}`;
    return fetch(url, {
      headers: { 'Content-Type': 'application/json' },
      ...opts,
      body: opts.body ? JSON.stringify(opts.body) : undefined,
    }).then((r) => r.json());
  }

  function setLoading(isLoading, label) {
    const el = $('#loading');
    if (label) $('#loading-label').textContent = label;
    if (isLoading) show(el); else hide(el);
  }

  /* ---------- motion helpers ---------- */

  const REVEAL = {
    entry: ['.entry-copy', '.entry-mascot'],
    image: ['.card-layout'],
    vignette: ['.study-panel'],
    'hidden-facts': ['.condition-intro', '#hidden-facts-list'],
    condition: ['.study-panel'],
    frames: ['.frame-stage', '.nav-footer'],
    veil: ['.study-panel'],
    fixes: ['.condition-intro', '#fixes-container', '.nav-footer'],
    tradeoff: ['.tradeoff-form'],
    demographics: ['.demographics'],
    'thank-you': ['.thank-you'],
  };

  function stagger(selector, root) {
    $$(selector, root).forEach((el, i) => {
      el.style.setProperty('--i', i);
      el.classList.add('fx-reveal');
    });
  }

  const PROGRESS = {
    vignette: 12, 'hidden-facts': 24, condition: 36, frames: 54,
    veil: 54, fixes: 74, tradeoff: 88, demographics: 96, 'thank-you': 100,
  };

  function setProgress(name) {
    const bar = $('#study-progress');
    const fill = $('#study-progress-fill');
    if (!bar) return;
    if (PROGRESS[name] == null) { hide(bar); return; }
    show(bar);
    requestAnimationFrame(() => { fill.style.width = PROGRESS[name] + '%'; });
  }

  function setProgressWidth(pct) {
    const fill = $('#study-progress-fill');
    const bar = $('#study-progress');
    if (fill && bar && !bar.hidden) requestAnimationFrame(() => { fill.style.width = pct + '%'; });
  }

  function switchView(name) {
    state.currentView = name;
    $$('.view').forEach((v) => v.classList.remove('active'));
    const viewEl = $(`#view-${name}`);
    viewEl.classList.add('active');
    setProgress(name);
    if (REVEAL[name]) stagger(REVEAL[name].join(','), viewEl);
    window.scrollTo({ top: 0, behavior: REDUCED_MOTION ? 'auto' : 'smooth' });
  }

  function companionSay(id, text, typing = true) {
    const el = $(id);
    if (!el) return;
    const wiggle = () => {
      if (REDUCED_MOTION) return;
      el.classList.remove('speaking');
      void el.offsetWidth; /* restart animation */
      el.classList.add('speaking');
    };
    if (!typing || REDUCED_MOTION) { el.textContent = text; el.style.opacity = '1'; wiggle(); return; }
    el.style.opacity = '1';
    el.innerHTML = '<span class="typing-dots"><span></span><span></span><span></span></span>';
    clearTimeout(el._sayT);
    el._sayT = setTimeout(() => {
      el.style.opacity = '0';
      setTimeout(() => { el.textContent = text; el.style.opacity = '1'; wiggle(); }, 170);
    }, 620);
  }

  function sparkleBurst(host, count = 9) {
    if (!host || REDUCED_MOTION) return;
    const colors = ['var(--yellow)', 'var(--hero-blue)', 'var(--teal)', 'var(--coral)'];
    for (let i = 0; i < count; i++) {
      const s = document.createElement('span');
      s.className = 'spark';
      s.style.left = (12 + Math.random() * 76) + '%';
      s.style.top = (10 + Math.random() * 78) + '%';
      s.style.color = colors[i % colors.length];
      s.style.animationDelay = (i * 45) + 'ms';
      s.innerHTML = '<svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor"><path d="M12 2l2.2 6.3L21 9l-5 4.2L17.6 21 12 17l-5.6 4L8 13.2 3 9l6.8-.7z"/></svg>';
      host.appendChild(s);
      setTimeout(() => s.remove(), 1100);
    }
  }

  function pctOf(level) {
    const v = String(level || '').toLowerCase();
    if (v.includes('high')) return 92;
    if (v.includes('med')) return 60;
    if (v.includes('low')) return 30;
    if (v.includes('none')) return 8;
    return 50;
  }

  /* ---------- init ---------- */

  function init() {
    loadConfig();
    bindEntry();
    bindImageView();
    bindVignette();
    bindHiddenFacts();
    bindCondition();
    bindFrames();
    bindVeil();
    bindFixes();
    bindTradeoff();
    bindDemographics();
    bindDifficulty();
  }

  async function loadConfig() {
    try {
      setLoading(true, 'Loading the study…');
      state.config = await api('/config');
      renderFixes();
    } catch (err) {
      console.error('Could not load study config', err);
      companionSay('#entry-speech', 'Could not load the study. Please refresh the page.');
    } finally {
      setLoading(false);
      switchView('entry');
    }
  }

  // ---------- Entry ----------
  function bindEntry() {
    const form = $('#issue-form');
    const input = $('#issue-input');

    $('.issue-chips').addEventListener('click', (e) => {
      if (e.target.tagName === 'BUTTON') {
        input.value = e.target.dataset.chip;
        input.focus();
      }
    });

    $('#btn-skip-issue').addEventListener('click', () => {
      input.value = '';
      startWithIssue('');
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const issue = input.value.trim();
      if (!issue && !confirm("You haven't described an issue. Continue with the StressLens vignette anyway?")) {
        return;
      }
      await startWithIssue(issue);
    });
  }

  async function startWithIssue(issue) {
    state.issue = issue;
    setLoading(true, 'Matching an image…');
    try {
      let matched;
      if (issue) {
        matched = await api('/issue-image', {
          method: 'POST',
          body: { issue },
        });
        if (!matched.success) throw new Error(matched.error);
        state.issueTheme = matched;
      }
      switchView('image');
      renderIssueImage();
      sparkleBurst($('.card-layout'), 9);
    } catch (err) {
      console.error(err);
      alert('Sorry, we could not match an image right now. Please try again.');
    } finally {
      setLoading(false);
    }
  }

  // ---------- Image view ----------
  function renderIssueImage() {
    const img = $('#issue-image');
    const label = $('#theme-label');
    const reflection = $('#reflection-text');
    const ribbon = $('#theme-ribbon');

    if (state.issueTheme) {
      img.src = state.issueTheme.image_url;
      label.textContent = state.issueTheme.theme_label;
      ribbon.textContent = state.issueTheme.theme_label;
      reflection.textContent = state.issueTheme.reflection;
      companionSay('#image-speech',
        `This looks related to "${state.issueTheme.theme_label}". ${state.issueTheme.reflection}`);
    } else {
      const theme = state.config.issue_gallery.find((t) => t.id === 'data_collection');
      img.src = theme.image_url;
      label.textContent = 'StressLens study';
      ribbon.textContent = 'StressLens study';
      reflection.textContent = state.config.vignette.setting;
      companionSay('#image-speech',
        'Let’s walk through the StressLens study together. It is a useful example even if your own issue is different.');
    }
  }

  function bindImageView() {
    $('#btn-explore-stresslens').addEventListener('click', async () => {
      await createSession();
      showVignette();
    });
    $('#btn-new-issue').addEventListener('click', () => {
      $('#issue-input').value = '';
      switchView('entry');
    });
  }

  async function createSession() {
    setLoading(true, 'Setting up your session…');
    try {
      const body = {};
      if (state.issue) body.issue = state.issue;
      if (state.issueTheme) body.theme_id = state.issueTheme.theme_id;
      state.session = await api('/sessions', { method: 'POST', body });
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }

  // ---------- Vignette ----------
  function showVignette() {
    const v = state.config.vignette;
    $('#vignette-title').textContent = v.title;
    $('#vignette-setting').textContent = v.setting;
    $('#vignette-participants').textContent = v.participants;
    $('#vignette-dilemma').textContent = v.researcher_dilemma;
    switchView('vignette');
  }

  function bindVignette() {
    $('#btn-vignette-next').addEventListener('click', () => {
      renderHiddenFacts();
      switchView('hidden-facts');
    });
  }

  // ---------- Hidden facts ----------
  function renderHiddenFacts() {
    const list = $('#hidden-facts-list');
    list.innerHTML = '';
    state.config.vignette.hidden_facts.forEach((fact, i) => {
      const card = document.createElement('div');
      card.className = 'frame-card';
      card.style.setProperty('--i', i);
      card.classList.add('fx-reveal');
      card.innerHTML = `
        <span class="week-kicker">${fact.label}</span>
        <h3>${fact.label}</h3>
        <p>${fact.text}</p>`;
      list.appendChild(card);
    });
  }

  function bindHiddenFacts() {
    $('#btn-facts-next').addEventListener('click', () => {
      showConditionIntro();
    });
  }

  // ---------- Condition ----------
  function showConditionIntro() {
    const cond = state.session.condition;
    $('#condition-label').textContent = cond.label;
    $('#condition-instruction').textContent = cond.instruction;
    switchView('condition');
  }

  function bindCondition() {
    $('#btn-condition-start').addEventListener('click', () => {
      const cond = state.session.condition;
      if (cond.id === 'c2_you_could_be_anyone') {
        $('#veil-text').textContent = cond.veil_text || '';
        switchView('veil');
      } else {
        state.frameIndex = 0;
        renderFrames();
        switchView('frames');
      }
    });
  }

  // ---------- Veil (C2) ----------
  function bindVeil() {
    $('#btn-veil-next').addEventListener('click', () => {
      const answer = $('#veil-input').value.trim();
      saveResponse('veil', { answer });
      state.roleIndex = 0;
      renderRoles();
      switchView('frames');
    });
  }

  // ---------- Frames / Roles ----------
  function renderFrames() {
    const cond = state.session.condition;
    const frame = cond.frames[state.frameIndex];
    const container = $('#frames-container');
    container.innerHTML = '';

    const card = document.createElement('div');
    card.className = 'frame-card';
    card.style.setProperty('--i', 0);
    card.classList.add('fx-reveal');
    card.style.maxWidth = '720px';
    card.style.margin = '0 auto';
    card.innerHTML = `
      <span class="week-kicker">Week ${frame.week || ''}</span>
      <h3>${frame.title}</h3>
      <img src="${frame.image_url}" alt="${frame.title}">
      <p>${frame.caption}</p>
      <label for="frame-input">${frame.prompt}</label>
      <textarea id="frame-input" data-frame="${frame.id}"></textarea>
    `;
    container.appendChild(card);

    setProgressWidth(54 + (state.frameIndex / Math.max(1, cond.frames.length - 1)) * 16);
    updateFrameDots();
    $('#btn-frames-next').textContent = state.frameIndex < cond.frames.length - 1 ? 'Next' : 'Choose fixes';
  }

  function renderRoles() {
    const cond = state.session.condition;
    const frame = cond.frames[state.roleIndex];
    const container = $('#frames-container');
    container.innerHTML = '';

    const card = document.createElement('div');
    card.className = 'role-card';
    card.style.setProperty('--i', 0);
    card.classList.add('fx-reveal');
    card.style.maxWidth = '720px';
    card.style.margin = '0 auto';
    card.innerHTML = `
      <span class="role-kicker">${frame.role || 'Role'}</span>
      <h3>${frame.title}</h3>
      <img src="${frame.image_url}" alt="${frame.title}">
      <p>${frame.caption}</p>
      <label for="frame-input">${frame.prompt}</label>
      <textarea id="frame-input" data-frame="${frame.id}"></textarea>
    `;
    container.appendChild(card);

    setProgressWidth(54 + (state.roleIndex / Math.max(1, cond.frames.length - 1)) * 16);
    updateFrameDots();
    $('#btn-frames-next').textContent = state.roleIndex < cond.frames.length - 1 ? 'Next' : 'Choose fixes';
  }

  function updateFrameDots() {
    const cond = state.session.condition;
    const idx = state.session.condition.id === 'c2_you_could_be_anyone' ? state.roleIndex : state.frameIndex;
    const dots = $('#frame-dots');
    dots.innerHTML = '';
    cond.frames.forEach((_, i) => {
      const span = document.createElement('span');
      if (i < idx) span.className = 'completed';
      else if (i === idx) span.className = 'active';
      dots.appendChild(span);
    });
  }

  function bindFrames() {
    $('#btn-frames-back').addEventListener('click', () => {
      if (state.session.condition.id === 'c2_you_could_be_anyone') {
        if (state.roleIndex > 0) { state.roleIndex--; renderRoles(); }
        else { switchView('veil'); }
      } else {
        if (state.frameIndex > 0) { state.frameIndex--; renderFrames(); }
        else { switchView('condition'); }
      }
    });

    $('#btn-frames-next').addEventListener('click', () => {
      const input = $('#frame-input');
      const frameId = input.dataset.frame;
      const text = input.value.trim();
      state.responses[frameId] = text;

      const isC2 = state.session.condition.id === 'c2_you_could_be_anyone';
      const currentIdx = isC2 ? state.roleIndex : state.frameIndex;
      const total = state.session.condition.frames.length;

      if (currentIdx < total - 1) {
        if (isC2) state.roleIndex++; else state.frameIndex++;
        isC2 ? renderRoles() : renderFrames();
      } else {
        saveResponse('frames', state.responses);
        switchView('fixes');
      }
    });
  }

  // ---------- Fixes ----------
  function renderFixes() {
    if (!state.config) return;
    const container = $('#fixes-container');
    container.innerHTML = '';
    state.config.fixes.forEach((fix, i) => {
      const card = document.createElement('div');
      card.className = 'fix-card';
      card.dataset.id = fix.id;
      card.style.setProperty('--i', i);
      card.classList.add('fx-reveal');
      const ePct = pctOf(fix.effort);
      const rPct = pctOf(fix.risk_reduction);
      card.innerHTML = `
        <img src="${fix.image_url}" alt="${fix.title}">
        <h3>${fix.title}</h3>
        <p>${fix.description}</p>
        <div class="effort">
          <div class="meter">
            <div class="label-row"><span>Effort</span><strong>${fix.effort}</strong></div>
            <div class="track"><div class="fill" data-pct="${ePct}"></div></div>
          </div>
          <div class="meter">
            <div class="label-row"><span>Risk reduction</span><strong>${fix.risk_reduction}</strong></div>
            <div class="track"><div class="fill" data-pct="${rPct}"></div></div>
          </div>
        </div>`;
      card.addEventListener('click', () => toggleFix(fix.id));
      container.appendChild(card);
    });
  }

  function toggleFix(id) {
    const idx = state.selectedFixes.indexOf(id);
    if (idx > -1) {
      state.selectedFixes.splice(idx, 1);
      delete state.fixRanks[id];
    } else if (state.selectedFixes.length < 3) {
      state.selectedFixes.push(id);
      state.fixRanks[id] = state.selectedFixes.length;
    } else {
      return;
    }
    refreshFixCards();
  }

  function refreshFixCards() {
    $$('.fix-card').forEach((card) => {
      const id = card.dataset.id;
      const isSel = state.selectedFixes.includes(id);
      card.classList.toggle('selected', isSel);

      // rank badge
      let badge = card.querySelector('.rank-badge');
      const rank = state.fixRanks[id];
      if (rank && !badge) {
        badge = document.createElement('span');
        badge.className = 'rank-badge fx-pop';
        badge.textContent = rank;
        card.appendChild(badge);
      } else if (rank && badge) {
        badge.textContent = rank;
      } else if (!rank && badge) {
        badge.remove();
      }

      const title = card.querySelector('h3');
      title.innerHTML = state.config.fixes.find((f) => f.id === id).title;

      // animate effort/risk meters
      card.querySelectorAll('.effort .fill').forEach((f) => {
        requestAnimationFrame(() => { f.style.width = (f.dataset.pct || 0) + '%'; });
      });
    });
    $('#fix-limit-notice').innerHTML = `<b>${state.selectedFixes.length}</b> of 3 selected`;
    $('#btn-fixes-next').disabled = state.selectedFixes.length !== 3;
  }

  function bindFixes() {
    $('#btn-fixes-back').addEventListener('click', () => {
      const isC2 = state.session.condition.id === 'c2_you_could_be_anyone';
      if (isC2) { state.roleIndex = state.session.condition.frames.length - 1; renderRoles(); }
      else { state.frameIndex = state.session.condition.frames.length - 1; renderFrames(); }
      switchView('frames');
    });

    $('#btn-fixes-next').addEventListener('click', () => {
      saveResponse('fixes', {
        selected: state.selectedFixes,
        ranks: state.fixRanks,
      });
      populateTradeoff();
      switchView('tradeoff');
    });
  }

  // ---------- Tradeoff ----------
  function populateTradeoff() {
    const select = $('#dropped-fix');
    select.innerHTML = '';
    const unselected = state.config.fixes.filter((f) => !state.selectedFixes.includes(f.id));
    unselected.forEach((f) => {
      const opt = document.createElement('option');
      opt.value = f.id;
      opt.textContent = f.title;
      select.appendChild(opt);
    });

    const kept = $('#kept-summary');
    kept.innerHTML = '';
    state.selectedFixes.forEach((id) => {
      const fix = state.config.fixes.find((f) => f.id === id);
      const chip = document.createElement('span');
      chip.className = 'chip';
      chip.innerHTML = `<svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12l5 5 9-10"/></svg>${fix.title}`;
      kept.appendChild(chip);
    });
  }

  function bindTradeoff() {
    $('#btn-tradeoff-back').addEventListener('click', () => switchView('fixes'));
    $('#btn-tradeoff-next').addEventListener('click', () => {
      const dropped = $('#dropped-fix').value;
      const reason = $('#tradeoff-reason').value.trim();
      if (!reason) {
        alert('Please explain why you left this fix out.');
        return;
      }
      saveResponse('tradeoff', { dropped_fix_id: dropped, reason });
      switchView('demographics');
    });
  }

  // ---------- Demographics ----------
  function bindDifficulty() {
    const range = $('#difficulty');
    const update = () => {
      const pct = ((range.value - range.min) / (range.max - range.min)) * 100;
      range.style.setProperty('--range-pct', pct + '%');
    };
    range.addEventListener('input', update);
    update();
  }

  function bindDemographics() {
    $('#btn-submit').addEventListener('click', async () => {
      const difficulty = parseInt($('#difficulty').value, 10);
      const comment = $('#comment').value.trim();
      const payload = {
        condition_id: state.session.condition_id,
        selected_fixes: state.selectedFixes,
        fix_ranks: state.fixRanks,
        tradeoff: {
          dropped: $('#dropped-fix').value,
          reason: $('#tradeoff-reason').value.trim(),
        },
        difficulty,
        comment,
      };
      setLoading(true, 'Submitting…');
      try {
        await api(`/sessions/${state.session.session_id}/response`, {
          method: 'POST',
          body: { step: 'final', data: payload },
        });
        populateThankYou();
        switchView('thank-you');
        sparkleBurst($('#view-thank-you .thank-you'), 12);
      } catch (err) {
        console.error(err);
        alert('Submission failed. Please try again.');
      } finally {
        setLoading(false);
      }
    });

    $('#btn-restart').addEventListener('click', () => {
      state = {
        config: state.config,
        session: null,
        issue: null,
        issueTheme: null,
        currentView: 'entry',
        frameIndex: 0,
        roleIndex: 0,
        selectedFixes: [],
        fixRanks: {},
        responses: {},
      };
      $('#issue-input').value = '';
      $('#frame-input') && ($('#frame-input').value = '');
      $('#veil-input').value = '';
      $('#tradeoff-reason').value = '';
      $('#comment').value = '';
      refreshFixCards();
      switchView('entry');
    });
  }

  function populateThankYou() {
    const recap = $('#thankyou-recap');
    const cond = state.session.condition;
    const chosen = state.selectedFixes.map((id) => state.config.fixes.find((f) => f.id === id).title);
    const dropped = state.config.fixes.find((f) => f.id === $('#dropped-fix').value);
    const items = [
      `<b>Condition:</b> ${cond.label}`,
      `<b>You kept:</b> ${chosen.join(', ')}`,
      `<b>You left out:</b> ${dropped ? dropped.title : '—'}`,
      `<b>Difficulty:</b> ${$('#difficulty').value} / 7`,
    ];
    recap.innerHTML = items.map((t) => `<li>${t}</li>`).join('');
  }

  async function saveResponse(step, data) {
    if (!state.session) return;
    try {
      await api(`/sessions/${state.session.session_id}/response`, {
        method: 'POST',
        body: { step, data },
      });
    } catch (err) {
      console.error('Could not save response', err);
    }
  }

  init();
})();
