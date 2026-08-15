/* SafeBARS StressLens — Transition Companion inspired frontend */

(function () {
  'use strict';

  const API_BASE = window.SAFEBARS_API_BASE || '/api/safebars/mirror-study';

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

  function setLoading(isLoading) {
    const el = $('#loading');
    if (isLoading) show(el); else hide(el);
  }

  function switchView(name) {
    state.currentView = name;
    $$('.view').forEach((v) => v.classList.remove('active'));
    $(`#view-${name}`).classList.add('active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function companionSay(id, text) {
    const el = $(id);
    if (!el) return;
    el.style.opacity = '0';
    setTimeout(() => {
      el.textContent = text;
      el.style.opacity = '1';
    }, 150);
  }

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
  }

  async function loadConfig() {
    try {
      setLoading(true);
      state.config = await api('/config');
      renderFixes();
    } catch (err) {
      console.error('Could not load study config', err);
      companionSay('#entry-speech', 'Could not load the study. Please refresh the page.');
    } finally {
      setLoading(false);
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
    setLoading(true);
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

    if (state.issueTheme) {
      img.src = state.issueTheme.image_url;
      label.textContent = state.issueTheme.theme_label;
      reflection.textContent = state.issueTheme.reflection;
      companionSay('#image-speech',
        `This looks related to "${state.issueTheme.theme_label}". ${state.issueTheme.reflection}`);
    } else {
      // Default StressLens vignette preview
      const theme = state.config.issue_gallery.find((t) => t.id === 'data_collection');
      img.src = theme.image_url;
      label.textContent = 'StressLens study';
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
    setLoading(true);
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
    state.config.vignette.hidden_facts.forEach((fact) => {
      const card = document.createElement('div');
      card.className = 'frame-card';
      card.innerHTML = `<h3>${fact.label}</h3><p>${fact.text}</p>`;
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
    card.style.maxWidth = '720px';
    card.style.margin = '0 auto';
    card.innerHTML = `
      <span class="entry-kicker">Week ${frame.week || ''}</span>
      <h3>${frame.title}</h3>
      <img src="${frame.image_url}" alt="${frame.title}">
      <p>${frame.caption}</p>
      <label for="frame-input">${frame.prompt}</label>
      <textarea id="frame-input" data-frame="${frame.id}"></textarea>
    `;
    container.appendChild(card);

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
    card.style.maxWidth = '720px';
    card.style.margin = '0 auto';
    card.innerHTML = `
      <span class="entry-kicker">${frame.role || 'Role'}</span>
      <h3>${frame.title}</h3>
      <img src="${frame.image_url}" alt="${frame.title}">
      <p>${frame.caption}</p>
      <label for="frame-input">${frame.prompt}</label>
      <textarea id="frame-input" data-frame="${frame.id}"></textarea>
    `;
    container.appendChild(card);

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
    state.config.fixes.forEach((fix) => {
      const card = document.createElement('div');
      card.className = 'fix-card';
      card.dataset.id = fix.id;
      card.innerHTML = `
        <img src="${fix.image_url}" alt="${fix.title}">
        <h3>${fix.title}</h3>
        <p>${fix.description}</p>
        <div class="effort">
          <span><strong>Effort:</strong> ${fix.effort}</span>
          <span><strong>Risk reduction:</strong> ${fix.risk_reduction}</span>
        </div>
      `;
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
      // Replace oldest if already 3 selected? Just alert.
      return;
    }
    refreshFixCards();
  }

  function refreshFixCards() {
    $$('.fix-card').forEach((card) => {
      const id = card.dataset.id;
      card.classList.toggle('selected', state.selectedFixes.includes(id));
      const rank = state.fixRanks[id];
      const title = card.querySelector('h3');
      const prefix = rank ? `<span style="display:inline-flex;align-items:center;justify-content:center;width:22px;height:22px;border-radius:50%;background:var(--hero-blue);color:#fff;font-size:12px;font-weight:800;margin-right:8px;">${rank}</span>` : '';
      title.innerHTML = prefix + state.config.fixes.find((f) => f.id === id).title;
    });
    $('#fix-limit-notice').textContent = `${state.selectedFixes.length} of 3 selected`;
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
      setLoading(true);
      try {
        await api(`/sessions/${state.session.session_id}/response`, {
          method: 'POST',
          body: { step: 'final', data: payload },
        });
        switchView('thank-you');
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
