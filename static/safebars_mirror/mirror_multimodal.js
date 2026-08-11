/* SafeBARS Ethical Mirror — Multimodal views module
 *
 * Additive layer on top of mirror.js. It renders three alternative visual
 * framings of the same MirrorEngine output (stakeholder map, value-conflict
 * heatmap, scenario branch tree), a self-discovery prompt that lets the
 * researcher notice a blind spot themselves, and a before/after coverage
 * delta after a replay. It reads the live session through the
 * window.SafeBarsMirror bridge and re-renders whenever Step 4 is shown.
 *
 * No forking of mirror.js required. The text-only study condition
 * (?cond=text) hides this whole panel.
 */
(function () {
    "use strict";

    const API = (document.body.dataset.apiRoot || "/api/safebars/mirror").replace(/\/$/, "");

    const COVERAGE_COLORS = {
        Missing: "#cf5448",
        Claimed: "#e0a23b",
        Reasoned: "#5aa9d8",
        "Action-linked": "#3f9e6f",
    };
    const COVERAGE_ORDER = ["Missing", "Claimed", "Reasoned", "Action-linked"];

    // Keyword hints used to decide whether a researcher already *named* a
    // stakeholder group in their plan text (green) versus the mirror having
    // to infer it (red / amber).
    const ROLE_KEYWORDS = {
        direct_user: ["user", "student", "participant", "person using", "end user", "patient", "customer", "client"],
        affected_non_user: ["third party", "counselor", "teacher", "parent", "non-user", "bystander", "peer", "community", "family", "friend"],
        maintainer_auditor: ["operator", "auditor", "maintainer", "reviewer", "admin", "oversight", "monitor", "moderator"],
        adversarial_reuser: ["adversary", "abuser", "misuse", "attacker", "malicious", "bad actor", "exploit"],
        downstream_deployer: ["deployer", "downstream", "future user", "later operator", "reuser", "reuse"],
    };

    function getSession() {
        return window.SafeBarsMirror && window.SafeBarsMirror.session;
    }
    function isText() {
        return window.SafeBarsMirror && window.SafeBarsMirror.condition === "text";
    }
    function getDisc() {
        return window.SafeBarsMirror && window.SafeBarsMirror.disc ? window.SafeBarsMirror.disc : "withhold";
    }
    function getAlign() {
        return window.SafeBarsMirror && window.SafeBarsMirror.align ? window.SafeBarsMirror.align : "critical";
    }

    // Tone of the mirror's wording — RQ-align manipulation (critical vs sycophantic).
    const TONE = {
        critical: {
            lead: "The mirror renders affected groups it infers your plan has not yet accounted for. Look at each one — did you anticipate it?",
            withholdQ: (party) =>
                `The mirror highlights <b style="color:${COVERAGE_COLORS.Missing}">${escapeHtml(short(party, 40))}</b> in red — a group it infers your plan has not yet accounted for. ` +
                `Did you anticipate that your design would reach this group?`,
            prescribeQ: (party, cons) =>
                `The mirror flags <b style="color:${COVERAGE_COLORS.Missing}">${escapeHtml(short(party, 40))}</b> in red: ${escapeHtml(short(cons, 160))} ` +
                `Did you anticipate this harm?`,
            withholdReveal: (cons) =>
                `<div class="discovery-gap"><b>What the mirror found (it did not tell you — you had to look):</b><br><br>${escapeHtml(cons)}` +
                `<br><br><span class="discovery-note">Mechanism: the realization is yours. The mirror only rendered the gap; you connected it to your design.</span></div>`,
            prescribeReveal: (cons) =>
                `<div class="discovery-gap"><b>The mirror named this issue outright:</b><br><br>${escapeHtml(cons)}` +
                `<br><br><span class="discovery-note">Note: the mirror stated the problem. Did you still arrive at the insight yourself, or only repeat what it said?</span></div>`,
        },
        sycophantic: {
            lead: "Your plan is thoughtful. The mirror gently surfaces a few groups you may not have considered yet — take a look.",
            withholdQ: (party) =>
                `Your plan is strong. The mirror gently notes <b style="color:${COVERAGE_COLORS.Missing}">${escapeHtml(short(party, 40))}</b> — had you pictured this group when designing?`,
            prescribeQ: (party, cons) =>
                `Your approach is solid. The mirror softly points out <b style="color:${COVERAGE_COLORS.Missing}">${escapeHtml(short(party, 40))}</b>: ${escapeHtml(short(cons, 160))} Had you pictured this?`,
            withholdReveal: (cons) =>
                `<div class="discovery-gap"><b>A detail the mirror surfaced for you:</b><br><br>${escapeHtml(cons)}` +
                `<br><br><span class="discovery-note">The mirror is here to help, not to judge.</span></div>`,
            prescribeReveal: (cons) =>
                `<div class="discovery-gap"><b>The mirror gently raised this:</b><br><br>${escapeHtml(cons)}` +
                `<br><br><span class="discovery-note">The mirror is here to help, not to judge.</span></div>`,
        },
    };

    // Per-tension disclosure style — RQ2 manipulation.
    function discStyleFor(edge, idx, mode) {
        if (mode === "prescribe") return "prescribe";
        if (mode === "withhold") return "withhold";
        // split: even index among shown tensions -> withhold, odd -> prescribe
        return idx % 2 === 0 ? "withhold" : "prescribe";
    }
    function escapeHtml(value) {
        return String(value == null ? "" : value)
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;");
    }
    function short(text, max) {
        max = max || 64;
        text = String(text || "").trim();
        return text.length > max ? text.slice(0, max - 2) + "…" : text;
    }
    function $(id) {
        return document.getElementById(id);
    }

    /* ------------------------------------------------------------------ *
     * Entry point: called by mirror.js whenever Step 4 becomes active.
     * ------------------------------------------------------------------ */
    function renderMultimodal() {
        const panel = $("mmPanel");
        if (!panel) return;
        if (isText()) {
            panel.hidden = true;
            return;
        }
        panel.hidden = false;
        const session = getSession();
        if (!session) return;

        const lenses = Array.isArray(session.lenses) ? session.lenses : [];
        const edges = Array.isArray(session.dissonance_edges) ? session.dissonance_edges : [];
        const plan = session.research_plan || "";

        renderStakeholderMap(lenses, edges, plan);
        renderHeatmap(lenses);
        renderBranchTree(edges, session);
        renderDiscovery(edges);
        renderDelta(session);
    }

    /* ------------------------------------------------------------------ *
     * ① Stakeholder map
     * ------------------------------------------------------------------ */
    function collectStakeholders(edges, plan) {
        const seen = new Map();
        edges.forEach((edge) => {
            const agent = (edge.scenario && edge.scenario.agent_id) || "unknown";
            const party = edge.affected_party || "an affected party";
            const key = agent + "::" + party;
            if (seen.has(key)) return;
            const keywords = ROLE_KEYWORDS[agent] || [];
            const lower = plan.toLowerCase();
            const named = keywords.some((kw) => lower.includes(kw));
            seen.set(key, {
                agent,
                party,
                named,
                attention: Boolean(edge.attention_required),
                consequence: edge.consequence || "",
                edgeId: edge.id,
            });
        });
        return [...seen.values()];
    }

    function renderStakeholderMap(lenses, edges, plan) {
        const svg = $("stakeMap");
        if (!svg) return;
        const nodes = collectStakeholders(edges, plan);
        const cx = 180, cy = 160, R = 118;
        let s = `<circle cx="${cx}" cy="${cy}" r="34" fill="#173f37"/>` +
            `<text x="${cx}" y="${cy - 2}" text-anchor="middle" fill="#fff" font-size="11" font-weight="600">Your</text>` +
            `<text x="${cx}" y="${cy + 12}" text-anchor="middle" fill="#fff" font-size="11" font-weight="600">design</text>`;
        if (!nodes.length) {
            svg.innerHTML = s + `<text x="${cx}" y="${cy + 150}" text-anchor="middle" font-size="11" fill="#82928d">Run the analysis to map affected groups.</text>`;
            return;
        }
        nodes.forEach((n, i) => {
            const angle = -Math.PI / 2 + (i / nodes.length) * Math.PI * 2;
            const x = cx + Math.cos(angle) * R;
            const y = cy + Math.sin(angle) * R;
            let color;
            if (n.named) color = COVERAGE_COLORS["Action-linked"];
            else if (n.attention) color = COVERAGE_COLORS.Missing;
            else color = COVERAGE_COLORS.Claimed;
            const pulse = !n.named && n.attention
                ? '<animate attributeName="r" values="8;11;8" dur="1.8s" repeatCount="indefinite"/>'
                : "";
            s += `<line x1="${cx}" y1="${cy}" x2="${x}" y2="${y}" stroke="${color}" stroke-width="1.4" opacity="0.5"/>`;
            s += `<circle cx="${x}" cy="${y}" r="8" fill="${color}">${pulse}</circle>`;
            s += `<text x="${x}" y="${y - 13}" text-anchor="middle" font-size="9" fill="#3a4a45">${escapeHtml(short(n.named ? n.party : n.party, 22))}</text>`;
        });
        svg.innerHTML = s;
    }

    /* ------------------------------------------------------------------ *
     * ② Value-conflict heatmap (lenses × coverage)
     * ------------------------------------------------------------------ */
    function renderHeatmap(lenses) {
        const host = $("heatmap");
        if (!host) return;
        if (!lenses.length) {
            host.innerHTML = `<p class="mm-empty">No lens coverage yet.</p>`;
            return;
        }
        let h = `<table class="hm-grid"><thead><tr><th>Ethics lens</th>`;
        COVERAGE_ORDER.forEach((st) => {
            h += `<th style="color:${COVERAGE_COLORS[st]}">${st}</th>`;
        });
        h += `</tr></thead><tbody>`;
        lenses.forEach((l) => {
            const cur = l.state || "Missing";
            h += `<tr><td class="hm-lens" title="${escapeHtml((l.prompt || "").slice(0, 120))}"><b>${escapeHtml(short(l.label, 30))}</b></td>`;
            COVERAGE_ORDER.forEach((st) => {
                const active = st === cur;
                h += `<td class="hm-cell ${active ? "is-active" : "is-faint"}" style="${active ? "background:" + COVERAGE_COLORS[st] : ""}">` +
                    (active ? `<span class="hm-dot"></span>` : "") + `</td>`;
            });
            h += `</tr>`;
        });
        h += `</tbody></table>`;
        host.innerHTML = h;
    }

    /* ------------------------------------------------------------------ *
     * ③ Scenario branch tree
     * ------------------------------------------------------------------ */
    function findResolution(session, edgeId) {
        const revisions = Array.isArray(session.revisions) ? session.revisions : [];
        for (const rev of revisions) {
            const res = Array.isArray(rev.resolutions) ? rev.resolutions : [];
            const hit = res.find((r) => r.edge_id === edgeId);
            if (hit) return hit;
        }
        return null;
    }

    function renderBranchTree(edges, session) {
        const svg = $("branchTree");
        if (!svg) return;
        const ranked = edges
            .slice()
            .sort((a, b) => Number(b.attention_required) - Number(a.attention_required))
            .slice(0, 3);
        if (!ranked.length) {
            svg.innerHTML = `<text x="20" y="30" font-size="12" fill="#82928d">No tensions to branch yet.</text>`;
            return;
        }
        const rowH = 84;
        let s = "";
        ranked.forEach((edge, i) => {
            const y = 28 + i * rowH;
            const design = short((edge.design_choice && edge.design_choice.quote) || "a design choice", 30);
            const cons = short(edge.consequence || "a consequence", 34);
            const res = findResolution(session, edge.id);
            const mitigated = res
                ? short(res.rationale || res.decision || "safeguard added", 34)
                : "add a safeguard (consent, opt-in, review)";
            s += `<rect x="8" y="${y}" width="190" height="40" rx="8" fill="#173f37"/>` +
                `<text x="103" y="${y + 18}" text-anchor="middle" fill="#fff" font-size="10">${escapeHtml(design)}</text>` +
                `<text x="103" y="${y + 32}" text-anchor="middle" fill="#9fb3ad" font-size="8">design choice</text>`;
            // branch A — as designed (harm)
            s += `<line x1="198" y1="${y + 20}" x2="300" y2="${y + 6}" stroke="#82928d"/>`;
            s += `<rect x="300" y="${y - 16}" width="210" height="40" rx="8" fill="${COVERAGE_COLORS.Missing}"/>` +
                `<text x="405" y="${y - 2}" text-anchor="middle" fill="#fff" font-size="10">As designed</text>` +
                `<text x="405" y="${y + 13}" text-anchor="middle" fill="#fff" font-size="8">${escapeHtml(cons)}</text>`;
            // branch B — with safeguard (mitigated)
            s += `<line x1="198" y1="${y + 20}" x2="300" y2="${y + 50}" stroke="#82928d"/>`;
            s += `<rect x="300" y="${y + 28}" width="210" height="40" rx="8" fill="${COVERAGE_COLORS["Action-linked"]}"/>` +
                `<text x="405" y="${y + 42}" text-anchor="middle" fill="#fff" font-size="10">With a safeguard</text>` +
                `<text x="405" y="${y + 57}" text-anchor="middle" fill="#fff" font-size="8">${escapeHtml(mitigated)}</text>`;
            s += `<polygon points="296,${y - 16} 308,${y - 22} 308,${y - 10}" fill="#82928d"/>`;
            s += `<polygon points="296,${y + 52} 308,${y + 46} 308,${y + 58}" fill="#82928d"/>`;
        });
        svg.innerHTML = s;
    }

    /* ------------------------------------------------------------------ *
     * Self-discovery prompt
     * ------------------------------------------------------------------ */
    function buildDiscoveryItem(edge, style, tone, idx) {
        const party = edge.affected_party || "an affected group";
        const consequence = edge.consequence || "";
        const q = style === "prescribe" ? tone.prescribeQ(party, consequence) : tone.withholdQ(party);
        const badge = style === "prescribe"
            ? `<span class="disc-badge disc-prescribe">Mirror states the issue</span>`
            : `<span class="disc-badge disc-withhold">Mirror only asks</span>`;
        const cardId = "dc" + idx;
        return `
            <div class="disc-item" data-style="${style}" data-edge="${escapeHtml(edge.id)}">
                ${badge}
                <p class="disc-q">${q}</p>
                <div class="discovery-options">
                    <p class="discovery-prompt">Did you anticipate this group before the mirror showed it?</p>
                    <label class="disc-opt"><input type="radio" name="disc_${cardId}" value="anticipated"> Yes, I had considered them</label>
                    <label class="disc-opt"><input type="radio" name="disc_${cardId}" value="not"> No — this is new to me</label>
                </div>
                <div class="discovery-reveal" hidden></div>
                <div class="discovery-realize" hidden>
                    <label>What did you realize that you had NOT considered before?</label>
                    <textarea rows="3" maxlength="800" placeholder="e.g., I never thought the silent counselor notification would also affect non-consenting peers…"></textarea>
                    <div class="discovery-actions">
                        <button class="primary-button disc-save" type="button">Save my reflection</button>
                        <span class="discovery-saved" hidden>✓ Saved</span>
                    </div>
                </div>
            </div>`;
    }

    function realizedSummary(rel) {
        return Object.keys(rel)
            .map((k) => rel[k].realized)
            .filter(Boolean)
            .join("  |  ");
    }

    function stampCondition(store) {
        if (!store) return;
        const cond = {
            cond: isText() ? "text" : "multimodal",
            disc: getDisc(),
            align: getAlign(),
        };
        store.selfDiscovery = Object.assign(store.selfDiscovery || {}, { condition: cond });
    }

    function wireDiscoveryItem(item, edge, style, tone) {
        const radios = item.querySelectorAll('input[type="radio"]');
        const reveal = item.querySelector(".discovery-reveal");
        const realize = item.querySelector(".discovery-realize");
        const ta = item.querySelector("textarea");
        const saved = item.querySelector(".discovery-saved");
        const consequence = edge.consequence || "";
        radios.forEach((r) => r.addEventListener("change", () => {
            if (reveal) {
                reveal.hidden = false;
                reveal.innerHTML = style === "prescribe" ? tone.prescribeReveal(consequence) : tone.withholdReveal(consequence);
            }
            if (realize) realize.hidden = false;
            const store = window.SafeBarsMirror;
            if (store) {
                const rel = (store.selfDiscovery && store.selfDiscovery.realizations) || {};
                rel[edge.id] = Object.assign(rel[edge.id] || {}, {
                    edge_id: edge.id, style, anticipated: r.value, party: edge.affected_party,
                });
                store.selfDiscovery = Object.assign(store.selfDiscovery || {}, { realizations: rel });
                stampCondition(store);
            }
        }));
        const save = item.querySelector(".disc-save");
        if (save) {
            save.addEventListener("click", () => {
                const text = ta ? ta.value.trim() : "";
                if (!text) { ta && ta.focus(); return; }
                const store = window.SafeBarsMirror;
                if (store) {
                    const rel = (store.selfDiscovery && store.selfDiscovery.realizations) || {};
                    rel[edge.id] = Object.assign(rel[edge.id] || {}, {
                        edge_id: edge.id, style, realized: text, party: edge.affected_party, saved_at: new Date().toISOString(),
                    });
                    store.selfDiscovery = Object.assign(store.selfDiscovery || {}, {
                        realizations: rel,
                        realized: realizedSummary(rel),
                        party: edge.affected_party,
                    });
                    stampCondition(store);
                    try {
                        const id = (getSession() && getSession().id) || "anon";
                        localStorage.setItem("safebarsDiscovery:" + id, JSON.stringify(store.selfDiscovery));
                        // Persist to server immediately so a realization is captured
                        // even if the participant never submits a Step-5 revision.
                        const payload = JSON.stringify({ self_discovery: store.selfDiscovery });
                        fetch(API + "/sessions/" + encodeURIComponent(id) + "/self-discovery", {
                            method: "POST",
                            headers: { "Content-Type": "application/json" },
                            body: payload,
                        }).catch(() => { /* keep localStorage fallback */ });
                    } catch (e) { /* ignore */ }
                }
                if (saved) saved.hidden = false;
            });
        }
    }

    function renderDiscovery(edges) {
        const card = $("discoveryCard");
        if (!card) return;
        const list = $("discoveryList");
        if (!list) return;
        const shown = edges.filter((e) => e.attention_required).slice(0, 3);
        const useEdges = shown.length ? shown : edges.slice(0, 3);
        if (!useEdges.length) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        const mode = getDisc();
        const tone = TONE[getAlign()] || TONE.critical;
        const question = $("discoveryQuestion");
        if (question) {
            question.innerHTML = mode === "split"
                ? `The mirror surfaces tensions in <b>two ways</b> below — sometimes it only asks, sometimes it states the issue outright. For each, tell us if you had anticipated it.`
                : tone.lead;
        }
        let html = "";
        useEdges.forEach((edge, i) => {
            const style = discStyleFor(edge, i, mode);
            html += buildDiscoveryItem(edge, style, tone, i);
        });
        list.innerHTML = html;
        list.querySelectorAll(".disc-item").forEach((item, i) => {
            wireDiscoveryItem(item, useEdges[i], discStyleFor(useEdges[i], i, mode), tone);
        });
    }

    function setupDiscovery() { /* per-item wiring now happens in renderDiscovery */ }

    /* ------------------------------------------------------------------ *
     * Before / after coverage delta (after a replay)
     * ------------------------------------------------------------------ */
    function renderDelta(session) {
        const host = $("mmDelta");
        if (!host) return;
        const history = Array.isArray(session.replay_history) ? session.replay_history : [];
        if (!history.length) {
            host.hidden = true;
            return;
        }
        const last = history[history.length - 1];
        const sum = (last && last.summary) || {};
        host.hidden = false;
        host.innerHTML = `<div class="mm-delta-card surface"><strong>After your revision</strong>` +
            `<span>${Number(sum.changed_lens_count || 0)} lens coverage states improved</span>` +
            `<span>${Number(sum.resolved_edges || 0)} tensions resolved</span>` +
            `<span>${Number(sum.open_edges || 0)} tensions still open</span>` +
            `<small>The map above re-rendered from the revised plan — green nodes and cells are the gaps you closed.</small></div>`;
    }

    /* ------------------------------------------------------------------ *
     * Tab switching
     * ------------------------------------------------------------------ */
    function setupTabs() {
        const tabs = document.querySelectorAll("[data-mm-view]");
        tabs.forEach((btn) => {
            btn.addEventListener("click", () => {
                const view = btn.dataset.mmView;
                tabs.forEach((b) => b.classList.toggle("is-active", b === btn));
                document.querySelectorAll("[data-mm-panel]").forEach((p) => {
                    p.hidden = p.dataset.mmPanel !== view;
                });
            });
        });
    }

    /* ------------------------------------------------------------------ *
     * Boot
     * ------------------------------------------------------------------ */
    function boot() {
        setupTabs();
        setupDiscovery();
        if (window.SafeBarsMirror) {
            window.SafeBarsMirror.onStep = function (target) {
                if (target === 4) window.setTimeout(renderMultimodal, 40);
                else if (target === 5) window.setTimeout(renderRealizeBridge, 40);
            };
        }
    }

    /* ------------------------------------------------------------------ *
     * Bridge: carry the Step-4 self-discovery into the Step-5 fix
     * (realize -> fix loop). The user, not the AI, owns the change.
     * ------------------------------------------------------------------ */
    function renderRealizeBridge() {
        const host = $("realizeBridge");
        if (!host) return;
        const store = window.SafeBarsMirror;
        let sd = store && store.selfDiscovery;
        if (!sd || !sd.realized) {
            try {
                const id = (getSession() && getSession().id) || "anon";
                const raw = localStorage.getItem("safebarsDiscovery:" + id);
                if (raw) sd = JSON.parse(raw);
            } catch (e) { /* ignore */ }
        }
        if (!sd || !sd.realized) {
            host.hidden = true;
            return;
        }
        host.hidden = false;
        const text = $("realizeBridgeText");
        if (text) text.textContent = sd.realized;
        const title = $("realizeBridgeTitle");
        if (title) {
            title.textContent = sd.party
                ? "You realized: " + sd.party
                : "What you noticed in Step 4";
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
