(() => {
  'use strict';

  const API_BASE = '/api/safebars/mirror-study';

  // Application state
  const state = {
    session: null,
    config: null,
    condition: null,
    vignette: null,
    fixes: null,
    step: 'landing',
    c1Index: 0,
    c2Index: 0,
    selectedFixes: [],
    fixRanks: {},
    frameResponses: {},
    roleResponses: {},
    veilResponse: '',
    tradeoffDropped: null,
    tradeoffText: '',
    difficulty: null,
  };

  // DOM helpers
  const $ = (sel, root = document) => root.querySelector(sel);
  const $$ = (sel, root = document) => Array.from(root.querySelectorAll(sel));

  function showStep(name) {
    state.step = name;
    $$('.ms-step').forEach(el => el.classList.remove('ms-step--active'));
    $(`#step-${name}`).classList.add('ms-step--active');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  }

  function showError(msg) {
    const el = $('#ms-error');
    el.textContent = msg;
    el.style.display = 'block';
    setTimeout(() => { el.style.display = 'none'; }, 6000);
  }

  async function api(method, path, body) {
    const opts = {
      method,
      headers: { 'Content-Type': 'application/json' },
    };
    if (body) opts.body = JSON.stringify(body);
    const res = await fetch(`${API_BASE}${path}`, opts);
    const data = await res.json().catch(() => ({}));
    if (!res.ok || !data.success) {
      throw new Error(data.error || `HTTP ${res.status}`);
    }
    return data;
  }

  async function saveResponse(step, data) {
    if (!state.session) return;
    try {
      await api('POST', `/sessions/${state.session.session_id}/response`, { step, data });
    } catch (err) {
      showError('Could not auto-save your answer. Please continue; your final submit will still work.');
    }
  }

  // ---------- Landing ----------
  $('#btn-start').addEventListener('click', async () => {
    $('#btn-start').disabled = true;
    $('#btn-start').textContent = 'Loading...';
    try {
      const session = await api('POST', '/sessions');
      state.session = session;
      state.condition = session.condition;
      state.vignette = session.vignette;
      state.fixes = session.fixes;
      renderVignette();
      showStep('vignette');
    } catch (err) {
      showError('Could not start the study: ' + err.message);
      $('#btn-start').disabled = false;
      $('#btn-start').textContent = 'Start';
    }
  });

  // ---------- Vignette ----------
  function renderVignette() {
    $('#vignette-setting').textContent = state.vignette.setting;
    $('#vignette-participants').textContent = state.vignette.participants;
    const list = $('#vignette-hidden');
    list.innerHTML = '';
    state.vignette.hidden_facts.forEach(fact => {
      const li = document.createElement('li');
      li.innerHTML = `<strong>${fact.label}.</strong> ${fact.text}`;
      list.appendChild(li);
    });
    $('#vignette-dilemma').textContent = state.vignette.researcher_dilemma;
  }

  $('#btn-vignette-next').addEventListener('click', () => {
    renderConditionIntro();
    showStep('condition-intro');
  });

  // ---------- Condition Intro ----------
  function renderConditionIntro() {
    const c = state.condition;
    const container = $('#condition-intro-content');
    const isC1 = c.id === 'c1_nothing_changes';
    container.innerHTML = `
      <div class="ms-card ms-card--accent">
        <h3>${c.label}</h3>
        <p>${c.instruction}</p>
        <p class="ms-meta">${c.frame_intro}</p>
      </div>
    `;
    $('#btn-condition-start').textContent = isC1 ? 'View timeline' : 'Enter the veil';
  }

  $('#btn-condition-start').addEventListener('click', () => {
    if (state.condition.id === 'c1_nothing_changes') {
      state.c1Index = 0;
      renderC1Frame();
      showStep('c1-timeline');
    } else {
      $('#c2-veil-text').textContent = state.condition.veil_text;
      showStep('c2-veil');
    }
  });

  // ---------- C1 Timeline ----------
  function renderC1Frame() {
    const frames = state.condition.frames;
    const frame = frames[state.c1Index];
    const progress = 30 + Math.round((state.c1Index / frames.length) * 35);
    $('#c1-progress').style.width = `${progress}%`;

    const saved = state.frameResponses[frame.id] || '';
    $('#c1-frame-container').innerHTML = `
      <div class="ms-frame">
        <div class="ms-frame__meta">Week ${frame.week} · ${state.c1Index + 1} / ${frames.length}</div>
        <h3>${frame.title}</h3>
        <img src="${frame.image_url}" alt="${frame.title}" class="ms-frame__img" loading="lazy">
        <p class="ms-frame__caption">${frame.caption}</p>
        <label class="ms-field">
          <span>${frame.prompt}</span>
          <textarea data-frame-id="${frame.id}" rows="2" maxlength="400">${saved}</textarea>
        </label>
      </div>
    `;
    $('#btn-c1-prev').style.visibility = state.c1Index === 0 ? 'hidden' : 'visible';
    $('#btn-c1-next').textContent = state.c1Index === frames.length - 1 ? 'Choose fixes' : 'Next';
  }

  $('#btn-c1-prev').addEventListener('click', () => {
    captureC1Response();
    if (state.c1Index > 0) {
      state.c1Index--;
      renderC1Frame();
    }
  });

  $('#btn-c1-next').addEventListener('click', () => {
    captureC1Response();
    const frames = state.condition.frames;
    if (state.c1Index < frames.length - 1) {
      state.c1Index++;
      renderC1Frame();
    } else {
      saveResponse('frames', state.frameResponses);
      renderFixes();
      showStep('fixes');
    }
  });

  function captureC1Response() {
    const ta = $('#c1-frame-container textarea');
    if (!ta) return;
    state.frameResponses[ta.dataset.frameId] = ta.value.trim();
  }

  // ---------- C2 Veil + Roles ----------
  $('#btn-c2-veil-next').addEventListener('click', () => {
    state.c2Index = 0;
    renderC2Role();
    showStep('c2-roles');
  });

  function renderC2Role() {
    const frames = state.condition.frames;
    const frame = frames[state.c2Index];
    const progress = 35 + Math.round((state.c2Index / frames.length) * 35);
    $('#c2-progress').style.width = `${progress}%`;

    const saved = state.roleResponses[frame.id] || '';
    $('#c2-role-container').innerHTML = `
      <div class="ms-frame">
        <div class="ms-frame__meta">${frame.role} · ${state.c2Index + 1} / ${frames.length}</div>
        <h3>${frame.title}</h3>
        <img src="${frame.image_url}" alt="${frame.title}" class="ms-frame__img" loading="lazy">
        <p class="ms-frame__caption">${frame.caption}</p>
        <label class="ms-field">
          <span>${frame.prompt}</span>
          <textarea data-role-id="${frame.id}" rows="2" maxlength="400">${saved}</textarea>
        </label>
      </div>
    `;
    $('#btn-c2-prev').style.visibility = state.c2Index === 0 ? 'hidden' : 'visible';
    $('#btn-c2-next').textContent = state.c2Index === frames.length - 1 ? 'Choose fixes' : 'Next';
  }

  $('#btn-c2-prev').addEventListener('click', () => {
    captureC2Response();
    if (state.c2Index > 0) {
      state.c2Index--;
      renderC2Role();
    }
  });

  $('#btn-c2-next').addEventListener('click', () => {
    captureC2Response();
    const frames = state.condition.frames;
    if (state.c2Index < frames.length - 1) {
      state.c2Index++;
      renderC2Role();
    } else {
      saveResponse('roles', state.roleResponses);
      renderFixes();
      showStep('fixes');
    }
  });

  function captureC2Response() {
    const ta = $('#c2-role-container textarea');
    if (!ta) return;
    state.roleResponses[ta.dataset.roleId] = ta.value.trim();
  }

  // ---------- Fix Selection ----------
  function renderFixes() {
    const grid = $('#fixes-grid');
    grid.innerHTML = '';
    state.fixes.forEach(fix => {
      const card = document.createElement('div');
      card.className = 'ms-fix-card';
      card.dataset.id = fix.id;
      card.innerHTML = `
        <img src="${fix.image_url}" alt="${fix.title}" loading="lazy">
        <div class="ms-fix-card__body">
          <h4>${fix.title}</h4>
          <p>${fix.description}</p>
          <div class="ms-badges">
            <span class="ms-badge ms-badge--effort">Effort: ${fix.effort}</span>
            <span class="ms-badge ms-badge--risk">Risk reduction: ${fix.risk_reduction}</span>
          </div>
        </div>
      `;
      card.addEventListener('click', () => toggleFix(fix.id));
      grid.appendChild(card);
    });
    updateFixSelection();
  }

  function toggleFix(id) {
    const idx = state.selectedFixes.indexOf(id);
    if (idx >= 0) {
      state.selectedFixes.splice(idx, 1);
      delete state.fixRanks[id];
    } else if (state.selectedFixes.length < 3) {
      state.selectedFixes.push(id);
      state.fixRanks[id] = state.selectedFixes.length;
    }
    normalizeRanks();
    updateFixSelection();
  }

  function normalizeRanks() {
    state.selectedFixes.forEach((id, i) => {
      state.fixRanks[id] = i + 1;
    });
  }

  function updateFixSelection() {
    $$('.ms-fix-card').forEach(card => {
      const id = card.dataset.id;
      const selected = state.selectedFixes.includes(id);
      card.classList.toggle('ms-fix-card--selected', selected);
      const rank = state.fixRanks[id];
      card.style.setProperty('--rank', rank ? `"${rank}"` : '""');
    });

    const rankList = $('#fix-rank-list');
    rankList.innerHTML = '';
    if (state.selectedFixes.length === 0) {
      rankList.innerHTML = '<li class="ms-rank-empty">Select fixes above to rank them.</li>';
    } else {
      state.selectedFixes.forEach((id, i) => {
        const fix = state.fixes.find(f => f.id === id);
        const li = document.createElement('li');
        li.innerHTML = `
          <span class="ms-rank-num">${i + 1}</span>
          <span class="ms-rank-title">${fix.title}</span>
          <button class="ms-rank-up" data-id="${id}" ${i === 0 ? 'disabled' : ''}>▲</button>
          <button class="ms-rank-down" data-id="${id}" ${i === state.selectedFixes.length - 1 ? 'disabled' : ''}>▼</button>
        `;
        rankList.appendChild(li);
      });
    }
    $('#fix-rank-panel').style.display = state.selectedFixes.length ? 'block' : 'none';
    $('#btn-fixes-next').disabled = state.selectedFixes.length !== 3;

    $$('.ms-rank-up').forEach(btn => {
      btn.addEventListener('click', e => moveFix(e.target.dataset.id, -1));
    });
    $$('.ms-rank-down').forEach(btn => {
      btn.addEventListener('click', e => moveFix(e.target.dataset.id, 1));
    });
  }

  function moveFix(id, dir) {
    const idx = state.selectedFixes.indexOf(id);
    const newIdx = idx + dir;
    if (newIdx < 0 || newIdx >= state.selectedFixes.length) return;
    [state.selectedFixes[idx], state.selectedFixes[newIdx]] =
      [state.selectedFixes[newIdx], state.selectedFixes[idx]];
    normalizeRanks();
    updateFixSelection();
  }

  $('#btn-fixes-next').addEventListener('click', () => {
    saveResponse('fixes', {
      selected: state.selectedFixes,
      ranks: state.fixRanks,
    });
    renderTradeoff();
    showStep('tradeoff');
  });

  // ---------- Trade-off ----------
  function renderTradeoff() {
    const options = state.fixes.filter(f => !state.selectedFixes.includes(f.id));
    const container = $('#tradeoff-options');
    container.innerHTML = '';
    options.forEach(fix => {
      const btn = document.createElement('button');
      btn.className = 'ms-tradeoff-btn';
      btn.textContent = `${fix.title} (effort ${fix.effort}, risk ↓${fix.risk_reduction})`;
      btn.dataset.id = fix.id;
      btn.addEventListener('click', () => {
        state.tradeoffDropped = fix.id;
        $$('.ms-tradeoff-btn').forEach(b => b.classList.remove('ms-tradeoff-btn--active'));
        btn.classList.add('ms-tradeoff-btn--active');
        checkTradeoffReady();
      });
      container.appendChild(btn);
    });
  }

  $('#tradeoff-text').addEventListener('input', e => {
    state.tradeoffText = e.target.value.trim();
    checkTradeoffReady();
  });

  function checkTradeoffReady() {
    $('#btn-tradeoff-next').disabled = !(state.tradeoffDropped && state.tradeoffText.length > 5);
  }

  $('#btn-tradeoff-next').addEventListener('click', () => {
    saveResponse('tradeoff', {
      dropped_fix_id: state.tradeoffDropped,
      reason: state.tradeoffText,
    });
    showStep('final');
  });

  // ---------- Final ----------
  $$('#difficulty-likert button').forEach(btn => {
    btn.addEventListener('click', () => {
      state.difficulty = parseInt(btn.dataset.value, 10);
      $$('#difficulty-likert button').forEach(b => b.classList.remove('ms-likert--active'));
      btn.classList.add('ms-likert--active');
    });
  });

  $('#btn-submit').addEventListener('click', async () => {
    $('#btn-submit').disabled = true;
    $('#btn-submit').textContent = 'Submitting...';
    try {
      await saveResponse('demographics', {
        difficulty: state.difficulty,
        comment: $('#final-comment').value.trim(),
      });
      await saveResponse('final', {
        condition_id: state.condition.id,
        selected_fixes: state.selectedFixes,
        fix_ranks: state.fixRanks,
        tradeoff: { dropped: state.tradeoffDropped, reason: state.tradeoffText },
      });
      $('#done-session-id').textContent = `Reference: ${state.session.session_id}`;
      showStep('done');
    } catch (err) {
      showError('Submit failed: ' + err.message);
      $('#btn-submit').disabled = false;
      $('#btn-submit').textContent = 'Submit';
    }
  });
})();
