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
    function renderDiscovery(edges) {
        const card = $("discoveryCard");
        if (!card) return;
        const edge = edges.find((e) => e.attention_required) || edges[0];
        if (!edge) {
            card.hidden = true;
            return;
        }
        card.hidden = false;
        const party = edge.affected_party || "an affected group";
        const consequence = edge.consequence || "";
        const question = $("discoveryQuestion");
        if (question) {
            question.innerHTML = `The mirror renders <b style="color:${COVERAGE_COLORS.Missing}">${escapeHtml(short(party, 40))}</b> ` +
                `in red — a group it infers your plan has not yet accounted for. ` +
                `<br><br>Did you anticipate that your design would affect this group?`;
        }
        const store = window.SafeBarsMirror;
        if (store) {
            store._discoveryEdge = { edge_id: edge.id, party, consequence };
        }
        // reset sub-controls
        ["discoveryOptions", "discoveryReveal", "discoveryRealize", "discoverySaved"].forEach((id) => {
            const el = $(id);
            if (el) el.hidden = true;
        });
        const opts = $("discoveryOptions");
        if (opts) opts.hidden = false;
        // clear prior radio + text
        document.querySelectorAll('input[name="disc"]').forEach((r) => (r.checked = false));
        const rt = $("realizeText");
        if (rt) rt.value = "";
    }

    function setupDiscovery() {
        const opts = $("discoveryOptions");
        if (opts) {
            opts.addEventListener("change", (ev) => {
                if (!ev.target || ev.target.name !== "disc") return;
                const reveal = $("discoveryReveal");
                const realize = $("discoveryRealize");
                const edge = window.SafeBarsMirror && window.SafeBarsMirror._discoveryEdge;
                if (reveal && edge) {
                    reveal.hidden = false;
                    reveal.innerHTML = `<div class="discovery-gap"><b>What the mirror found (it did not tell you — you had to look):</b><br><br>` +
                        `${escapeHtml(edge.consequence || "")}<br><br>` +
                        `<span class="discovery-note">Mechanism: the realization is yours. The mirror only rendered the gap; you connected it to your design.</span></div>`;
                }
                if (realize) realize.hidden = false;
                if (window.SafeBarsMirror) {
                    window.SafeBarsMirror.selfDiscovery = Object.assign(
                        window.SafeBarsMirror.selfDiscovery || {},
                        { anticipated: ev.target.value, party: edge && edge.party, consequence: edge && edge.consequence, edge_id: edge && edge.edge_id }
                    );
                }
            });
        }
        const save = $("saveDiscoveryBtn");
        if (save) {
            save.addEventListener("click", () => {
                const rt = $("realizeText");
                const text = rt ? rt.value.trim() : "";
                if (!text) {
                    rt && rt.focus();
                    return;
                }
                if (window.SafeBarsMirror) {
                    window.SafeBarsMirror.selfDiscovery = Object.assign(
                        window.SafeBarsMirror.selfDiscovery || {},
                        { realized: text, saved_at: new Date().toISOString() }
                    );
                }
                try {
                    const id = (getSession() && getSession().id) || "anon";
                    localStorage.setItem("safebarsDiscovery:" + id, JSON.stringify(window.SafeBarsMirror.selfDiscovery));
                } catch (e) { /* ignore */ }
                const saved = $("discoverySaved");
                if (saved) saved.hidden = false;
            });
        }
    }

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
            };
        }
    }

    if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", boot);
    } else {
        boot();
    }
})();
