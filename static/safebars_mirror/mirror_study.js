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
    analysis: null,
    currentView: 'entry',
    frameIndex: 0,
    roleIndex: 0,
    selectedFixes: [],
    fixRanks: {},
    responses: {},
    // three-stage reflection flow
    messages: [],
    issues: [],
    issuesSource: null,
    selectedIssue: null,
    timeline: null,
    chatReady: false,
  };
  let history = [];

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
    chat: ['.chat-header', '#chat-log'],
    issues: ['.condition-intro', '#issue-grid'],
    timeline: ['.timeline-head', '#timeline-stepper', '#leverage-card'],
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
    chat: 4, issues: 10, timeline: 18,
    vignette: 28, 'hidden-facts': 40, condition: 52, frames: 66,
    veil: 66, fixes: 82, tradeoff: 92, demographics: 97, 'thank-you': 100,
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
    if (state.currentView && state.currentView !== name) {
      history.push(state.currentView);
    }
    state.currentView = name;
    $$('.view').forEach((v) => v.classList.remove('active'));
    const viewEl = $(`#view-${name}`);
    viewEl.classList.add('active');
    setProgress(name);
    if (REVEAL[name]) stagger(REVEAL[name].join(','), viewEl);
    updateBackButton();
    window.scrollTo({ top: 0, behavior: REDUCED_MOTION ? 'auto' : 'smooth' });
  }

  function updateBackButton() {
    const btn = $('#btn-back');
    if (!btn) return;
    if (history.length && state.currentView !== 'entry' && state.currentView !== 'thank-you') {
      btn.removeAttribute('hidden');
    } else {
      btn.setAttribute('hidden', '');
    }
  }

  function goBack() {
    if (!history.length) return;
    const prev = history.pop();
    state.currentView = prev;
    switchView(prev);
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
    bindBack();
    bindEntry();
    bindChat();
    bindTimeline();
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

  function bindBack() {
    $('#btn-back').addEventListener('click', () => goBack());
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
      skipToVignette();
    });

    form.addEventListener('submit', async (e) => {
      e.preventDefault();
      const text = input.value.trim();
      if (!text) { skipToVignette(); return; }
      startChat(text);
    });

    const ta = $('#issue-input');
    if (ta) ta.addEventListener('input', () => autoGrow(ta));
  }

  function skipToVignette() {
    createSession().then(() => showVignette());
  }

  function autoGrow(el) {
    if (!el) return;
    el.style.height = 'auto';
    el.style.height = Math.min(el.scrollHeight, 200) + 'px';
  }

  function escapeHtml(s) {
    return String(s || '').replace(/[&<>"']/g, (c) => (
      { '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#39;' }[c]
    ));
  }

  // ---------- Stage 1: conversation ----------
  function bindChat() {
    const form = $('#chat-form');
    if (form) form.addEventListener('submit', (e) => {
      e.preventDefault();
      const input = $('#chat-input');
      const text = input.value.trim();
      if (!text) return;
      input.value = '';
      autoGrow(input);
      sendChat(text);
    });
    const ci = $('#chat-input');
    if (ci) ci.addEventListener('input', () => autoGrow(ci));
    $('#btn-summarise-issues').addEventListener('click', () => summariseIssues());
    $('#btn-issues-back').addEventListener('click', () => goBack());
  }

  function startChat(opening) {
    state.messages = [{ role: 'user', content: opening }];
    state.issues = [];
    state.issuesSource = null;
    state.selectedIssue = null;
    state.timeline = null;
    state.chatReady = false;
    renderChatBubbles();
    switchView('chat');
    setChatInputEnabled(false);
    showTyping(true);
    chatTurn().then(() => { showTyping(false); setChatInputEnabled(!state.chatReady); focusChat(); });
  }

  function renderChatBubbles() {
    const log = $('#chat-log');
    if (!log) return;
    log.innerHTML = '';
    state.messages.forEach((m) => {
      const bubble = document.createElement('div');
      bubble.className = 'bubble ' + (m.role === 'user' ? 'bubble-user' : 'bubble-assistant');
      bubble.textContent = m.content;
      log.appendChild(bubble);
    });
    log.scrollTop = log.scrollHeight;
  }

  function showTyping(on) {
    const el = $('#chat-typing');
    if (el) el.hidden = !on;
    if (on) { const log = $('#chat-log'); if (log) log.scrollTop = log.scrollHeight; }
  }

  function setChatInputEnabled(on) {
    const input = $('#chat-input');
    const btn = $('#btn-chat-send');
    if (input) input.disabled = !on;
    if (btn) btn.disabled = !on;
  }

  function focusChat() {
    const input = $('#chat-input');
    if (input && !input.disabled) input.focus();
  }

  async function chatTurn() {
    showTyping(true);
    try {
      const data = await api('/chat', { method: 'POST', body: { messages: state.messages } });
      if (!data || data.success === false) throw new Error((data && data.error) || 'chat failed');
      const reply = data.reply || '';
      const question = data.question || '';
      state.messages.push({
        role: 'assistant',
        content: reply + (question ? '\n\n' + question : ''),
      });
      renderChatBubbles();
      state.chatReady = !!data.ready;
      showReadyBox(!!data.ready);
      if (data.ready) setChatInputEnabled(false);
      return data;
    } catch (err) {
      console.error(err);
      state.messages.push({
        role: 'assistant',
        content: "Sorry — I had trouble thinking there. Could you say that another way?",
      });
      renderChatBubbles();
    } finally {
      showTyping(false);
    }
  }

  async function sendChat(text) {
    state.messages.push({ role: 'user', content: text });
    renderChatBubbles();
    setChatInputEnabled(false);
    await chatTurn();
    setChatInputEnabled(!state.chatReady);
    focusChat();
  }

  function showReadyBox(on) {
    const box = $('#chat-ready-box');
    if (box) box.hidden = !on;
  }

  // ---------- Stage 2: five concrete issues ----------
  async function summariseIssues() {
    showReadyBox(false);
    setChatInputEnabled(false);
    try {
      const data = await api('/issues', { method: 'POST', body: { messages: state.messages } });
      if (!data || data.success === false) throw new Error((data && data.error) || 'issues failed');
      state.issues = Array.isArray(data.issues) ? data.issues : [];
      state.issuesSource = data.source;
      renderIssues();
      switchView('issues');
    } catch (err) {
      console.error(err);
      alert('Could not summarise the issues right now. Please try again.');
      setChatInputEnabled(true);
    }
  }

  function renderIssues() {
    const grid = $('#issue-grid');
    if (!grid) return;
    grid.innerHTML = '';
    state.issues.forEach((iss, idx) => {
      const card = document.createElement('button');
      card.type = 'button';
      card.className = 'issue-card fx-reveal';
      card.style.setProperty('--i', idx);
      card.innerHTML = `
        <div class="issue-card-top">
          <span class="issue-num">${idx + 1}</span>
          <span class="sev-badge sev-${iss.severity}">${iss.severity}</span>
          <span class="eff-badge eff-${iss.effort}">${iss.effort} effort</span>
        </div>
        <h3 class="issue-title">${escapeHtml(iss.title)}</h3>
        <p class="issue-one-line">${escapeHtml(iss.one_line)}</p>
        <div class="issue-meta">
          <span class="issue-affected"><b>Who:</b> ${escapeHtml(iss.who_is_affected)}</span>
          <span class="issue-why">${escapeHtml(iss.why_specific)}</span>
        </div>
        <span class="issue-cta">See where this leads →</span>`;
      card.addEventListener('click', () => selectIssue(iss, card));
      grid.appendChild(card);
    });
  }

  // ---------- Stage 3: dated trajectory for one issue ----------
  async function selectIssue(issue, cardEl) {
    state.selectedIssue = issue;
    if (cardEl) {
      cardEl.classList.add('is-loading');
      cardEl.setAttribute('aria-busy', 'true');
    }
    try {
      const data = await api('/timeline', {
        method: 'POST',
        body: { issue: issue, messages: state.messages },
      });
      if (!data || data.success === false) throw new Error((data && data.error) || 'timeline failed');
      state.timeline = data;
      renderTimeline(data);
      switchView('timeline');
    } catch (err) {
      console.error(err);
      alert('Could not build the timeline right now. Please try again.');
    } finally {
      if (cardEl) {
        cardEl.classList.remove('is-loading');
        cardEl.removeAttribute('aria-busy');
      }
    }
  }

  function renderTimeline(data) {
    const focus = $('#timeline-focus');
    if (focus) focus.textContent = data.focus || (state.selectedIssue && state.selectedIssue.title) || '';

    const narr = $('#timeline-narrative');
    if (narr) narr.textContent = data.future_narrative || '';

    const lens = $('#timeline-lens');
    if (lens) {
      lens.innerHTML = '';
      if (data.if_nothing_changes) {
        const n = document.createElement('div');
        n.className = 'lens-row lens-nothing';
        n.innerHTML = `<span class="lens-tag">If nothing changes</span><span>${escapeHtml(data.if_nothing_changes)}</span>`;
        lens.appendChild(n);
      }
      if (data.if_you_act_now) {
        const a = document.createElement('div');
        a.className = 'lens-row lens-act';
        a.innerHTML = `<span class="lens-tag">If you act now</span><span>${escapeHtml(data.if_you_act_now)}</span>`;
        lens.appendChild(a);
      }
    }

    const stepper = $('#timeline-stepper');
    if (stepper) {
      stepper.innerHTML = '';
      (data.frames || []).forEach((f, i) => {
        const li = document.createElement('li');
        li.className = 'tl-node fx-reveal';
        li.style.setProperty('--i', i);
        li.innerHTML = `
          <span class="tl-time">${escapeHtml(f.when)}</span>
          <span class="tl-dot sev-${f.severity}"></span>
          <div class="tl-body">
            <div class="tl-head-row">
              <h4>${escapeHtml(f.headline)}</h4>
              <span class="sev-badge sev-${f.severity}">${f.severity}</span>
            </div>
            ${f.builds_on ? `<p class="tl-builds"><b>Develops from:</b> ${escapeHtml(f.builds_on)}</p>` : ''}
            <p>${escapeHtml(f.what_happens)}</p>
            <div class="tl-meta">
              <span><b>Who:</b> ${escapeHtml(f.who_is_affected)}</span>
              <span class="tl-signal"><b>Early signal:</b> ${escapeHtml(f.early_signal)}</span>
            </div>
          </div>`;
        stepper.appendChild(li);
      });
    }

    const lp = data.leverage_point || {};
    const card = $('#leverage-card');
    if (card) {
      card.innerHTML = `
        <h3>One place to intervene</h3>
        <p class="lp-action">${escapeHtml(lp.action || (state.selectedIssue && state.selectedIssue.changeable_decision) || '')}</p>
        <div class="lp-grid">
          <div><span class="lp-k">By when</span><span class="lp-v">${escapeHtml(lp.when || '')}</span></div>
          <div><span class="lp-k">Owner</span><span class="lp-v">${escapeHtml(lp.owner || '')}</span></div>
          <div><span class="lp-k">Cost</span><span class="lp-v">${escapeHtml(lp.cost || '')}</span></div>
        </div>
        ${data.first_step_this_week ? `<p class="lp-step"><b>First step this week:</b> ${escapeHtml(data.first_step_this_week)}</p>` : ''}
        ${data.how_to_measure ? `<p class="lp-measure"><b>You\'ll know it worked when:</b> ${escapeHtml(data.how_to_measure)}</p>` : ''}
      `;
    }
  }

  // ---------- continue into the StressLens study ----------
  function bindTimeline() {
    $('#btn-timeline-back').addEventListener('click', () => goBack());
    $('#btn-timeline-explore').addEventListener('click', async () => {
      await createSession();
      showVignette();
    });
  }

  async function createSession() {
    setLoading(true, 'Saving your reflection…');
    try {
      const body = {
        messages: state.messages || [],
        issues: state.issues || [],
        selected_issue: state.selectedIssue || null,
        timeline: state.timeline || null,
      };
      if (state.issue) body.issue = state.issue;
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
        analysis: null,
        currentView: 'entry',
        frameIndex: 0,
        roleIndex: 0,
        selectedFixes: [],
        fixRanks: {},
        responses: {},
        messages: [],
        issues: [],
        issuesSource: null,
        selectedIssue: null,
        timeline: null,
        chatReady: false,
      };
      history.length = 0;
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
      state.selectedIssue ? `<b>You focused on:</b> ${escapeHtml(state.selectedIssue.title)}` : '',
      `<b>You kept:</b> ${chosen.join(', ')}`,
      `<b>You left out:</b> ${dropped ? dropped.title : '—'}`,
      `<b>Difficulty:</b> ${$('#difficulty').value} / 7`,
    ].filter(Boolean);
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
