(() => {
    "use strict";

    const API_ROOT = (document.body.dataset.apiRoot || "/api/safebars/mirror").replace(/\/$/, "");
    const STORAGE_KEY = "safebarsMirrorSessionId";
    const DRAFT_KEY = "safebarsMirrorUnsavedDraft";
    const SVG_NS = "http://www.w3.org/2000/svg";

    const COVERAGE_ORDER = ["missing", "claimed", "reasoned", "action-linked"];
    const COVERAGE_LABELS = {
        missing: "Missing",
        claimed: "Claimed",
        reasoned: "Reasoned",
        "action-linked": "Action-linked",
    };

    const RESOLUTION_TYPES = {
        revise_design: {
            label: "Revise the design",
            icon: "↺",
            help: "Change a feature, data flow, user journey, or deployment assumption.",
        },
        add_safeguard: {
            label: "Add a safeguard",
            icon: "＋",
            help: "Add human review, evaluation, fallback, monitoring, or a stopping rule.",
        },
        contest_with_evidence: {
            label: "Contest with evidence",
            icon: "≠",
            help: "Explain why this generated argument does not fit—and cite what supports you.",
        },
        consult_stakeholders: {
            label: "Consult real people",
            icon: "◎",
            help: "Leave the question open for affected people or an accountable expert.",
        },
    };

    const FALLBACK_LENSES = [
        {
            id: "lifecycle_integration",
            label: "Lifecycle integration",
            description: "Where and when unintended consequences will be examined across ideation, prototyping, deployment, and follow-up.",
            question: "At which design decisions can reflection still change the project—and who will revisit it later?",
            source_id: "do_2023",
            source_label: "Do et al. · CHI 2023",
        },
        {
            id: "benefit_harm_assumptions",
            label: "Benefit–harm assumptions",
            description: "The causal assumptions connecting the proposed innovation to intended benefit and possible harm.",
            question: "What must be true for the claimed benefit, and how could the same mechanism create harm?",
            source_id: "do_2023",
            source_label: "Do et al. · CHI 2023",
        },
        {
            id: "affected_groups",
            label: "Affected groups & uneven effects",
            description: "Direct users, non-users, excluded people, and groups who may carry different benefits, burdens, or risks.",
            question: "Who can be affected without choosing to use the app, and who is easiest to overlook?",
            source_id: "jobin_2019",
            source_label: "Jobin et al. · NMI 2019",
        },
        {
            id: "downstream_use",
            label: "Downstream use, misuse & scale",
            description: "How an app, model output, dataset, or research claim may be reused, repurposed, combined, or scaled.",
            question: "What changes if a different actor deploys this capability for a different goal or at greater scale?",
            source_id: "do_2023",
            source_label: "Do et al. · CHI 2023",
        },
        {
            id: "perspective_diversity",
            label: "Perspective diversity & participation",
            description: "Whose knowledge shaped the design and which claims require engagement with people rather than simulation.",
            question: "Which uncertainties can only affected people answer, and how will they influence a real design decision?",
            source_id: "bernstein_2021",
            source_label: "Bernstein et al. · PNAS 2021",
        },
        {
            id: "responsibility_oversight",
            label: "Responsibility & oversight",
            description: "Named responsibility for model outputs, consequential decisions, appeals, correction, and intervention.",
            question: "Who remains answerable when the AI is wrong, and what authority do they have to act?",
            source_id: "jobin_2019",
            source_label: "Jobin et al. · NMI 2019",
        },
        {
            id: "prior_cases",
            label: "Prior cases & analogues",
            description: "Evidence from similar systems, incidents, domains, or populations used to challenge novelty assumptions.",
            question: "What comparable system or failure case should change the design before a new study is run?",
            source_id: "do_2023",
            source_label: "Do et al. · CHI 2023",
        },
        {
            id: "mitigation_commitment",
            label: "Design-change & mitigation commitment",
            description: "Specific changes, safeguards, owners, tests, or stopping rules connected to identified consequences.",
            question: "What would you actually change if this concern were credible, and what evidence would be enough?",
            source_id: "bernstein_2021",
            source_label: "Bernstein et al. · PNAS 2021",
        },
        {
            id: "monitoring_learning",
            label: "Monitoring, reaction & learning",
            description: "How weak signals, unexpected outcomes, complaints, and design reversals will be noticed and acted on.",
            question: "What could reveal an emerging consequence, who reviews it, and when would the project pause?",
            source_id: "do_2023",
            source_label: "Do et al. · CHI 2023",
        },
    ];

    const FALLBACK_LITERATURE = [
        {
            id: "do_2023",
            title: "“That’s important, but…”: How Computer Science Researchers Anticipate Unintended Consequences of Their Research Innovations",
            citation: "Do, L. et al. (2023). CHI Conference on Human Factors in Computing Systems.",
            venue: "CHI 2023",
            type: "HCI paper",
            url: "https://doi.org/10.1145/3544548.3581347",
            informs: "Lifecycle reflection, motivation barriers, concrete cases, perspective diversity, and collective responsibility.",
            operationalisation: "Nine consequence lenses and prompts embedded before implementation.",
            limit: "The paper reports researcher practices; it does not provide a validated nine-item ethics scale.",
        },
        {
            id: "bernstein_2021",
            title: "Ethics and Society Review: Ethics reflection as a precondition to research funding",
            citation: "Bernstein, M. S. et al. (2021). Proceedings of the National Academy of Sciences.",
            venue: "PNAS",
            type: "Process framework",
            url: "https://doi.org/10.1073/pnas.2117261118",
            informs: "Early-stage reflection on societal risks and design changes while projects remain malleable.",
            operationalisation: "Tension review, mitigation commitments, and revision records.",
            limit: "It is a broader societal-review process, not an institutional approval decision.",
        },
        {
            id: "jobin_2019",
            title: "The global landscape of AI ethics guidelines",
            citation: "Jobin, A., Ienca, M., & Vayena, E. (2019). Nature Machine Intelligence.",
            venue: "Nature Machine Intelligence",
            type: "Journal synthesis",
            url: "https://doi.org/10.1038/s42256-019-0088-2",
            informs: "Transparency, justice, fairness, non-maleficence, responsibility, and privacy value categories.",
            operationalisation: "Affected-group, oversight, privacy, and accountability prompts.",
            limit: "Principle convergence does not by itself specify context-sensitive design action.",
        },
        {
            id: "priolo_2019",
            title: "Three decades of research on induced hypocrisy: A meta-analysis",
            citation: "Priolo, D. et al. (2019). Personality and Social Psychology Bulletin.",
            venue: "PSPB",
            type: "Behavioural evidence",
            url: "https://doi.org/10.1177/0146167219841621",
            informs: "Commitment–behaviour discrepancy as a prompt for self-directed change.",
            operationalisation: "User-authored value commitments are juxtaposed with concrete design evidence and consequences.",
            limit: "The interface must not shame, manipulate, or treat dissonance as proof of wrongdoing.",
        },
    ];

    const GUIDED_EXAMPLE = {
        title: "LLM feedback coach for student research ideas",
        plan: `We plan to build an LLM-enabled web app that helps computer-science students develop early research ideas. Students paste a project pitch and the app generates novelty feedback, methodological suggestions, and a “readiness” label. It can compare the pitch with papers retrieved from a university library index.

The app will be tested with undergraduate and master's students in project-design classes. Students can revise their pitch after reading the feedback. The research team will collect submitted pitches, generated feedback, revision histories, clicks, and a short usefulness survey. Instructors can view a dashboard showing readiness labels and common weaknesses across the class.

We expect the tool to help students who have limited access to individual supervision. The LLM will not assign grades, but instructors may use its dashboard when deciding who needs support. Study data will be stored by the research team for analysis. We will compare the app with a general-purpose LLM chat condition.`,
        commitments: [
            "Students should retain authorship of their research ideas and be able to contest consequential AI feedback.",
            "The app should broaden access to useful supervision without quietly increasing surveillance or unequal treatment.",
            "AI assistance should not shift academic responsibility away from a named instructor or researcher.",
        ],
        answers: {
            research_context: "Computer-science education in university project-design classes.",
            intended_change: "Help students turn an early research idea into a clearer, more feasible project proposal when individual supervision is limited.",
            direct_users: "Undergraduate and master’s students would use the app while preparing project pitches; instructors may later view class-level feedback.",
            ai_role: "An LLM would retrieve related papers, generate novelty and method feedback, and attach a readiness label. It would advise rather than grade.",
            data_materials: "Student project pitches, prompts, generated feedback, revision histories, clicks, and a short usefulness survey would be collected.",
            affected_others: "Students who do not use the tool, classmates compared through the dashboard, and instructors whose attention may be directed by readiness labels could still be affected.",
            value_commitment: "Students should retain authorship and be able to understand, reject, and contest consequential AI feedback.",
            stop_condition: "Readiness labels begin shaping grades or access to supervision, or some student groups are repeatedly misclassified without an effective appeal route.",
        },
    };

    const INTAKE_QUESTIONS = [
        {
            id: "research_context",
            label: "Research context",
            stage: "Getting oriented",
            prompt: "What area or real-world problem are you exploring?",
            hint: "A few words are enough. You can revise any answer later.",
            why: "The same app can create very different consequences in a classroom, clinic, workplace, public service, or home.",
            placeholder: "For example: supporting students who have limited access to project supervision…",
            min: 8,
            options: [
                ["Education", "Education or learning"],
                ["Health", "Health or wellbeing"],
                ["Work", "Work or employment"],
                ["Public services", "Public services"],
                ["Community", "Community life"],
            ],
        },
        {
            id: "intended_change",
            label: "Intended benefit",
            stage: "Clarifying the hope",
            prompt: "If this became an app, what would you hope it helps someone do?",
            hint: "Describe the change you want—not the technology yet.",
            why: "Starting with the intended benefit gives the later mirror a concrete claim to test instead of assuming that innovation is automatically beneficial.",
            placeholder: "I hope it helps people…",
            min: 12,
            options: [
                ["Make a decision", "Help someone make a decision"],
                ["Receive feedback", "Give timely, useful feedback"],
                ["Create something", "Support creative or research work"],
                ["Notice a problem", "Detect a problem earlier"],
            ],
        },
        {
            id: "direct_users",
            label: "Direct users",
            stage: "Placing the encounter",
            prompt: "Who would choose to use it, and in what moment or setting?",
            hint: "Tell me about a concrete encounter rather than a broad population label.",
            why: "Ethical tensions often appear in the situation of use: who has power, what is at stake, and whether use is genuinely voluntary.",
            placeholder: "A person would open the app when…",
            min: 14,
            options: [
                ["Student · preparing work", "Students would choose to use it while preparing an assignment, project, or application."],
                ["Person · before a decision", "A person would open it privately before making a decision or asking a professional for help."],
                ["Worker · during a task", "Workers would choose to use it during a specific task while remaining responsible for the decision."],
                ["Service user · seeking support", "Members of the public would use it while voluntarily applying for or accessing a service."],
                ["Professional · reviewing a case", "Professionals would use it while reviewing a real case, with a named human retaining authority."],
            ],
        },
        {
            id: "ai_role",
            label: "AI role",
            stage: "Locating AI authority",
            prompt: "What would the AI actually do—and what, if anything, could people rely on it to decide?",
            hint: "Choose a starter or describe the role in your own words.",
            why: "Generating text, ranking people, monitoring behavior, and making a consequential recommendation create different oversight and contestability needs.",
            placeholder: "The AI would… A human would remain responsible for…",
            min: 14,
            optionMode: "append",
            options: [
                ["Generate", "Generate content"],
                ["Recommend", "Recommend an action"],
                ["Classify", "Classify or rank"],
                ["Monitor", "Monitor behavior"],
                ["Automate", "Automate a task"],
            ],
        },
        {
            id: "data_materials",
            label: "Data and materials",
            stage: "Following the data",
            prompt: "What would the app need to see, collect, remember, or infer?",
            hint: "Include prompts, uploads, logs, model outputs, and any sensitive or third-party information.",
            why: "A design can change once data necessity, retention, inference, and access are made visible—not after an approval form is drafted.",
            placeholder: "The app would receive… It would retain…",
            min: 12,
            optionMode: "append",
            options: [
                ["Text", "Text or documents"],
                ["Interaction logs", "Interaction logs"],
                ["Images or audio", "Images, audio, or video"],
                ["Profiles", "Profile information"],
                ["Biometrics", "Biometric or inferred traits"],
            ],
        },
        {
            id: "sensitive_data_justification",
            label: "Sensitive-data necessity",
            stage: "Pausing at a sensitive choice",
            prompt: "You mentioned a sensitive or inferred trait. Why is it necessary—and could the app work without estimating it?",
            hint: "Please separate what a person volunteers from what a camera, model, or dataset would infer.",
            why: "Age, race or ethnicity, disability, gender, family or marital status, and biometric signals can expose people to misclassification and discrimination. Relevance and necessity must be established before collection or inference.",
            placeholder: "This information is needed because… A less intrusive alternative would be…",
            min: 18,
            conditional: "sensitive_data",
            options: [
                ["Self-description", "Ask for optional self-description instead of inference"],
                ["Avoid it", "Remove the trait because it is not necessary"],
                ["Coarse alternative", "Use a less sensitive contextual measure"],
                ["Still necessary", "Retain it with a specific scientific justification and safeguards"],
            ],
        },
        {
            id: "affected_others",
            label: "Indirect effects",
            stage: "Widening the circle",
            prompt: "Now look one step beyond the user: who could be affected without ever opening the app?",
            hint: "Think about people represented in data, compared by outputs, excluded from access, or acted on by another person.",
            why: "Do et al. and related HCI work show why unintended consequences cannot be anticipated only from the intended user’s point of view.",
            placeholder: "Someone who never uses the app could still be affected when…",
            min: 14,
            options: [
                ["People in the data", "People represented in the data"],
                ["Compared peers", "People compared with users"],
                ["Family or community", "Family or community members"],
                ["Frontline staff", "Staff asked to act on outputs"],
            ],
        },
        {
            id: "value_commitment",
            label: "Your commitment",
            stage: "Declaring a standard",
            prompt: "What promise would you want to make to the people this app may affect?",
            hint: "Use your own words. Later, the mirror will compare this promise with concrete design choices.",
            why: "The commitment–design contrast is a transparent cognitive-dissonance scaffold: it invites self-directed revision without shaming or declaring the plan unethical.",
            placeholder: "People affected by this app should be able to…",
            min: 18,
            options: [
                ["Contest", "Understand and contest important outputs"],
                ["Remain in control", "Keep meaningful choice and control"],
                ["Minimise data", "Share only data that is truly necessary"],
                ["Fair access", "Receive benefits without unequal burdens"],
            ],
        },
        {
            id: "stop_condition",
            label: "Redesign threshold",
            stage: "Making the value actionable",
            prompt: "Imagine the app becomes widely used. What outcome would make you pause or redesign it?",
            hint: "A concrete signal is more useful than saying “if harm occurs.”",
            why: "A value becomes actionable when it is connected to a visible trigger, a decision owner, and a willingness to change the research design.",
            placeholder: "I would pause or redesign the project if…",
            min: 18,
            options: [
                ["Unequal errors", "Errors repeatedly burden one group"],
                ["Hidden influence", "People rely on outputs without understanding them"],
                ["No appeal", "A consequential output cannot be challenged"],
                ["Scope drift", "The app is reused beyond the tested setting"],
            ],
        },
    ];

    const SENSITIVE_DATA_PATTERN = /\b(age|race|racial|ethnic|ethnicity|marital|marriage|spouse|partner|gender|sex|sexuality|disability|disabled|health|medical|biometric|face|facial|camera|voiceprint|religion|nationality|migration|income)\b/i;

    const state = {
        activeStep: 1,
        config: {},
        literature: [...FALLBACK_LITERATURE],
        session: null,
        lensFilter: "all",
        roleFilter: "all",
        scenarioSort: "tension",
        selectedScenarioId: null,
        selectedEdgeId: null,
        selectedTensionId: null,
        resolutionDrafts: {},
        editorView: "edit",
        mapMode: "all",
        graphScale: 1,
        ledgerFilter: "all",
        lastConnectionOk: false,
        loadingTimer: null,
        dirty: false,
        restored: false,
        intakeIndex: 0,
        intakeAnswers: {},
        intakeComplete: false,
    };

    const dom = {};

    function cacheDom() {
        [
            "workspace", "apiStatus", "sessionLabel", "connectionBanner", "retryConnectionBtn", "resumeBtn",
            "loadExampleBtn", "methodTopBtn", "showMethodBtn", "startOverBtn", "newMirrorBtn",
            "planForm", "projectTitle", "researchPlan", "planWordCount", "planSignals", "signalRow",
            "commitmentList", "commitmentCount", "addCommitmentBtn", "planValidation", "buildMirrorBtn",
            "intakeQuestionCount", "intakeStageLabel", "intakeProgressFill", "intakeReflection",
            "intakePrompt", "intakeHint", "intakeWhyBtn", "intakeWhy", "intakeOptions",
            "intakeTextInput", "intakeInputGuide", "intakeCharCount", "intakeBackBtn",
            "intakeSkipBtn", "intakeNextBtn", "intakeAnsweredCount", "intakeTrail",
            "intakeComplete", "intakeOptionalContext", "intakeBuildActions",
            "reanalyzeBtn", "coverageHeadline", "coverageTrack", "coverageLabels", "lensAllCount",
            "lensGrid", "lensEmpty", "literatureCount", "openLiteratureBtn", "roleFilter",
            "scenarioSort", "scenarioList", "scenarioStage", "boundaryDetailsBtn", "dissonanceGraph",
            "graphViewport", "graphWrap", "graphTooltip", "graphEmpty", "pathInspector", "zoomOutBtn",
            "fitGraphBtn", "zoomInBtn", "tensionCount", "tensionList", "resolutionPanel",
            "revisedPlan", "originalPlanView", "planDiff", "revisionStats", "restoreOriginalBtn",
            "revisionSaveState", "saveRevisionBtn", "replayBtn", "metricChanges", "metricAddressed",
            "metricOpen", "metricActionLinked", "ledgerTimestamp", "ledgerList", "ledgerEmpty",
            "downloadBundleBtn", "printLedgerBtn", "literatureDialog", "literatureList", "methodDialog",
            "boundaryDialog", "loadingLayer", "loadingEyebrow", "loadingTitle", "loadingDetail",
            "loadingSteps", "toastRegion",
        ].forEach((id) => {
            dom[id] = document.getElementById(id);
        });
        dom.stepNav = document.getElementById("stepNav");
        dom.stepPanels = [...document.querySelectorAll("[data-step-panel]")];
        dom.stepNavItems = [...document.querySelectorAll("[data-step-target]")];
    }

    function asArray(value) {
        if (Array.isArray(value)) return value;
        if (!value || typeof value !== "object") return [];
        return Object.entries(value).map(([id, item]) => (
            typeof item === "object" && item !== null ? { id, ...item } : { id, value: item }
        ));
    }

    function firstValue(...values) {
        return values.find((value) => value !== undefined && value !== null && value !== "");
    }

    function clamp(value, min, max) {
        const number = Number(value);
        if (!Number.isFinite(number)) return min;
        return Math.max(min, Math.min(max, number));
    }

    function slug(value, fallback = "item") {
        const normal = String(value || "")
            .toLowerCase()
            .replace(/[^a-z0-9]+/g, "-")
            .replace(/^-|-$/g, "");
        return normal || fallback;
    }

    function escapeHtml(value) {
        return String(value ?? "")
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }

    function escapeAttr(value) {
        return escapeHtml(value).replace(/`/g, "&#096;");
    }

    function shortText(value, max = 150) {
        const text = String(value || "").replace(/\s+/g, " ").trim();
        if (text.length <= max) return text;
        return `${text.slice(0, Math.max(0, max - 1)).trim()}…`;
    }

    function titleCase(value) {
        return String(value || "")
            .replace(/[_-]+/g, " ")
            .replace(/\b\w/g, (letter) => letter.toUpperCase());
    }

    function normaliseCoverage(value) {
        const raw = String(value || "missing").toLowerCase().trim().replace(/[_\s]+/g, "-");
        if (["action-linked", "actionable", "implemented", "linked", "action"].includes(raw)) return "action-linked";
        if (["reasoned", "explained", "supported", "evidence"].includes(raw)) return "reasoned";
        if (["claimed", "mentioned", "partial", "present"].includes(raw)) return "claimed";
        return "missing";
    }

    function normaliseLens(item, index) {
        const fallback = FALLBACK_LENSES[index] || {};
        const source = firstValue(item.source, item.literature, item.citation, {});
        const evidenceRaw = firstValue(
            item.evidence,
            item.evidence_excerpt,
            item.plan_excerpt,
            item.submitted_evidence,
            item.matched_passage,
            ""
        );
        const evidenceItems = asArray(evidenceRaw);
        const evidence = evidenceItems.length
            ? evidenceItems.map((entry) => firstValue(entry.quote, entry.text, entry.excerpt, "")).filter(Boolean).join(" … ")
            : evidenceRaw;
        const sourceIds = asArray(firstValue(item.source_ids, item.literature_ids, [])).map((entry) => (
            typeof entry === "object" ? firstValue(entry.id, entry.key, entry.url, "") : String(entry)
        )).filter(Boolean);
        return {
            id: firstValue(item.id, item.key, item.dimension_id, fallback.id, `lens_${index + 1}`),
            label: firstValue(item.label, item.name, item.title, item.dimension, fallback.label, `Lens ${index + 1}`),
            description: firstValue(item.description, item.operational_definition, item.definition, fallback.description, ""),
            question: firstValue(item.question, item.prompt, item.reflection_prompt, fallback.question, ""),
            status: normaliseCoverage(firstValue(item.status, item.state, item.state_id, item.coverage, item.level, item.evidence_state)),
            evidence: typeof evidence === "object"
                ? firstValue(evidence.text, evidence.excerpt, evidence.quote, "")
                : evidence,
            explanation: firstValue(item.explanation, item.assessment, item.reasoning, item.rationale, item.note, ""),
            next_action: firstValue(item.next_action, item.improvement, item.missing_evidence, item.suggestion, ""),
            boundary: firstValue(item.boundary, item.interpretation_boundary, ""),
            source_ids: sourceIds,
            source_id: firstValue(
                item.source_id,
                sourceIds[0],
                typeof source === "object" ? firstValue(source.id, source.key) : "",
                fallback.source_id,
                ""
            ),
            source_label: firstValue(
                item.source_label,
                typeof source === "object" ? firstValue(source.short_label, source.label, source.citation) : source,
                fallback.source_label,
                "Literature source"
            ),
        };
    }

    function normaliseScenario(item, index) {
        const roleValue = firstValue(item.role_label, item.agent_label, item.role, item.affected_role, item.perspective, item.persona, item.actor, "Affected person");
        const role = typeof roleValue === "object"
            ? firstValue(roleValue.label, roleValue.name, roleValue.role, "Affected person")
            : roleValue;
        const rawFrames = asArray(firstValue(
            item.frames,
            item.visualization?.frames,
            item.storyboard,
            item.timeline,
            item.events,
            []
        ));
        const frames = rawFrames.slice(0, 4).map((frame, frameIndex) => ({
            title: firstValue(frame.title, frame.label, frame.stage, `Moment ${frameIndex + 1}`),
            text: firstValue(frame.text, frame.description, frame.event, frame.outcome, ""),
            visual_type: firstValue(frame.visual_type, frame.type, ["app", "people", "data"][frameIndex % 3]),
        }));
        const planEvidenceRaw = firstValue(item.plan_evidence, item.evidence, item.plan_excerpt, item.trigger, "");
        const planEvidence = typeof planEvidenceRaw === "object"
            ? firstValue(planEvidenceRaw.quote, planEvidenceRaw.text, planEvidenceRaw.excerpt, "")
            : planEvidenceRaw;
        const sourceIds = asArray(firstValue(item.source_ids, item.literature_ids, item.sources, [])).map((source) => (
            typeof source === "object" ? firstValue(source.id, source.key, source.url, source.label) : source
        )).filter(Boolean);
        return {
            id: firstValue(item.id, item.scenario_id, item.key, `scenario_${index + 1}`),
            role: String(role),
            role_type: firstValue(item.role_id, item.agent_id, item.role_type, item.actor_type, slug(role)),
            title: firstValue(item.title, item.name, typeof item.scenario === "string" ? item.scenario : "", shortText(item.consequence, 85), `Possible future ${index + 1}`),
            summary: firstValue(item.summary, item.situation, item.description, item.consequence, item.outcome, ""),
            consequence: firstValue(item.consequence, item.outcome, item.harm, item.summary, ""),
            plan_evidence: planEvidence,
            plan_passage_id: typeof planEvidenceRaw === "object" ? firstValue(planEvidenceRaw.passage_id, planEvidenceRaw.id, "") : "",
            literature_evidence: firstValue(item.literature_evidence, item.case_evidence, item.analogue, item.source_note, sourceIds.join(", "), ""),
            inference: firstValue(item.first_person_probe, item.inference, item.assumption_challenged, item.assumption, item.uncertainty_note, "This scenario is a model-generated hypothesis requiring verification."),
            assumption_challenged: firstValue(item.assumption_challenged, item.assumption, ""),
            revision_lever: firstValue(item.revision_lever, item.intervention, item.suggested_revision, ""),
            question: firstValue(item.question_for_real_people, item.question, item.handoff_question, item.follow_up, "What would a real affected person need to confirm or challenge here?"),
            tension: clamp(firstValue(item.tension, item.tension_level, item.severity, item.priority, 2), 0, 4),
            uncertainty: clamp(firstValue(item.uncertainty, item.uncertainty_level, item.confidence ? 1 - Number(item.confidence) : 0.5), 0, 1),
            literature_ids: sourceIds,
            synthetic: item.synthetic !== false,
            boundary_notice: firstValue(item.boundary_notice, ""),
            generation_mode: firstValue(item.generation_mode, item.model_enrichment ? "llm_batched_bounded_role_probe" : "deterministic_bounded_fallback"),
            model_enrichment: firstValue(item.model_enrichment, {}),
            frames,
        };
    }

    function normaliseEdge(item, index, session) {
        const scenarioValue = firstValue(item.scenario, {});
        const scenarioId = firstValue(
            item.scenario_id,
            typeof scenarioValue === "object" ? firstValue(scenarioValue.id, scenarioValue.scenario_id) : scenarioValue,
            item.source_scenario_id,
            ""
        );
        const relatedScenario = session.scenarios.find((scenario) => scenario.id === scenarioId);
        const commitmentValue = firstValue(
            item.commitment,
            item.value_commitment,
            item.promise,
            session.value_commitments[index % Math.max(session.value_commitments.length, 1)],
            "The project should avoid preventable harm."
        );
        const partyValue = firstValue(
            item.affected_party,
            item.party,
            item.role,
            relatedScenario?.role,
            "Affected person"
        );
        const designChoice = firstValue(item.design_choice, item.plan_evidence, item.evidence, {});
        const designEvidence = typeof designChoice === "object"
            ? firstValue(designChoice.quote, designChoice.text, designChoice.excerpt, "")
            : designChoice;
        const provenance = firstValue(item.provenance, {});
        const literatureIds = asArray(firstValue(
            item.literature_ids,
            item.sources,
            typeof provenance === "object" ? provenance.literature_ids : [],
            relatedScenario?.literature_ids,
            []
        )).map((source) => (
            typeof source === "object" ? firstValue(source.id, source.key, source.url, source.label) : source
        )).filter(Boolean);
        return {
            id: firstValue(item.id, item.edge_id, item.path_id, `tension_${index + 1}`),
            commitment: typeof commitmentValue === "object"
                ? firstValue(commitmentValue.text, commitmentValue.label, commitmentValue.value, "")
                : commitmentValue,
            evidence: firstValue(
                designEvidence,
                typeof item.design_decision === "object"
                    ? firstValue(item.design_decision.quote, item.design_decision.text, item.design_decision.excerpt)
                    : item.design_decision,
                relatedScenario?.plan_evidence,
                "No matching plan passage was identified."
            ),
            consequence: firstValue(
                item.consequence,
                item.possible_consequence,
                item.outcome,
                relatedScenario?.consequence,
                "A plausible downstream consequence requires examination."
            ),
            affected_party: typeof partyValue === "object"
                ? firstValue(partyValue.label, partyValue.name, partyValue.role, "Affected person")
                : partyValue,
            relation: String(firstValue(item.relation, item.type, item.edge_type, "conflict")).toLowerCase(),
            tension: clamp(firstValue(item.tension_level, item.strength, item.severity, relatedScenario?.tension, 3), 0, 4),
            rationale: firstValue(
                item.rationale,
                item.argument,
                item.explanation,
                item.dissonance,
                typeof item.tension === "string" ? item.tension : "",
                ""
            ),
            scenario_id: scenarioId || relatedScenario?.id || "",
            literature_ids: literatureIds,
            suggested_revision: firstValue(item.suggested_revision, item.revision_prompt, item.possible_change, relatedScenario?.revision_lever, ""),
            uncertainty: clamp(firstValue(item.uncertainty, relatedScenario?.uncertainty, 0.5), 0, 1),
            status: firstValue(item.status, "open"),
            status_reason: firstValue(item.status_reason, ""),
            decision: firstValue(item.decision, null),
        };
    }

    function normaliseLedger(item, index) {
        const resolutionType = firstValue(item.resolution_type, item.choice, item.response_type, "");
        const statusRaw = String(firstValue(item.status, item.outcome_status, "")).toLowerCase();
        let status = statusRaw;
        if (!["changed", "contested", "open"].includes(status)) {
            if (resolutionType === "contest_with_evidence") status = "contested";
            else if (resolutionType === "consult_stakeholders") status = "open";
            else if (resolutionType) status = "changed";
            else status = "open";
        }
        return {
            id: firstValue(item.id, item.ledger_id, item.edge_id, `ledger_${index + 1}`),
            edge_id: firstValue(item.edge_id, item.tension_id, item.path_id, ""),
            title: firstValue(item.title, item.tension, item.consequence, `Revision record ${index + 1}`),
            role: firstValue(item.role, item.affected_party, ""),
            before: firstValue(item.before, item.original, item.original_evidence, item.plan_before, ""),
            after: firstValue(item.after, item.revised, item.revised_evidence, item.plan_after, ""),
            response: firstValue(item.response, item.rationale, item.researcher_response, ""),
            evidence: firstValue(item.evidence, item.follow_up, item.verification, ""),
            resolution_type: resolutionType,
            status,
            replay_outcome: firstValue(item.replay_outcome, item.outcome, item.result, ""),
            updated_at: firstValue(item.updated_at, item.created_at, ""),
        };
    }

    function unwrapSession(payload) {
        if (!payload || typeof payload !== "object") return {};
        return firstValue(payload.session, payload.data?.session, payload.data, payload);
    }

    function normaliseSession(raw, previous = null) {
        const source = raw && typeof raw === "object" ? raw : {};
        const prior = previous || {};
        const commitmentsRaw = firstValue(source.value_commitments, source.commitments, prior.value_commitments, []);
        const valueCommitments = asArray(commitmentsRaw).map((item) => (
            typeof item === "object" ? firstValue(item.text, item.value, item.label, "") : String(item)
        )).filter(Boolean);

        const session = {
            ...prior,
            ...source,
            id: firstValue(source.id, source.session_id, prior.id, ""),
            title: firstValue(source.title, source.project_title, prior.title, "Untitled Ethical Mirror"),
            original_research_plan: firstValue(
                source.original_research_plan,
                prior.original_research_plan,
                source.research_plan,
                source.plan,
                prior.research_plan,
                ""
            ),
            research_plan: firstValue(source.research_plan, source.plan, prior.research_plan, ""),
            revised_plan: firstValue(
                source.revised_plan,
                source.revisions?.revised_plan,
                prior.revised_plan,
                source.research_plan,
                prior.research_plan,
                ""
            ),
            value_commitments: valueCommitments,
            intake_answers: firstValue(source.intake_answers, prior.intake_answers, {}),
            boundary_notice: firstValue(source.boundary_notice, prior.boundary_notice, ""),
            created_at: firstValue(source.created_at, prior.created_at, ""),
            updated_at: firstValue(source.updated_at, source.replayed_at, prior.updated_at, ""),
            analyzed_at: firstValue(source.analyzed_at, source.analysis_completed_at, prior.analyzed_at, ""),
            replayed_at: firstValue(source.replayed_at, source.replay_completed_at, prior.replayed_at, ""),
        };

        const rawLenses = firstValue(source.lenses, source.dimensions, source.lens_assessments, prior.lenses, []);
        const lensArray = asArray(rawLenses);
        const configLenses = asArray(firstValue(state.config.lenses, state.config.dimensions, []));
        const baseLenses = lensArray.length ? lensArray : (configLenses.length ? configLenses : []);
        session.lenses = baseLenses.map(normaliseLens);

        const rawScenarios = firstValue(source.scenarios, source.role_scenarios, source.scenario_cards, prior.scenarios, []);
        session.scenarios = asArray(rawScenarios).map(normaliseScenario);

        const rawEdges = firstValue(
            source.dissonance_edges,
            source.tensions,
            source.dissonance_paths,
            source.edges,
            prior.dissonance_edges,
            []
        );
        session.dissonance_edges = asArray(rawEdges).map((edge, index) => normaliseEdge(edge, index, session));

        if (!session.dissonance_edges.length && session.scenarios.length) {
            session.dissonance_edges = session.scenarios.map((scenario, index) => normaliseEdge({
                id: `tension_${index + 1}`,
                scenario_id: scenario.id,
                commitment: valueCommitments[index % Math.max(valueCommitments.length, 1)],
                evidence: scenario.plan_evidence,
                consequence: scenario.consequence,
                affected_party: scenario.role,
                tension: scenario.tension,
                literature_ids: scenario.literature_ids,
            }, index, session));
        }

        const rawRevisions = firstValue(source.revisions, prior.revisions, []);
        session.revisions = Array.isArray(rawRevisions)
            ? rawRevisions
            : asArray(firstValue(rawRevisions.items, rawRevisions.resolutions, rawRevisions, []));
        const latestRevision = [...session.revisions].reverse().find((revision) => (
            revision && typeof revision === "object" && revision.revised_plan
        ));
        if (!source.revised_plan && latestRevision?.revised_plan) {
            session.revised_plan = latestRevision.revised_plan;
        } else if (!session.revised_plan) {
            session.revised_plan = session.research_plan;
        }

        const rawLedger = firstValue(source.ledger, source.change_ledger, source.before_after_ledger, prior.ledger, []);
        const ledgerItems = asArray(rawLedger);
        session.audit_events = ledgerItems.filter((item) => item.event_type || item.details);
        session.ledger = ledgerItems
            .filter((item) => (
                item.before !== undefined
                || item.after !== undefined
                || item.edge_id
                || item.resolution_type
            ))
            .map(normaliseLedger);
        return session;
    }

    async function api(path, options = {}) {
        const request = {
            method: options.method || "GET",
            headers: {
                Accept: "application/json",
                ...(options.body !== undefined ? { "Content-Type": "application/json" } : {}),
                ...(options.headers || {}),
            },
            credentials: "same-origin",
        };
        if (options.body !== undefined) {
            request.body = typeof options.body === "string" ? options.body : JSON.stringify(options.body);
        }
        let response;
        try {
            response = await fetch(`${API_ROOT}${path}`, request);
        } catch (error) {
            setConnection(false);
            const networkError = new Error("SafeBARS could not reach the analysis service.");
            networkError.cause = error;
            throw networkError;
        }
        let payload = null;
        const contentType = response.headers.get("content-type") || "";
        try {
            payload = contentType.includes("application/json")
                ? await response.json()
                : { message: await response.text() };
        } catch {
            payload = {};
        }
        if (!response.ok || payload?.success === false) {
            const message = firstValue(payload?.error, payload?.message, `Request failed (${response.status}).`);
            const error = new Error(typeof message === "object" ? firstValue(message.message, message.detail, "Request failed.") : message);
            error.status = response.status;
            error.payload = payload;
            if (response.status >= 500) setConnection(false);
            throw error;
        }
        setConnection(true);
        return payload || {};
    }

    function setConnection(online) {
        state.lastConnectionOk = Boolean(online);
        dom.apiStatus.classList.toggle("is-online", online);
        dom.apiStatus.classList.toggle("is-offline", !online);
        dom.apiStatus.querySelector("span").textContent = online ? "Service ready" : "Service unavailable";
        dom.connectionBanner.hidden = online;
    }

    async function loadConfiguration() {
        try {
            const [configResult, literatureResult] = await Promise.allSettled([
                api("/config"),
                api("/literature"),
            ]);
            if (configResult.status === "fulfilled") {
                state.config = firstValue(configResult.value.config, configResult.value.data, configResult.value, {});
            }
            if (literatureResult.status === "fulfilled") {
                const sources = asArray(firstValue(
                    literatureResult.value.literature,
                    literatureResult.value.sources,
                    literatureResult.value.data,
                    []
                ));
                if (sources.length) state.literature = sources.map(normaliseLiterature);
            }
            if (configResult.status === "rejected" && literatureResult.status === "rejected") {
                setConnection(false);
            }
        } catch {
            setConnection(false);
        }
        renderLiterature();
        dom.literatureCount.textContent = String(state.literature.length);
    }

    function normaliseLiterature(item, index) {
        const fallback = FALLBACK_LITERATURE[index] || {};
        const authors = firstValue(item.authors, "");
        const year = firstValue(item.year, "");
        return {
            id: firstValue(item.id, item.key, item.source_id, fallback.id, `source_${index + 1}`),
            title: firstValue(item.title, item.name, fallback.title, `Grounding source ${index + 1}`),
            citation: firstValue(
                item.citation,
                item.reference,
                authors ? `${authors}${year ? ` (${year})` : ""}` : "",
                fallback.citation,
                ""
            ),
            venue: firstValue(item.venue, item.journal, item.conference, fallback.venue, ""),
            type: firstValue(item.type, item.source_type, item.publication_type, fallback.type, "Literature source"),
            url: firstValue(item.url, item.doi_url, item.doi ? `https://doi.org/${item.doi}` : "", fallback.url, ""),
            informs: firstValue(item.informs, item.design_use, item.relevance, fallback.informs, ""),
            operationalisation: firstValue(item.operationalisation, item.implementation, item.app_use, fallback.operationalisation, ""),
            limit: firstValue(item.limit, item.limitation, item.boundary, fallback.limit, ""),
        };
    }

    function renderLiterature() {
        dom.literatureList.innerHTML = state.literature.map((source) => `
            <article class="literature-card" id="source-${escapeAttr(source.id)}">
                <div class="literature-card-top">
                    <span class="source-type">${escapeHtml(source.type)}</span>
                    ${source.url ? `<a href="${escapeAttr(source.url)}" target="_blank" rel="noopener noreferrer">Open source ↗</a>` : ""}
                </div>
                <h3>${escapeHtml(source.title)}</h3>
                <p class="citation">${escapeHtml(source.citation)}${source.venue ? ` · ${escapeHtml(source.venue)}` : ""}</p>
                <dl>
                    <dt>Informs</dt><dd>${escapeHtml(source.informs || "Grounding for a reflection prompt.")}</dd>
                    <dt>In the app</dt><dd>${escapeHtml(source.operationalisation || "Mapped to a visible decision point.")}</dd>
                    <dt>Limit</dt><dd>${escapeHtml(source.limit || "The source does not validate a generated claim about this project.")}</dd>
                </dl>
            </article>
        `).join("");
    }

    function intakeAnswer(id) {
        return String(state.intakeAnswers[id] || "").trim();
    }

    function activeIntakeQuestions() {
        const dataAnswer = intakeAnswer("data_materials");
        const needsSensitiveFollowUp = SENSITIVE_DATA_PATTERN.test(dataAnswer);
        return INTAKE_QUESTIONS.filter((question) => (
            !question.conditional
            || (question.conditional === "sensitive_data" && needsSensitiveFollowUp)
        ));
    }

    function intakeIsComplete() {
        return activeIntakeQuestions().every((question) => (
            intakeAnswer(question.id).length >= question.min
        ));
    }

    function intakeReflection(question) {
        const heard = (id, limit = 64) => {
            const answer = intakeAnswer(id);
            return answer ? `“${shortText(answer, limit)}”` : "";
        };
        const reflections = {
            research_context: "Hi—there is no form to complete all at once. We’ll take this slowly.",
            intended_change: `I’ll keep ${heard("research_context")} as our setting. Now let’s name the benefit you are hoping for.`,
            direct_users: `So the hoped-for change is ${heard("intended_change")}. Let’s place it in one real encounter.`,
            ai_role: `I can picture ${heard("direct_users")}. Now let’s separate what that person wants from what the AI may decide.`,
            data_materials: `The AI role is becoming concrete: ${heard("ai_role")}. Let’s follow the information that makes it possible.`,
            sensitive_data_justification: "I noticed a sensitive or inferred trait in that data flow. This choice deserves a short pause before we move on.",
            affected_others: "We have the intended journey and data flow. Now let’s widen the circle beyond people who choose the app.",
            value_commitment: `You identified an indirect effect: ${heard("affected_others")}. I want the standard for it to come from you.`,
            stop_condition: `You have made this promise: ${heard("value_commitment")}. One final step makes it actionable.`,
        };
        return reflections[question?.id] || reflections.research_context;
    }

    function renderIntakeTrail() {
        const questions = activeIntakeQuestions();
        const answered = questions.filter((question) => intakeAnswer(question.id)).length;
        dom.intakeAnsweredCount.textContent = `${answered} / ${questions.length}`;
        dom.intakeTrail.innerHTML = questions.map((question, index) => {
            const answer = intakeAnswer(question.id);
            const current = !state.intakeComplete && index === state.intakeIndex;
            return `
                <button class="intake-trail-item ${answer ? "is-answered" : ""} ${current ? "is-current" : ""}"
                        type="button" data-intake-edit="${index}" ${answer || index <= answered ? "" : "disabled"}>
                    <span class="trail-index">${answer ? "✓" : String(index + 1).padStart(2, "0")}</span>
                    <span class="trail-copy">
                        <small>${escapeHtml(question.label)}</small>
                        <strong>${escapeHtml(answer ? shortText(answer, 72) : (current ? "Answering now…" : "Not reached yet"))}</strong>
                    </span>
                    <span class="trail-edit">${answer ? "Edit" : ""}</span>
                </button>
            `;
        }).join("");
        dom.intakeTrail.querySelectorAll("[data-intake-edit]").forEach((button) => {
            button.addEventListener("click", () => editIntakeAnswer(Number(button.dataset.intakeEdit)));
        });
    }

    function renderIntake() {
        const completed = state.intakeComplete && intakeIsComplete();
        state.intakeComplete = completed;
        renderIntakeTrail();
        dom.intakeComplete.hidden = !completed;
        dom.buildMirrorBtn.hidden = !completed;
        dom.intakeBuildActions.hidden = !completed && !dom.planValidation.textContent.trim();
        dom.intakeTextInput.closest(".intake-conversation")?.classList.toggle("is-complete", completed);
        dom.intakeTextInput.closest(".intake-answer").hidden = completed;
        dom.intakeNextBtn.closest(".intake-controls").hidden = completed;

        if (completed) {
            dom.intakeQuestionCount.textContent = "Conversation complete";
            dom.intakeStageLabel.textContent = "Ready to mirror";
            dom.intakeProgressFill.style.width = "100%";
            dom.intakeReflection.textContent = "You began with the intended benefit and then widened the view to authority, data, indirect effects, and a redesign threshold.";
            dom.intakePrompt.textContent = "Your first research plan is ready.";
            dom.intakeHint.textContent = "Review any answer in the trail, or build the Ethical Mirror to test your commitments against possible consequences.";
            dom.intakeWhyBtn.hidden = true;
            dom.intakeWhy.hidden = true;
            syncIntakePayload();
            return;
        }

        const questions = activeIntakeQuestions();
        const question = questions[state.intakeIndex] || questions[0];
        const saved = intakeAnswer(question.id);
        dom.intakeQuestionCount.textContent = `Question ${state.intakeIndex + 1} of ${questions.length}`;
        dom.intakeStageLabel.textContent = question.stage;
        dom.intakeProgressFill.style.width = `${((state.intakeIndex + 1) / questions.length) * 100}%`;
        dom.intakeReflection.textContent = intakeReflection(question);
        dom.intakePrompt.textContent = question.prompt;
        dom.intakeHint.textContent = question.hint;
        dom.intakeWhy.textContent = question.why;
        dom.intakeWhy.hidden = true;
        dom.intakeWhyBtn.hidden = false;
        dom.intakeWhyBtn.setAttribute("aria-expanded", "false");
        dom.intakeTextInput.value = saved;
        dom.intakeTextInput.placeholder = question.placeholder;
        dom.intakeCharCount.textContent = String(saved.length);
        dom.intakeInputGuide.textContent = `A useful answer is at least ${question.min} characters. No demographic detail is required unless it is genuinely relevant.`;
        dom.intakeBackBtn.disabled = state.intakeIndex === 0;
        dom.intakeSkipBtn.hidden = true;
        dom.intakeNextBtn.querySelector("span").textContent = saved ? "Update answer & continue" : "Save answer & continue";
        dom.intakeOptions.innerHTML = question.options.map(([label, value]) => `
            <button type="button" data-intake-option="${escapeAttr(value)}">${escapeHtml(label)}</button>
        `).join("");
        dom.intakeOptions.querySelectorAll("[data-intake-option]").forEach((button) => {
            button.addEventListener("click", () => {
                const value = button.dataset.intakeOption;
                if (question.optionMode === "append") {
                    const current = dom.intakeTextInput.value.trim();
                    dom.intakeTextInput.value = current
                        ? `${current.replace(/[.;,\s]+$/, "")}; ${value}.`
                        : `${value}. `;
                } else {
                    dom.intakeTextInput.value = value;
                }
                dom.intakeTextInput.dispatchEvent(new Event("input", { bubbles: true }));
                dom.intakeTextInput.focus();
            });
        });
        window.setTimeout(() => dom.intakeTextInput.focus({ preventScroll: true }), 40);
    }

    function editIntakeAnswer(index) {
        const questions = activeIntakeQuestions();
        if (!Number.isInteger(index) || index < 0 || index >= questions.length) return;
        state.intakeIndex = index;
        state.intakeComplete = false;
        dom.planValidation.textContent = "";
        renderIntake();
    }

    function saveCurrentIntakeAnswer() {
        const questionsBeforeSave = activeIntakeQuestions();
        const question = questionsBeforeSave[state.intakeIndex];
        if (!question) return;
        const answer = dom.intakeTextInput.value.trim();
        if (answer.length < question.min) {
            dom.planValidation.textContent = `Please add a little more detail (${question.min} characters or more) so the later scenario has concrete evidence.`;
            dom.intakeBuildActions.hidden = false;
            dom.intakeTextInput.focus();
            return;
        }
        dom.planValidation.textContent = "";
        state.intakeAnswers[question.id] = answer;
        const questionsAfterSave = activeIntakeQuestions();
        if (state.intakeIndex >= questionsAfterSave.length - 1) {
            state.intakeComplete = intakeIsComplete();
        } else {
            state.intakeIndex += 1;
        }
        syncIntakePayload();
        saveUnsavedDraft();
        renderIntake();
    }

    function titleFromIntake() {
        const context = intakeAnswer("research_context").replace(/\s+/g, " ");
        if (!context) return "Untitled Ethical Mirror";
        const firstClause = context.split(/[.!?;:\n]/)[0].trim();
        const compact = firstClause.length > 92 ? `${firstClause.slice(0, 91).trim()}…` : firstClause;
        return `${compact} · AI app concept`.slice(0, 140);
    }

    function synthesiseResearchPlan() {
        const sections = [
            ["Research area and context", intakeAnswer("research_context")],
            ["Intended change", intakeAnswer("intended_change")],
            ["Direct users and encounter", intakeAnswer("direct_users")],
            ["AI role and decision authority", intakeAnswer("ai_role")],
            ["Data and materials", intakeAnswer("data_materials")],
            ["Sensitive-data necessity and alternative", intakeAnswer("sensitive_data_justification")],
            ["People affected without direct use", intakeAnswer("affected_others")],
            ["Researcher-authored value commitment", intakeAnswer("value_commitment")],
            ["Pause or redesign condition", intakeAnswer("stop_condition")],
        ];
        const perspective = dom.intakeOptionalContext?.value.trim();
        if (perspective) sections.push(["Optional researcher perspective context", perspective]);
        return sections
            .filter(([, value]) => value)
            .map(([label, value]) => `${label}\n${value}`)
            .join("\n\n");
    }

    function syncIntakePayload() {
        dom.projectTitle.value = titleFromIntake();
        dom.researchPlan.value = synthesiseResearchPlan();
        const commitments = [
            intakeAnswer("value_commitment"),
            intakeAnswer("stop_condition")
                ? `The research team will pause or redesign the app if ${intakeAnswer("stop_condition").replace(/^[Ii]\s+would\s+/, "")}`
                : "",
        ].filter(Boolean);
        setCommitments(commitments.length ? commitments : [""]);
        updatePlanSignals();
    }

    function getCommitments() {
        return [...dom.commitmentList.querySelectorAll("[data-commitment-input]")]
            .map((input) => input.value.trim())
            .filter(Boolean);
    }

    function addCommitment(value = "") {
        const rows = [...dom.commitmentList.querySelectorAll("[data-commitment-row]")];
        if (rows.length >= 5) {
            toast("Commitment limit reached", "Use up to five concrete commitments so the later map stays inspectable.");
            return null;
        }
        const wrapper = document.createElement("div");
        wrapper.className = "commitment-input-row";
        wrapper.setAttribute("data-commitment-row", "");
        wrapper.innerHTML = `
            <span class="commitment-index">${rows.length + 1}</span>
            <textarea data-commitment-input rows="2" maxlength="260" placeholder="My app should…">${escapeHtml(value)}</textarea>
            <button class="remove-commitment" data-remove-commitment type="button" aria-label="Remove commitment">×</button>
        `;
        dom.commitmentList.appendChild(wrapper);
        bindCommitmentRow(wrapper);
        updateCommitmentCount();
        return wrapper.querySelector("textarea");
    }

    function bindCommitmentRow(row) {
        row.querySelector("[data-remove-commitment]")?.addEventListener("click", () => {
            const rows = [...dom.commitmentList.querySelectorAll("[data-commitment-row]")];
            if (rows.length <= 1) {
                toast("Keep one commitment", "The Ethical Mirror needs at least one researcher-authored standard.");
                return;
            }
            row.remove();
            renumberCommitments();
            markDraftChanged();
        });
        row.querySelector("[data-commitment-input]")?.addEventListener("input", () => {
            updateCommitmentCount();
            saveUnsavedDraft();
        });
    }

    function renumberCommitments() {
        [...dom.commitmentList.querySelectorAll("[data-commitment-row]")].forEach((row, index) => {
            row.querySelector(".commitment-index").textContent = String(index + 1);
        });
        updateCommitmentCount();
    }

    function updateCommitmentCount() {
        const total = dom.commitmentList.querySelectorAll("[data-commitment-row]").length;
        const complete = getCommitments().length;
        dom.commitmentCount.textContent = `${complete || total} / 5`;
        dom.addCommitmentBtn.disabled = total >= 5;
    }

    function setCommitments(values) {
        dom.commitmentList.innerHTML = "";
        const list = values?.length ? values.slice(0, 5) : ["", ""];
        list.forEach((value) => addCommitment(value));
        renumberCommitments();
    }

    function updatePlanSignals() {
        const text = dom.researchPlan.value;
        const words = text.trim() ? text.trim().split(/\s+/).length : 0;
        dom.planWordCount.textContent = String(words);
        const patterns = {
            purpose: /\b(aim|goal|purpose|research question|study|evaluate|investigate|build|design)\b/i,
            people: /\b(user|participant|student|researcher|teacher|worker|patient|community|people|person|group)\b/i,
            ai: /\b(AI|artificial intelligence|LLM|language model|model|agent|algorithm|automated)\b/i,
            data: /\b(data|log|record|prompt|response|transcript|image|audio|video|dataset|collect|store)\b/i,
            setting: /\b(university|school|classroom|workplace|online|platform|clinic|community|home|deployment|setting|field)\b/i,
        };
        let visible = 0;
        Object.entries(patterns).forEach(([key, pattern]) => {
            const match = pattern.test(text);
            dom.signalRow.querySelector(`[data-signal="${key}"]`)?.classList.toggle("is-visible", match);
            if (match) visible += 1;
        });
        dom.planSignals.textContent = `${visible} of 5 planning signals visible`;
        saveUnsavedDraft();
    }

    function saveUnsavedDraft() {
        if (state.session) return;
        try {
            localStorage.setItem(DRAFT_KEY, JSON.stringify({
                title: dom.projectTitle.value,
                plan: dom.researchPlan.value,
                commitments: getCommitments(),
                intake_answers: state.intakeAnswers,
                intake_index: state.intakeIndex,
                intake_complete: state.intakeComplete,
                optional_context: dom.intakeOptionalContext?.value || "",
            }));
        } catch {
            // Browser storage can be unavailable in privacy modes. The form still works.
        }
    }

    function loadUnsavedDraft() {
        if (state.session) return;
        try {
            const raw = localStorage.getItem(DRAFT_KEY);
            if (!raw) return;
            const draft = JSON.parse(raw);
            if (!draft || (!draft.plan && !draft.title && !draft.intake_answers)) return;
            state.intakeAnswers = draft.intake_answers && typeof draft.intake_answers === "object"
                ? { ...draft.intake_answers }
                : {};
            state.intakeIndex = clamp(
                Number(draft.intake_index || 0),
                0,
                activeIntakeQuestions().length - 1
            );
            state.intakeComplete = Boolean(draft.intake_complete && intakeIsComplete());
            if (dom.intakeOptionalContext) dom.intakeOptionalContext.value = draft.optional_context || "";
            if (Object.keys(state.intakeAnswers).length) {
                syncIntakePayload();
                renderIntake();
            } else {
                dom.projectTitle.value = draft.title || "";
                dom.researchPlan.value = draft.plan || "";
                setCommitments(draft.commitments?.length ? draft.commitments : [""]);
                updatePlanSignals();
            }
        } catch {
            // Ignore malformed or inaccessible local drafts.
        }
    }

    function validatePlan() {
        syncIntakePayload();
        const title = dom.projectTitle.value.trim();
        const plan = dom.researchPlan.value.trim();
        const commitments = getCommitments();
        const errors = [];
        if (!intakeIsComplete()) errors.push("Complete the eight short questions before building the mirror.");
        if (!title) errors.push("Add enough context for SafeBARS to name the working plan.");
        if (plan.split(/\s+/).filter(Boolean).length < 45) errors.push("Please give a little more detail so the role probes have concrete design evidence.");
        if (commitments.length < 1) errors.push("State at least one value commitment in your own words.");
        if (commitments.some((item) => item.length < 18)) errors.push("Make the commitment specific enough to examine.");
        dom.planValidation.textContent = errors[0] || "";
        return errors.length ? null : {
            title,
            research_plan: plan,
            value_commitments: commitments,
            intake_answers: {
                ...state.intakeAnswers,
                ...(dom.intakeOptionalContext?.value.trim()
                    ? { optional_perspective_context: dom.intakeOptionalContext.value.trim() }
                    : {}),
            },
        };
    }

    async function createAndAnalyse(event) {
        event?.preventDefault();
        const payload = validatePlan();
        if (!payload) return;
        setBusy(true);
        showLoading({
            eyebrow: "Building the mirror",
            title: "Tracing claims through possible futures…",
            detail: "Bounded role probes examine the same plan separately while keeping literature evidence distinct from generated inference.",
        });
        try {
            const created = await api("/sessions", { method: "POST", body: payload });
            state.session = normaliseSession(unwrapSession(created));
            if (!state.session.id) throw new Error("The server created a response without a session identifier.");
            localStorage.setItem(STORAGE_KEY, state.session.id);
            localStorage.removeItem(DRAFT_KEY);
            syncSessionIntoUi();
            advanceLoading(1);
            const analysed = await api(`/sessions/${encodeURIComponent(state.session.id)}/analyze`, {
                method: "POST",
                body: { use_llm: true },
            });
            advanceLoading(3);
            state.session = normaliseSession(unwrapSession(analysed), state.session);
            state.session.analyzed_at = state.session.analyzed_at || new Date().toISOString();
            syncSessionIntoUi();
            renderAll();
            navigateToStep(2, true);
            const probeMode = state.session.analysis_mode?.llm_used
                ? `${state.session.analysis_mode.role_probe_count || state.session.scenarios.length} model-enriched bounded role probes`
                : `${state.session.scenarios.length} deterministic bounded fallback probes`;
            toast("Consequence map ready", `${probeMode} and ${state.session.dissonance_edges.length} inspectable tension paths were generated.`);
        } catch (error) {
            dom.planValidation.textContent = error.message;
            toast("Could not build the mirror", error.message, "error");
        } finally {
            hideLoading();
            setBusy(false);
        }
    }

    async function runAnalysis() {
        if (!state.session?.id) {
            navigateToStep(1, true);
            toast("Save the plan first", "Build a session before running the perspective analysis.", "error");
            return;
        }
        setBusy(true);
        showLoading({
            eyebrow: "Re-running analysis",
            title: "Checking the current plan against the same lenses…",
            detail: "Existing researcher responses remain visible; new model output does not silently overwrite them.",
        });
        try {
            const result = await api(`/sessions/${encodeURIComponent(state.session.id)}/analyze`, {
                method: "POST",
                body: { use_llm: true },
            });
            state.session = normaliseSession(unwrapSession(result), state.session);
            state.session.analyzed_at = state.session.analyzed_at || new Date().toISOString();
            renderAll();
            toast("Analysis refreshed", "Coverage, scenarios, and tension paths now reflect the current saved plan.");
        } catch (error) {
            toast("Analysis did not complete", error.message, "error");
        } finally {
            hideLoading();
            setBusy(false);
        }
    }

    async function restoreSession(sessionId, notify = true) {
        if (!sessionId) return;
        setBusy(true);
        try {
            const result = await api(`/sessions/${encodeURIComponent(sessionId)}`);
            state.session = normaliseSession(unwrapSession(result));
            if (!state.session.id) throw new Error("The saved session is no longer available.");
            localStorage.setItem(STORAGE_KEY, state.session.id);
            hydrateResolutionDrafts();
            syncSessionIntoUi();
            renderAll();
            const nextStep = state.session.ledger.length ? 6
                : state.session.dissonance_edges.length ? 4
                    : state.session.lenses.length ? 2 : 1;
            navigateToStep(nextStep, true);
            state.restored = true;
            if (notify) toast("Session restored", state.session.title);
        } catch (error) {
            localStorage.removeItem(STORAGE_KEY);
            dom.resumeBtn.hidden = true;
            if (notify) toast("Could not restore session", error.message, "error");
        } finally {
            setBusy(false);
        }
    }

    function hydrateResolutionDrafts() {
        state.resolutionDrafts = {};
        const revisionHistory = asArray(state.session?.revisions);
        const latestRevision = [...revisionHistory].reverse().find((revision) => (
            revision && typeof revision === "object" && Array.isArray(revision.resolutions)
        ));
        const resolutionItems = latestRevision
            ? latestRevision.resolutions
            : revisionHistory;
        asArray(resolutionItems).forEach((revision) => {
            const edgeId = firstValue(revision.edge_id, revision.tension_id, revision.path_id, revision.id);
            if (!edgeId) return;
            const decision = firstValue(revision.resolution_type, revision.decision, revision.choice, revision.response_type, "");
            const uiDecision = decision === "revise" ? "revise_design"
                : decision === "consult_stakeholder" ? "consult_stakeholders"
                    : decision;
            state.resolutionDrafts[edgeId] = {
                edge_id: edgeId,
                resolution_type: uiDecision,
                rationale: firstValue(revision.rationale, revision.response, revision.researcher_response, ""),
                follow_up: firstValue(revision.follow_up, revision.evidence, revision.verification, ""),
            };
        });
    }

    function syncSessionIntoUi() {
        if (!state.session) return;
        const savedIntake = state.session.intake_answers;
        if (savedIntake && typeof savedIntake === "object" && Object.keys(savedIntake).length) {
            state.intakeAnswers = Object.fromEntries(
                INTAKE_QUESTIONS
                    .map((question) => [question.id, String(savedIntake[question.id] || "").trim()])
                    .filter(([, value]) => value)
            );
            const questions = activeIntakeQuestions();
            const firstMissing = questions.findIndex((question) => !intakeAnswer(question.id));
            state.intakeIndex = firstMissing >= 0 ? firstMissing : questions.length - 1;
            state.intakeComplete = intakeIsComplete();
            if (dom.intakeOptionalContext) {
                dom.intakeOptionalContext.value = savedIntake.optional_perspective_context || "";
            }
            renderIntake();
        } else {
            dom.projectTitle.value = state.session.title || "";
            dom.researchPlan.value = state.session.research_plan || "";
            setCommitments(state.session.value_commitments || []);
        }
        dom.revisedPlan.value = state.session.revised_plan || state.session.research_plan || "";
        dom.originalPlanView.textContent = state.session.original_research_plan || state.session.research_plan || "";
        dom.sessionLabel.textContent = `${state.session.title} · ${state.session.id}`;
        updatePlanSignals();
        updateRevisionStats();
        dom.resumeBtn.hidden = true;
    }

    function mergeSessionPayload(payload) {
        state.session = normaliseSession(unwrapSession(payload), state.session);
        syncSessionIntoUi();
        renderAll();
    }

    function setBusy(busy) {
        document.body.classList.toggle("is-busy", busy);
        [dom.buildMirrorBtn, dom.reanalyzeBtn, dom.saveRevisionBtn, dom.replayBtn].forEach((button) => {
            if (button) button.disabled = busy;
        });
    }

    function showLoading({ eyebrow, title, detail }) {
        dom.loadingEyebrow.textContent = eyebrow;
        dom.loadingTitle.textContent = title;
        dom.loadingDetail.textContent = detail;
        dom.loadingLayer.hidden = false;
        document.body.style.overflow = "hidden";
        let index = 0;
        updateLoadingSteps(index);
        clearInterval(state.loadingTimer);
        state.loadingTimer = window.setInterval(() => {
            index = Math.min(3, index + 1);
            updateLoadingSteps(index);
        }, 1300);
    }

    function advanceLoading(index) {
        updateLoadingSteps(index);
    }

    function updateLoadingSteps(activeIndex) {
        [...dom.loadingSteps.children].forEach((step, index) => {
            step.classList.toggle("is-active", index <= activeIndex);
        });
    }

    function hideLoading() {
        clearInterval(state.loadingTimer);
        state.loadingTimer = null;
        dom.loadingLayer.hidden = true;
        document.body.style.overflow = "";
    }

    function renderAll() {
        renderLenses();
        renderScenarios();
        renderGraph();
        renderTensions();
        renderLedger();
        updateProgress();
        updateRevisionStats();
        dom.literatureCount.textContent = String(state.literature.length);
    }

    function renderLenses() {
        const lenses = state.session?.lenses?.length
            ? state.session.lenses
            : FALLBACK_LENSES.map((lens, index) => normaliseLens(lens, index));
        const counts = Object.fromEntries(COVERAGE_ORDER.map((key) => [key, 0]));
        lenses.forEach((lens) => { counts[lens.status] = (counts[lens.status] || 0) + 1; });
        const actionCount = counts["action-linked"];
        const reasonedCount = counts.reasoned;
        dom.coverageHeadline.textContent = state.session?.lenses?.length
            ? `${reasonedCount + actionCount} of ${lenses.length} lenses contain reasoning or an action`
            : "Run analysis to locate evidence in the plan";
        dom.lensAllCount.textContent = String(lenses.length);
        dom.coverageTrack.innerHTML = COVERAGE_ORDER.map((status) => {
            const count = counts[status] || 0;
            return `<span class="${status}" style="flex:${count}" title="${COVERAGE_LABELS[status]}: ${count}"></span>`;
        }).join("");
        dom.coverageLabels.innerHTML = COVERAGE_ORDER.map((status) => `
            <span><i class="coverage-dot ${status}"></i>${COVERAGE_LABELS[status]} · ${counts[status] || 0}</span>
        `).join("");

        const visible = lenses.filter((lens) => state.lensFilter === "all" || lens.status === state.lensFilter);
        dom.lensEmpty.hidden = visible.length > 0;
        dom.lensGrid.innerHTML = visible.map((lens, index) => {
            const number = String(lenses.findIndex((item) => item.id === lens.id) + 1).padStart(2, "0");
            const sourceLabel = lens.source_ids?.length
                ? lens.source_ids.map((sourceId) => {
                    const source = state.literature.find((item) => item.id === sourceId);
                    return source ? firstValue(source.venue, source.citation, source.title) : sourceId;
                }).join(" · ")
                : lens.source_label;
            const evidence = lens.evidence || (
                lens.status === "missing"
                    ? "No matching plan passage was located. Absence is a question for review, not proof of a problem."
                    : "A matching passage was identified; open this lens to inspect how it was interpreted."
            );
            return `
                <article class="lens-card" data-lens-id="${escapeAttr(lens.id)}">
                    <button class="lens-card-button" type="button" aria-expanded="false">
                        <span class="lens-card-top">
                            <span class="lens-number">${number}</span>
                            <span class="coverage-pill ${lens.status}">${escapeHtml(COVERAGE_LABELS[lens.status])}</span>
                        </span>
                        <h3>${escapeHtml(lens.label)}</h3>
                        <p class="lens-card-summary">${escapeHtml(lens.description)}</p>
                        <p class="lens-evidence-preview">“${escapeHtml(shortText(evidence, 165))}”</p>
                        <span class="lens-source-row">
                            <span>${escapeHtml(sourceLabel)}</span>
                            <span>Inspect ↓</span>
                        </span>
                    </button>
                    <div class="lens-detail">
                        <div class="lens-detail-section">
                            <strong>Plan evidence</strong>
                            <p>${escapeHtml(evidence)}</p>
                        </div>
                        <div class="lens-detail-section">
                            <strong>Interpretation</strong>
                            <p>${escapeHtml(lens.explanation || "Coverage reflects the specificity of evidence in the submitted plan, not the moral quality of the project.")}</p>
                        </div>
                        <div class="lens-detail-section">
                            <strong>Reflection prompt</strong>
                            <p>${escapeHtml(lens.next_action || lens.question)}</p>
                        </div>
                        ${lens.boundary ? `
                            <div class="lens-detail-section">
                                <strong>Interpretation boundary</strong>
                                <p>${escapeHtml(lens.boundary)}</p>
                            </div>
                        ` : ""}
                    </div>
                </article>
            `;
        }).join("");

        dom.lensGrid.querySelectorAll(".lens-card-button").forEach((button) => {
            button.addEventListener("click", () => {
                const card = button.closest(".lens-card");
                const open = !card.classList.contains("is-open");
                card.classList.toggle("is-open", open);
                button.setAttribute("aria-expanded", String(open));
            });
        });
    }

    function renderScenarios() {
        const scenarios = [...(state.session?.scenarios || [])];
        const roles = [...new Set(scenarios.map((scenario) => scenario.role))];
        dom.roleFilter.innerHTML = `
            <button class="filter-chip ${state.roleFilter === "all" ? "is-active" : ""}" type="button" data-role-filter="all" aria-pressed="${state.roleFilter === "all"}">All roles</button>
            ${roles.map((role) => `
                <button class="filter-chip ${state.roleFilter === role ? "is-active" : ""}" type="button" data-role-filter="${escapeAttr(role)}" aria-pressed="${state.roleFilter === role}">${escapeHtml(role)}</button>
            `).join("")}
        `;
        dom.roleFilter.querySelectorAll("[data-role-filter]").forEach((button) => {
            button.addEventListener("click", () => {
                const nextRole = button.dataset.roleFilter;
                state.roleFilter = nextRole;
                if (nextRole !== "all") {
                    state.selectedScenarioId = scenarios.find((scenario) => scenario.role === nextRole)?.id || null;
                }
                renderScenarios();
            });
        });

        let visible = scenarios.filter((scenario) => state.roleFilter === "all" || scenario.role === state.roleFilter);
        visible.sort((a, b) => {
            if (state.scenarioSort === "role") return a.role.localeCompare(b.role);
            if (state.scenarioSort === "uncertainty") return b.uncertainty - a.uncertainty;
            return b.tension - a.tension;
        });

        if (!scenarios.length) {
            dom.scenarioList.innerHTML = `
                <div class="empty-state">
                    <span aria-hidden="true">◎</span>
                    <h3>No scenarios yet</h3>
                    <p>Run the analysis to create bounded affected-role probes.</p>
                </div>
            `;
            renderScenarioStage(null);
            return;
        }

        const selectedScenarioIsVisible = visible.some((scenario) => scenario.id === state.selectedScenarioId);
        if (!state.selectedScenarioId || !selectedScenarioIsVisible) {
            state.selectedScenarioId = visible[0]?.id || null;
        }

        dom.scenarioList.innerHTML = visible.map((scenario) => `
            <button class="scenario-card ${scenario.id === state.selectedScenarioId ? "is-active" : ""}" type="button" data-scenario-id="${escapeAttr(scenario.id)}">
                <span class="scenario-card-top">
                    <span class="role-label"><i></i>${escapeHtml(scenario.role)}</span>
                    <span class="uncertainty-label">${Math.round(scenario.uncertainty * 100)}% uncertain</span>
                </span>
                <h3>${escapeHtml(scenario.title)}</h3>
                <p>${escapeHtml(scenario.summary || scenario.consequence)}</p>
                <span class="scenario-card-footer">
                    <span class="tension-meter" aria-label="Tension strength ${Math.round(scenario.tension)} of 4">
                        ${[1, 2, 3, 4].map((level) => `<i class="${level <= scenario.tension ? "is-on" : ""}"></i>`).join("")}
                    </span>
                    <span>${scenario.generation_mode.startsWith("llm") ? "AI role probe · synthetic" : "bounded fallback · synthetic"}</span>
                </span>
            </button>
        `).join("");
        dom.scenarioList.querySelectorAll("[data-scenario-id]").forEach((button) => {
            button.addEventListener("click", () => {
                state.selectedScenarioId = button.dataset.scenarioId;
                renderScenarios();
            });
        });
        renderScenarioStage(visible.find((scenario) => scenario.id === state.selectedScenarioId) || null);
    }

    function defaultFrames(scenario) {
        return [
            {
                title: "Design enters use",
                text: shortText(scenario.plan_evidence || "The proposed app is introduced in the stated setting.", 105),
                visual_type: "app",
            },
            {
                title: `${scenario.role} encounters it`,
                text: shortText(scenario.summary || "The role experiences a design decision from a different position.", 105),
                visual_type: "people",
            },
            {
                title: "A consequence unfolds",
                text: shortText(scenario.consequence || "A downstream effect becomes visible.", 105),
                visual_type: "data",
            },
        ];
    }

    function storyVisual(type, frame) {
        const mode = String(type || "").toLowerCase();
        if (mode.includes("people") || mode.includes("user") || mode.includes("role")) {
            return `
                <div class="visual-people" aria-label="Abstract people and relationship illustration">
                    <span class="visual-person"></span>
                    <span class="visual-person is-distant"></span>
                </div>`;
        }
        if (mode.includes("data") || mode.includes("outcome") || mode.includes("network")) {
            return `
                <div class="visual-data" aria-label="Abstract data flow illustration">
                    <span></span><span></span><span></span>
                </div>`;
        }
        return `
            <div class="visual-app" aria-label="Abstract application interface illustration">
                <div class="visual-app-bar"></div>
                <div class="visual-app-body">
                    <div class="visual-line"></div>
                    <div class="visual-line short"></div>
                    <div class="visual-alert">${escapeHtml(shortText(frame.title, 30))}</div>
                </div>
            </div>`;
    }

    function renderScenarioStage(scenario) {
        if (!scenario) {
            dom.scenarioStage.innerHTML = `
                <div class="stage-placeholder">
                    <span class="stage-placeholder-mark" aria-hidden="true">→</span>
                    <h2>Select a scenario</h2>
                    <p>Inspect its evidence, assumptions, and a short future-incident storyboard.</p>
                </div>`;
            return;
        }
        const frames = scenario.frames.length ? scenario.frames : defaultFrames(scenario);
        dom.scenarioStage.innerHTML = `
            <div class="stage-content">
                <header class="stage-header">
                    <span class="stage-role"><span>${escapeHtml(scenario.role.charAt(0).toUpperCase())}</span>${escapeHtml(scenario.role)} · ${scenario.generation_mode.startsWith("llm") ? "AI role probe" : "bounded fallback"} · synthetic</span>
                    <h2>${escapeHtml(scenario.title)}</h2>
                    <p>${escapeHtml(scenario.summary || scenario.consequence)}</p>
                </header>
                <div class="storyboard" aria-label="Generated future-incident storyboard">
                    ${frames.slice(0, 3).map((frame, index) => `
                        <article class="story-frame">
                            <div class="story-visual">
                                <span class="story-frame-number">${index + 1}</span>
                                ${storyVisual(frame.visual_type, frame)}
                            </div>
                            <h3>${escapeHtml(frame.title)}</h3>
                            <p>${escapeHtml(frame.text)}</p>
                        </article>
                    `).join("")}
                </div>
                <div class="scenario-evidence-grid">
                    <div class="evidence-block">
                        <strong>Submitted plan evidence</strong>
                        <p>${escapeHtml(scenario.plan_evidence || "No exact passage was supplied with this scenario. Inspect the research plan before acting.")}</p>
                    </div>
                    <div class="evidence-block">
                        <strong>Published case or literature</strong>
                        <p>${escapeHtml(scenario.literature_evidence || "Open the grounding sources and verify whether the analogy fits this setting.")}</p>
                    </div>
                    <div class="evidence-block inference">
                        <strong>${scenario.generation_mode.startsWith("llm") ? "Model-generated role probe" : "Bounded fallback probe"} · not testimony</strong>
                        <p>${escapeHtml(scenario.inference)}</p>
                    </div>
                    <div class="evidence-block inference">
                        <strong>Question for real people</strong>
                        <p>${escapeHtml(scenario.question)}</p>
                    </div>
                </div>
                <div class="stage-actions">
                    <button class="secondary-button" type="button" data-scenario-to-map="${escapeAttr(scenario.id)}">Inspect its argument path</button>
                    <button class="primary-button" type="button" data-scenario-to-revision="${escapeAttr(scenario.id)}">Take to revision</button>
                </div>
            </div>
        `;
        dom.scenarioStage.scrollTop = 0;
        dom.scenarioStage.querySelector("[data-scenario-to-map]")?.addEventListener("click", () => {
            const edge = state.session.dissonance_edges.find((item) => item.scenario_id === scenario.id);
            if (edge) selectEdge(edge.id);
            navigateToStep(4, true);
        });
        dom.scenarioStage.querySelector("[data-scenario-to-revision]")?.addEventListener("click", () => {
            const edge = state.session.dissonance_edges.find((item) => item.scenario_id === scenario.id);
            if (edge) state.selectedTensionId = edge.id;
            navigateToStep(5, true);
            renderTensions();
        });
    }

    function graphEdges() {
        const edges = state.session?.dissonance_edges || [];
        if (state.mapMode === "strong") {
            return edges.filter((edge) => edge.tension >= 2.5 || edge.relation.includes("conflict"));
        }
        return edges;
    }

    function wrapSvgText(text, maxChars = 28, maxLines = 3) {
        const words = String(text || "").split(/\s+/);
        const lines = [];
        let current = "";
        words.forEach((word) => {
            if (lines.length >= maxLines) return;
            const candidate = current ? `${current} ${word}` : word;
            if (candidate.length > maxChars && current) {
                lines.push(current);
                current = word;
            } else {
                current = candidate;
            }
        });
        if (current && lines.length < maxLines) lines.push(current);
        const original = words.join(" ");
        const combined = lines.join(" ");
        if (combined.length < original.length && lines.length) {
            lines[lines.length - 1] = `${lines[lines.length - 1].replace(/[.…]+$/, "")}…`;
        }
        return lines;
    }

    function svgNodeMarkup(edge, type, text, x, y, width, kindLabel) {
        const lines = wrapSvgText(text, type === "commitment" ? 32 : 29, 3);
        const height = 90;
        return `
            <g class="graph-node ${type}" data-edge-id="${escapeAttr(edge.id)}" data-node-type="${type}" tabindex="0" role="button" aria-label="${escapeAttr(`${kindLabel}: ${text}`)}" transform="translate(${x} ${y})">
                <rect width="${width}" height="${height}" rx="14"></rect>
                <rect class="node-accent" x="0" y="0" width="6" height="${height}" rx="3"></rect>
                <text class="node-kind" x="17" y="22">${escapeHtml(kindLabel.toUpperCase())}</text>
                <text x="17" y="43">
                    ${lines.map((line, index) => `<tspan x="17" dy="${index === 0 ? 0 : 15}">${escapeHtml(line)}</tspan>`).join("")}
                </text>
            </g>
        `;
    }

    function renderGraph() {
        const edges = graphEdges();
        dom.graphEmpty.hidden = edges.length > 0;
        dom.dissonanceGraph.style.display = edges.length ? "block" : "none";
        if (!edges.length) {
            dom.graphViewport.innerHTML = "";
            renderInspector(null);
            return;
        }

        const positions = [
            { x: 18, width: 235, type: "commitment", key: "commitment", label: "My commitment" },
            { x: 294, width: 235, type: "evidence", key: "evidence", label: "Plan evidence" },
            { x: 570, width: 235, type: "consequence", key: "consequence", label: "Possible consequence" },
            { x: 846, width: 240, type: "party", key: "affected_party", label: "Affected party" },
        ];
        const rowHeight = 122;
        const height = Math.max(640, edges.length * rowHeight + 54);
        dom.dissonanceGraph.setAttribute("viewBox", `0 0 1120 ${height}`);
        dom.dissonanceGraph.setAttribute("height", String(Math.min(Math.max(610, height), 1100)));

        const markup = [];
        edges.forEach((edge, index) => {
            const y = 27 + index * rowHeight;
            const isConflict = edge.relation.includes("conflict") || edge.relation.includes("tension");
            const edgeClass = isConflict ? "conflict" : "neutral";
            for (let connection = 0; connection < positions.length - 1; connection += 1) {
                const from = positions[connection];
                const to = positions[connection + 1];
                const x1 = from.x + from.width;
                const x2 = to.x;
                const mid = (x1 + x2) / 2;
                const yMid = y + 45;
                markup.push(`
                    <path class="graph-edge ${edgeClass}" data-edge-id="${escapeAttr(edge.id)}"
                        d="M${x1},${yMid} C${mid},${yMid} ${mid},${yMid} ${x2 - 7},${yMid}"
                        marker-end="url(#${isConflict && connection === 1 ? "arrowConflict" : "arrowNeutral"})"></path>
                `);
            }
            positions.forEach((position) => {
                markup.push(svgNodeMarkup(edge, position.type, edge[position.key], position.x, y, position.width, position.label));
            });
        });
        dom.graphViewport.innerHTML = markup.join("");
        applyGraphScale();
        bindGraphEvents();
        if (state.selectedEdgeId && edges.some((edge) => edge.id === state.selectedEdgeId)) {
            selectEdge(state.selectedEdgeId, false);
        } else {
            renderInspector(null);
        }
    }

    function bindGraphEvents() {
        dom.graphViewport.querySelectorAll("[data-edge-id]").forEach((element) => {
            const activate = () => selectEdge(element.dataset.edgeId);
            element.addEventListener("click", activate);
            element.addEventListener("keydown", (event) => {
                if (event.key === "Enter" || event.key === " ") {
                    event.preventDefault();
                    activate();
                }
            });
            if (element.classList.contains("graph-node")) {
                element.addEventListener("mousemove", (event) => {
                    const edge = state.session.dissonance_edges.find((item) => item.id === element.dataset.edgeId);
                    if (!edge) return;
                    const nodeType = element.dataset.nodeType;
                    const labels = {
                        commitment: "Researcher-authored commitment",
                        evidence: "Evidence located in the plan",
                        consequence: "Generated possible consequence",
                        party: "Potentially affected position",
                    };
                    const key = nodeType === "party" ? "affected_party" : nodeType;
                    dom.graphTooltip.innerHTML = `<strong>${escapeHtml(labels[nodeType])}</strong><br>${escapeHtml(shortText(edge[key], 170))}`;
                    const wrapRect = dom.graphWrap.getBoundingClientRect();
                    dom.graphTooltip.style.left = `${event.clientX - wrapRect.left + dom.graphWrap.scrollLeft + 13}px`;
                    dom.graphTooltip.style.top = `${event.clientY - wrapRect.top + dom.graphWrap.scrollTop + 13}px`;
                    dom.graphTooltip.hidden = false;
                });
                element.addEventListener("mouseleave", () => {
                    dom.graphTooltip.hidden = true;
                });
            }
        });
    }

    function selectEdge(edgeId, rerenderInspector = true) {
        state.selectedEdgeId = edgeId;
        dom.graphViewport.querySelectorAll("[data-edge-id]").forEach((element) => {
            const selected = element.dataset.edgeId === edgeId;
            element.classList.toggle("is-selected", selected);
            element.classList.toggle("is-muted", !selected);
        });
        if (rerenderInspector) {
            const edge = state.session?.dissonance_edges?.find((item) => item.id === edgeId);
            renderInspector(edge || null);
        }
    }

    function clearEdgeSelection() {
        state.selectedEdgeId = null;
        dom.graphViewport.querySelectorAll("[data-edge-id]").forEach((element) => {
            element.classList.remove("is-selected", "is-muted");
        });
        renderInspector(null);
    }

    function renderInspector(edge) {
        if (!edge) {
            dom.pathInspector.innerHTML = `
                <div class="inspector-placeholder">
                    <span aria-hidden="true">↗</span>
                    <h2>Inspect one path</h2>
                    <p>Select a node or connection in the map. The argument will be shown as four claims you can verify separately.</p>
                </div>`;
            return;
        }
        const sourceLabels = edge.literature_ids.map((id) => {
            const source = state.literature.find((item) => item.id === id || item.url === id);
            return source ? source.citation : id;
        }).filter(Boolean);
        dom.pathInspector.innerHTML = `
            <div class="inspector-content">
                <header class="inspector-header">
                    <span class="tension-label">Inspectable tension · ${Math.round(edge.uncertainty * 100)}% uncertain</span>
                    <h2>${escapeHtml(shortText(edge.consequence, 105))}</h2>
                    <p>${escapeHtml(edge.rationale || "This path juxtaposes the researcher's declared standard with a concrete design choice and a plausible downstream experience.")}</p>
                </header>
                <div class="argument-chain">
                    <div class="argument-claim commitment"><span>1</span><div><small>I said</small><strong>${escapeHtml(edge.commitment)}</strong></div></div>
                    <div class="argument-claim evidence"><span>2</span><div><small>My current design says</small><strong>${escapeHtml(edge.evidence)}</strong></div></div>
                    <div class="argument-claim consequence"><span>3</span><div><small>A possible future is</small><strong>${escapeHtml(edge.consequence)}</strong></div></div>
                    <div class="argument-claim party"><span>4</span><div><small>Experienced from the position of</small><strong>${escapeHtml(edge.affected_party)}</strong></div></div>
                </div>
                <div class="inspector-evidence">
                    <strong>Grounding &amp; limit</strong>
                    <p>${escapeHtml(sourceLabels.join("; ") || "No source identifier was returned for this path. Verify the scenario before using it.")}</p>
                </div>
                <div class="inspector-actions">
                    <button class="primary-button" type="button" data-revise-edge="${escapeAttr(edge.id)}">Respond to this tension</button>
                    <button class="secondary-button" type="button" data-clear-edge>Return to all paths</button>
                </div>
            </div>
        `;
        dom.pathInspector.querySelector("[data-revise-edge]")?.addEventListener("click", () => {
            state.selectedTensionId = edge.id;
            navigateToStep(5, true);
            renderTensions();
        });
        dom.pathInspector.querySelector("[data-clear-edge]")?.addEventListener("click", clearEdgeSelection);
    }

    function applyGraphScale() {
        if (!dom.graphViewport) return;
        dom.graphViewport.setAttribute("transform", `scale(${state.graphScale})`);
    }

    function renderTensions() {
        const edges = state.session?.dissonance_edges || [];
        dom.tensionCount.textContent = String(edges.length);
        if (!edges.length) {
            dom.tensionList.innerHTML = `<div class="empty-state"><p>No tension paths are available yet.</p></div>`;
            renderResolutionPanel(null);
            return;
        }
        if (!state.selectedTensionId || !edges.some((edge) => edge.id === state.selectedTensionId)) {
            state.selectedTensionId = edges[0].id;
        }
        dom.tensionList.innerHTML = edges.map((edge, index) => {
            const hasResponse = Boolean(state.resolutionDrafts[edge.id]?.resolution_type);
            const isThreshold = /\b(pause|redesign|stop condition|stopping rule|trigger)\b/i.test(edge.commitment);
            const commitmentKind = isThreshold ? "Redesign threshold" : `Commitment ${index + 1}`;
            return `
                <button class="tension-item ${edge.id === state.selectedTensionId ? "is-active" : ""} ${hasResponse ? "has-response" : ""}" type="button" data-tension-id="${escapeAttr(edge.id)}">
                    <span class="tension-item-status">${hasResponse ? "✓" : index + 1}</span>
                    <span>
                        <span class="tension-item-kind">${escapeHtml(commitmentKind)}</span>
                        <strong>${escapeHtml(shortText(edge.commitment, 105))}</strong>
                        <small><b>Possible consequence:</b> ${escapeHtml(shortText(edge.consequence, 92))}</small>
                        <small>${escapeHtml(edge.affected_party)} · ${hasResponse ? RESOLUTION_TYPES[state.resolutionDrafts[edge.id].resolution_type]?.label || "Responded" : "Awaiting response"}</small>
                    </span>
                </button>`;
        }).join("");
        dom.tensionList.querySelectorAll("[data-tension-id]").forEach((button) => {
            button.addEventListener("click", () => {
                state.selectedTensionId = button.dataset.tensionId;
                renderTensions();
            });
        });
        renderResolutionPanel(edges.find((edge) => edge.id === state.selectedTensionId));
    }

    function renderResolutionPanel(edge) {
        if (!edge) {
            dom.resolutionPanel.innerHTML = `
                <div class="resolution-placeholder">
                    <span aria-hidden="true">⌁</span>
                    <h2>Select a tension to respond</h2>
                    <p>Each response is recorded with the relevant commitment, plan passage, scenario, and literature source.</p>
                </div>`;
            return;
        }
        const draft = state.resolutionDrafts[edge.id] || {
            edge_id: edge.id,
            resolution_type: "",
            rationale: "",
            follow_up: "",
        };
        dom.resolutionPanel.innerHTML = `
            <div class="resolution-content">
                <div class="resolution-context">
                    <div><small>Commitment</small><strong>${escapeHtml(edge.commitment)}</strong></div>
                    <div><small>Possible consequence</small><strong>${escapeHtml(edge.consequence)}</strong></div>
                </div>
                <h2>How will you respond?</h2>
                <p>None of the four choices is automatically “correct.” Your rationale and next action are the research evidence.</p>
                <div class="resolution-options" role="radiogroup" aria-label="Resolution for selected tension">
                    ${Object.entries(RESOLUTION_TYPES).map(([key, option]) => `
                        <label class="resolution-option">
                            <input type="radio" name="resolution-${escapeAttr(edge.id)}" value="${key}" ${draft.resolution_type === key ? "checked" : ""}>
                            <span class="resolution-option-icon" aria-hidden="true">${option.icon}</span>
                            <span><strong>${option.label}</strong><small>${option.help}</small></span>
                        </label>
                    `).join("")}
                </div>
                <div class="response-fields">
                    <label>
                        Why this response?
                        <textarea data-response-rationale placeholder="Explain your reasoning in relation to this project and affected role.">${escapeHtml(draft.rationale)}</textarea>
                    </label>
                    <label>
                        What would count as follow-up evidence?
                        <textarea data-response-follow-up placeholder="Name an edit, test, source, accountable person, or stakeholder question.">${escapeHtml(draft.follow_up)}</textarea>
                    </label>
                </div>
                ${edge.suggested_revision ? `
                    <button class="secondary-button" type="button" data-apply-suggestion="${escapeAttr(edge.id)}">Preview AI-proposed wording in the editor</button>
                ` : ""}
            </div>
        `;
        dom.resolutionPanel.querySelectorAll(`input[name="resolution-${CSS.escape(edge.id)}"]`).forEach((radio) => {
            radio.addEventListener("change", () => {
                const next = state.resolutionDrafts[edge.id] || { edge_id: edge.id, rationale: "", follow_up: "" };
                next.resolution_type = radio.value;
                state.resolutionDrafts[edge.id] = next;
                markDirty();
                renderTensions();
            });
        });
        dom.resolutionPanel.querySelector("[data-response-rationale]")?.addEventListener("input", (event) => {
            const next = state.resolutionDrafts[edge.id] || { edge_id: edge.id, resolution_type: "", follow_up: "" };
            next.rationale = event.target.value;
            state.resolutionDrafts[edge.id] = next;
            markDirty();
        });
        dom.resolutionPanel.querySelector("[data-response-follow-up]")?.addEventListener("input", (event) => {
            const next = state.resolutionDrafts[edge.id] || { edge_id: edge.id, resolution_type: "", rationale: "" };
            next.follow_up = event.target.value;
            state.resolutionDrafts[edge.id] = next;
            markDirty();
        });
        dom.resolutionPanel.querySelector("[data-apply-suggestion]")?.addEventListener("click", () => {
            const current = dom.revisedPlan.value.trim();
            const block = `\n\nDesign revision for ${edge.affected_party}:\n${edge.suggested_revision}`;
            if (!current.includes(edge.suggested_revision)) {
                dom.revisedPlan.value = `${current}${block}`;
                markDirty();
                updateRevisionStats();
                dom.revisedPlan.focus();
                toast("Proposed wording added", "It remains editable and is not saved until you choose to save.");
            }
        });
    }

    function markDirty() {
        state.dirty = true;
        dom.revisionSaveState.textContent = "Unsaved changes";
        dom.revisionSaveState.classList.add("is-dirty");
        dom.revisionSaveState.classList.remove("is-saved");
    }

    function markDraftChanged() {
        saveUnsavedDraft();
        updateCommitmentCount();
    }

    function markSaved() {
        state.dirty = false;
        dom.revisionSaveState.textContent = "Saved";
        dom.revisionSaveState.classList.remove("is-dirty");
        dom.revisionSaveState.classList.add("is-saved");
    }

    function tokenise(text) {
        return String(text || "").trim().split(/(\s+)/).filter(Boolean);
    }

    function simpleDiff(before, after) {
        const a = tokenise(before);
        const b = tokenise(after);
        if (a.length * b.length > 180000) {
            return {
                html: `<span class="diff-removed">${escapeHtml(shortText(before, 1000))}</span>\n\n<span class="diff-added">${escapeHtml(shortText(after, 1000))}</span>`,
                added: Math.max(0, b.length - a.length),
                removed: Math.max(0, a.length - b.length),
            };
        }
        const rows = a.length + 1;
        const cols = b.length + 1;
        const table = Array.from({ length: rows }, () => new Uint16Array(cols));
        for (let i = 1; i < rows; i += 1) {
            for (let j = 1; j < cols; j += 1) {
                table[i][j] = a[i - 1] === b[j - 1]
                    ? table[i - 1][j - 1] + 1
                    : Math.max(table[i - 1][j], table[i][j - 1]);
            }
        }
        const parts = [];
        let i = a.length;
        let j = b.length;
        let added = 0;
        let removed = 0;
        while (i > 0 || j > 0) {
            if (i > 0 && j > 0 && a[i - 1] === b[j - 1]) {
                parts.push({ type: "same", value: a[i - 1] });
                i -= 1;
                j -= 1;
            } else if (j > 0 && (i === 0 || table[i][j - 1] >= table[i - 1][j])) {
                parts.push({ type: "added", value: b[j - 1] });
                added += /\S/.test(b[j - 1]) ? 1 : 0;
                j -= 1;
            } else {
                parts.push({ type: "removed", value: a[i - 1] });
                removed += /\S/.test(a[i - 1]) ? 1 : 0;
                i -= 1;
            }
        }
        parts.reverse();
        return {
            html: parts.map((part) => (
                part.type === "same"
                    ? escapeHtml(part.value)
                    : `<span class="diff-${part.type}">${escapeHtml(part.value)}</span>`
            )).join(""),
            added,
            removed,
        };
    }

    function updateRevisionStats() {
        const before = state.session?.research_plan || dom.researchPlan.value || "";
        const after = dom.revisedPlan.value || before;
        dom.originalPlanView.textContent = before;
        const diff = simpleDiff(before, after);
        dom.planDiff.innerHTML = diff.html || "<span>No content</span>";
        if (!diff.added && !diff.removed) {
            dom.revisionStats.textContent = "Plan unchanged · a reasoned response is still valid";
        } else {
            dom.revisionStats.textContent = `${diff.added} words added · ${diff.removed} removed`;
        }
    }

    function getResolutionPayload() {
        return Object.values(state.resolutionDrafts)
            .filter((draft) => draft.resolution_type)
            .map((draft) => ({
                edge_id: draft.edge_id,
                decision: draft.resolution_type,
                resolution_type: draft.resolution_type,
                rationale: [
                    String(draft.rationale || "").trim(),
                    draft.follow_up ? `Follow-up evidence or action: ${String(draft.follow_up).trim()}` : "",
                ].filter(Boolean).join("\n"),
                follow_up: String(draft.follow_up || "").trim(),
            }));
    }

    async function saveRevisions(andReplay = false) {
        if (!state.session?.id) {
            toast("No saved session", "Build a consequence map before saving revisions.", "error");
            return;
        }
        const revisedPlan = dom.revisedPlan.value.trim();
        const resolutions = getResolutionPayload();
        if (!revisedPlan) {
            toast("Revised plan is empty", "Restore the original or enter a revised research design.", "error");
            return;
        }
        if (!resolutions.length && revisedPlan === state.session.research_plan.trim()) {
            toast(
                "Record one response first",
                "You do not have to edit the plan. Choose a response to a tension and explain why, or make a design change.",
                "error",
            );
            return;
        }
        setBusy(true);
        if (andReplay) {
            showLoading({
                eyebrow: "Counterfactual replay",
                title: "Running the same roles through the revised design…",
                detail: "Replay looks for resolved, transferred, and newly introduced concerns. It does not certify the revision.",
            });
        }
        try {
            const saved = await api(`/sessions/${encodeURIComponent(state.session.id)}/revisions`, {
                method: "POST",
                body: { revised_plan: revisedPlan, resolutions },
            });
            state.session = normaliseSession(unwrapSession(saved), state.session);
            state.session.revised_plan = revisedPlan;
            markSaved();
            if (andReplay) {
                advanceLoading(2);
                const replayed = await api(`/sessions/${encodeURIComponent(state.session.id)}/replay`, {
                    method: "POST",
                    body: { use_llm: true },
                });
                state.session = normaliseSession(unwrapSession(replayed), state.session);
                state.session.replayed_at = state.session.replayed_at || new Date().toISOString();
                syncSessionIntoUi();
                renderAll();
                navigateToStep(6, true);
                toast("Replay complete", "The change ledger now distinguishes recorded edits from tensions that remain open.");
            } else {
                renderTensions();
                renderLedger();
                updateProgress();
                toast("Responses saved", "Run replay when you are ready to compare the same scenarios.");
            }
        } catch (error) {
            toast(andReplay ? "Replay did not complete" : "Could not save responses", error.message, "error");
        } finally {
            if (andReplay) hideLoading();
            setBusy(false);
        }
    }

    function derivedLedger() {
        if (state.session?.ledger?.length) return state.session.ledger;
        const backendRevisions = asArray(state.session?.revisions);
        if (backendRevisions.length) {
            return backendRevisions.map((revision, index) => {
                const resolution = asArray(revision.resolutions)[0] || {};
                const edgeId = firstValue(
                    resolution.edge_id,
                    revision.edge_id,
                    revision.tension_id,
                    revision.path_id,
                    ""
                );
                const edge = state.session.dissonance_edges.find((item) => item.id === edgeId) || {};
                const replay = firstValue(revision.replay, revision.replay_result, {});
                const changes = asArray(revision.diff?.changes);
                const afterSnapshotPlan = revision.after_snapshot?.research_plan || "";
                const inserted = changes.flatMap((change) => asArray(change.after))
                    .map((value) => String(value || "").trim()).filter(Boolean).join(" ");
                const removed = changes.flatMap((change) => asArray(change.before))
                    .map((value) => String(value || "").trim()).filter(Boolean).join(" ");
                const decisionRaw = firstValue(
                    resolution.resolution_type,
                    resolution.decision,
                    revision.resolution_type,
                    revision.choice,
                    ""
                );
                const resolutionType = decisionRaw === "revise" ? "revise_design"
                    : decisionRaw === "consult_stakeholder" ? "consult_stakeholders"
                        : decisionRaw;
                const replaySummary = typeof replay === "object" ? replay.summary : null;
                const openEdges = Number(replaySummary?.open_edges);
                const resolvedEdges = Number(replaySummary?.resolved_edges);
                const changedLenses = Number(replaySummary?.changed_lens_count);
                const replayText = replaySummary && typeof replaySummary === "object"
                    ? [
                        Number.isFinite(changedLenses) ? `${changedLenses} lens${changedLenses === 1 ? "" : "es"} gained different evidence coverage` : "",
                        Number.isFinite(resolvedEdges) ? `${resolvedEdges} tension${resolvedEdges === 1 ? "" : "s"} resolved` : "",
                        Number.isFinite(openEdges) ? `${openEdges} remain open` : "",
                    ].filter(Boolean).join("; ") + ". Replay is evidence comparison, not proof that harm was prevented."
                    : firstValue(
                        typeof replay === "object" ? replay.outcome : "",
                        typeof replay === "string" ? replay : "",
                        "Revision saved; replay evidence was not available."
                    );
                const status = resolutionType === "contest_with_evidence" ? "contested"
                    : resolutionType === "consult_stakeholders" ? "open"
                        : revision.diff?.changed ? "changed" : "open";
                return normaliseLedger({
                    id: firstValue(revision.id, `revision_${index + 1}`),
                    edge_id: edgeId,
                    title: firstValue(revision.title, edge.consequence, `Revision record ${index + 1}`),
                    role: firstValue(revision.affected_party, edge.affected_party, ""),
                    before: firstValue(
                        removed,
                        edge.evidence,
                        "The original plan did not state the recorded safeguard or design change."
                    ),
                    after: firstValue(
                        inserted,
                        resolution.follow_up,
                        afterSnapshotPlan ? shortText(afterSnapshotPlan, 420) : "",
                        "No concise changed passage was recorded."
                    ),
                    response: firstValue(
                        resolution.rationale,
                        revision.rationale,
                        revision.response,
                        revision.researcher_response,
                        ""
                    ),
                    evidence: firstValue(
                        resolution.follow_up,
                        revision.follow_up,
                        revision.evidence,
                        revision.verification,
                        ""
                    ),
                    resolution_type: resolutionType,
                    status,
                    replay_outcome: replayText,
                    updated_at: firstValue(revision.updated_at, revision.created_at, state.session.updated_at, ""),
                }, index);
            });
        }
        const revisedPlan = state.session?.revised_plan || dom.revisedPlan.value || "";
        return getResolutionPayload().map((resolution, index) => {
            const edge = state.session.dissonance_edges.find((item) => item.id === resolution.edge_id) || {};
            const type = resolution.resolution_type;
            const status = type === "contest_with_evidence" ? "contested"
                : type === "consult_stakeholders" ? "open" : "changed";
            return normaliseLedger({
                id: resolution.edge_id,
                edge_id: resolution.edge_id,
                title: edge.consequence || `Response ${index + 1}`,
                role: edge.affected_party,
                before: edge.evidence,
                after: type === "revise_design" || type === "add_safeguard"
                    ? shortText(revisedPlan, 330)
                    : resolution.follow_up,
                response: resolution.rationale,
                evidence: resolution.follow_up,
                resolution_type: type,
                status,
                replay_outcome: state.session?.replayed_at
                    ? "Replay completed; inspect the current scenarios and coverage for remaining uncertainty."
                    : "Response saved. Replay has not yet tested this change.",
                updated_at: state.session?.updated_at,
            }, index);
        });
    }

    function renderLedger() {
        const ledger = derivedLedger();
        const revisions = getResolutionPayload();
        const changed = ledger.filter((record) => record.status === "changed");
        const addressed = ledger.filter((record) => Boolean(record.response || record.resolution_type));
        const open = ledger.filter((record) => record.status === "open");
        const latestReplaySummary = [...asArray(state.session?.revisions)]
            .reverse()
            .find((revision) => revision?.replay?.summary)?.replay?.summary;
        const openCount = Number.isFinite(Number(latestReplaySummary?.open_edges))
            ? Number(latestReplaySummary.open_edges)
            : open.length;
        const actionLinked = (state.session?.lenses || []).filter((lens) => lens.status === "action-linked");
        dom.metricChanges.textContent = String(changed.length);
        dom.metricAddressed.textContent = String(addressed.length || revisions.length);
        dom.metricOpen.textContent = String(openCount);
        dom.metricActionLinked.textContent = String(actionLinked.length);
        const timestamp = firstValue(state.session?.replayed_at, state.session?.updated_at, "");
        dom.ledgerTimestamp.textContent = timestamp
            ? `Last updated ${formatDate(timestamp)}`
            : "No replay recorded";

        const visible = ledger.filter((record) => state.ledgerFilter === "all" || record.status === state.ledgerFilter);
        dom.ledgerEmpty.hidden = ledger.length > 0;
        dom.ledgerList.hidden = !ledger.length;
        dom.ledgerList.innerHTML = visible.map((record) => {
            const responseLabel = RESOLUTION_TYPES[record.resolution_type]?.label || titleCase(record.status);
            return `
                <article class="ledger-record">
                    <header class="ledger-record-header">
                        <div>
                            <h3>${escapeHtml(record.title)}</h3>
                            <p>${escapeHtml(record.role || "Affected position not specified")} · ${escapeHtml(responseLabel)}</p>
                        </div>
                        <span class="ledger-status ${record.status}">${escapeHtml(record.status)}</span>
                    </header>
                    <div class="ledger-compare">
                        <div class="ledger-version">
                            <span>Before · plan evidence</span>
                            <p>${escapeHtml(record.before || "No exact original passage was linked.")}</p>
                        </div>
                        <div class="ledger-version">
                            <span>After · response or revision</span>
                            <p>${escapeHtml(record.after || record.response || "No revised evidence recorded.")}</p>
                        </div>
                    </div>
                    ${(record.response || record.evidence) ? `
                        <div class="ledger-reasoning">
                            ${record.response ? `<p><strong>Researcher reasoning</strong>${escapeHtml(record.response)}</p>` : ""}
                            ${record.evidence ? `<p><strong>Follow-up evidence or action</strong>${escapeHtml(record.evidence)}</p>` : ""}
                        </div>
                    ` : ""}
                    <footer class="ledger-record-footer">
                        <span>${escapeHtml(record.replay_outcome || "This record preserves the response without claiming the tension is resolved.")}</span>
                        <span>${record.updated_at ? escapeHtml(formatDate(record.updated_at)) : "researcher-authored"}</span>
                    </footer>
                </article>
            `;
        }).join("");
        if (ledger.length && !visible.length) {
            dom.ledgerList.innerHTML = `
                <div class="empty-state">
                    <span aria-hidden="true">◌</span>
                    <h3>No records match this filter</h3>
                    <p>Choose another outcome state.</p>
                </div>`;
        }
    }

    function formatDate(value) {
        try {
            const date = new Date(value);
            if (Number.isNaN(date.getTime())) return String(value);
            return new Intl.DateTimeFormat(undefined, {
                month: "short",
                day: "numeric",
                hour: "2-digit",
                minute: "2-digit",
            }).format(date);
        } catch {
            return String(value || "");
        }
    }

    function downloadBundle() {
        if (!state.session) {
            toast("No session to download", "Build a mirror first.", "error");
            return;
        }
        const bundle = {
            schema: "safebars-ethical-mirror-study-bundle-v1",
            exported_at: new Date().toISOString(),
            boundary_notice: state.session.boundary_notice || "Synthetic scenarios are hypotheses, not stakeholder testimony or institutional approval.",
            session_id: state.session.id,
            title: state.session.title,
            research_plan_before: state.session.research_plan,
            value_commitments: state.session.value_commitments,
            literature_lenses: state.session.lenses,
            synthetic_scenarios: state.session.scenarios,
            dissonance_paths: state.session.dissonance_edges,
            researcher_responses: getResolutionPayload(),
            research_plan_after: state.session.revised_plan || dom.revisedPlan.value,
            before_after_ledger: derivedLedger(),
            literature_registry: state.literature,
        };
        const blob = new Blob([JSON.stringify(bundle, null, 2)], { type: "application/json" });
        const url = URL.createObjectURL(blob);
        const anchor = document.createElement("a");
        anchor.href = url;
        anchor.download = `safebars-mirror-${slug(state.session.title, state.session.id)}.json`;
        document.body.appendChild(anchor);
        anchor.click();
        anchor.remove();
        URL.revokeObjectURL(url);
        toast("Study bundle downloaded", "The JSON preserves sources, model hypotheses, researcher choices, and unresolved questions separately.");
    }

    function updateProgress() {
        const hasSession = Boolean(state.session?.id);
        const hasAnalysis = Boolean(
            state.session?.analyzed_at
            || state.session?.lenses?.length
            || state.session?.scenarios?.length
            || state.session?.dissonance_edges?.length
        );
        const hasScenarios = Boolean(state.session?.scenarios?.length);
        const hasEdges = Boolean(state.session?.dissonance_edges?.length);
        const hasResponses = Boolean(getResolutionPayload().length || state.session?.revisions?.length);
        const hasLedger = Boolean(state.session?.ledger?.length || hasResponses);
        const unlocked = {
            1: true,
            2: hasSession,
            3: hasAnalysis,
            4: hasEdges || hasScenarios,
            5: hasEdges,
            6: hasLedger,
        };
        const complete = {
            1: hasSession,
            2: Boolean(state.session?.lenses?.length),
            3: hasScenarios,
            4: hasEdges,
            5: hasResponses,
            6: Boolean(state.session?.ledger?.length || state.session?.replayed_at),
        };
        dom.stepNavItems.forEach((button) => {
            const step = Number(button.dataset.stepTarget);
            button.setAttribute("aria-disabled", String(!unlocked[step]));
            button.classList.toggle("is-complete", complete[step]);
            button.classList.toggle("is-active", step === state.activeStep);
            if (step === state.activeStep) button.setAttribute("aria-current", "step");
            else button.removeAttribute("aria-current");
        });
    }

    function canNavigateTo(step) {
        const button = dom.stepNavItems.find((item) => Number(item.dataset.stepTarget) === step);
        return button && button.getAttribute("aria-disabled") !== "true";
    }

    function navigateToStep(step, force = false) {
        const target = clamp(step, 1, 6);
        if (!force && !canNavigateTo(target)) {
            toast("Complete the earlier step first", "The next workspace opens when its evidence is available.", "error");
            return;
        }
        state.activeStep = target;
        dom.stepPanels.forEach((panel) => {
            const active = Number(panel.dataset.stepPanel) === target;
            panel.hidden = !active;
            panel.classList.toggle("is-active", active);
        });
        updateProgress();
        if (target === 2) renderLenses();
        if (target === 3) renderScenarios();
        if (target === 4) window.setTimeout(renderGraph, 30);
        if (target === 5) {
            dom.revisedPlan.value = state.session?.revised_plan || state.session?.research_plan || "";
            renderTensions();
            updateRevisionStats();
        }
        if (target === 6) renderLedger();
        document.querySelector(`[data-step-panel="${target}"]`)?.scrollIntoView({ block: "start" });
        dom.workspace.focus({ preventScroll: true });
    }

    function setLensFilter(filter) {
        state.lensFilter = filter;
        document.querySelectorAll("[data-lens-filter]").forEach((button) => {
            button.classList.toggle("is-active", button.dataset.lensFilter === filter);
        });
        renderLenses();
    }

    function setLedgerFilter(filter) {
        state.ledgerFilter = filter;
        document.querySelectorAll("[data-ledger-filter]").forEach((button) => {
            button.classList.toggle("is-active", button.dataset.ledgerFilter === filter);
        });
        renderLedger();
    }

    function setEditorView(view) {
        state.editorView = view;
        document.querySelectorAll("[data-editor-view]").forEach((button) => {
            const active = button.dataset.editorView === view;
            button.classList.toggle("is-active", active);
            button.setAttribute("aria-selected", String(active));
        });
        document.querySelectorAll("[data-editor-panel]").forEach((panel) => {
            const active = panel.dataset.editorPanel === view;
            panel.hidden = !active;
            panel.classList.toggle("is-active", active);
        });
        if (view === "diff") updateRevisionStats();
    }

    function loadGuidedExample() {
        if (state.session && !window.confirm("Start a new guided conversation with the example? Your saved session will remain on the server.")) return;
        if (state.session) resetLocalState(false);
        state.intakeAnswers = { ...GUIDED_EXAMPLE.answers };
        state.intakeIndex = activeIntakeQuestions().length - 1;
        state.intakeComplete = true;
        if (dom.intakeOptionalContext) dom.intakeOptionalContext.value = "";
        syncIntakePayload();
        renderIntake();
        navigateToStep(1, true);
        toast("Guided example loaded", "The completed conversation trail can be edited before you build the mirror.");
    }

    function resetLocalState(confirmFirst = true) {
        if (confirmFirst && state.session && !window.confirm("Start a new Ethical Mirror? The saved session will remain on the server, but this browser will stop tracking it.")) return;
        state.session = null;
        state.activeStep = 1;
        state.selectedScenarioId = null;
        state.selectedEdgeId = null;
        state.selectedTensionId = null;
        state.resolutionDrafts = {};
        state.dirty = false;
        state.intakeAnswers = {};
        state.intakeIndex = 0;
        state.intakeComplete = false;
        localStorage.removeItem(STORAGE_KEY);
        localStorage.removeItem(DRAFT_KEY);
        dom.projectTitle.value = "";
        dom.researchPlan.value = "";
        setCommitments([""]);
        if (dom.intakeOptionalContext) dom.intakeOptionalContext.value = "";
        dom.revisedPlan.value = "";
        dom.originalPlanView.textContent = "";
        dom.sessionLabel.textContent = "Unsaved research plan";
        dom.planValidation.textContent = "";
        dom.revisionSaveState.textContent = "Not yet saved";
        dom.revisionSaveState.classList.remove("is-dirty", "is-saved");
        updatePlanSignals();
        renderIntake();
        renderAll();
        navigateToStep(1, true);
    }

    function openDialog(dialog, focusId = "") {
        if (!dialog) return;
        if (typeof dialog.showModal === "function") dialog.showModal();
        else dialog.setAttribute("open", "");
        if (focusId) {
            window.setTimeout(() => document.getElementById(focusId)?.scrollIntoView({ block: "center" }), 80);
        }
    }

    function toast(title, detail = "", type = "success") {
        const item = document.createElement("div");
        item.className = `toast ${type === "error" ? "is-error" : ""}`;
        item.innerHTML = `
            <i aria-hidden="true"></i>
            <span><strong>${escapeHtml(title)}</strong>${detail ? `<small>${escapeHtml(detail)}</small>` : ""}</span>
            <button type="button" aria-label="Dismiss notification">×</button>
        `;
        const remove = () => {
            item.style.opacity = "0";
            item.style.transform = "translateY(5px)";
            window.setTimeout(() => item.remove(), 180);
        };
        item.querySelector("button").addEventListener("click", remove);
        dom.toastRegion.appendChild(item);
        window.setTimeout(remove, type === "error" ? 7000 : 4800);
    }

    function bindEvents() {
        dom.planForm.addEventListener("submit", createAndAnalyse);
        dom.intakeNextBtn.addEventListener("click", saveCurrentIntakeAnswer);
        dom.intakeBackBtn.addEventListener("click", () => {
            if (state.intakeIndex <= 0) return;
            state.intakeIndex -= 1;
            state.intakeComplete = false;
            dom.planValidation.textContent = "";
            renderIntake();
        });
        dom.intakeWhyBtn.addEventListener("click", () => {
            const expanded = dom.intakeWhyBtn.getAttribute("aria-expanded") === "true";
            dom.intakeWhyBtn.setAttribute("aria-expanded", String(!expanded));
            dom.intakeWhy.hidden = expanded;
        });
        dom.intakeTextInput.addEventListener("input", () => {
            dom.intakeCharCount.textContent = String(dom.intakeTextInput.value.length);
            dom.planValidation.textContent = "";
            if (!state.intakeComplete) dom.intakeBuildActions.hidden = true;
        });
        dom.intakeTextInput.addEventListener("keydown", (event) => {
            if (event.key === "Enter" && (event.ctrlKey || event.metaKey)) {
                event.preventDefault();
                saveCurrentIntakeAnswer();
            }
        });
        dom.intakeOptionalContext.addEventListener("input", () => {
            syncIntakePayload();
            saveUnsavedDraft();
        });
        dom.addCommitmentBtn.addEventListener("click", () => {
            const input = addCommitment("");
            input?.focus();
            markDraftChanged();
        });
        [...dom.commitmentList.querySelectorAll("[data-commitment-row]")].forEach(bindCommitmentRow);

        document.querySelectorAll("[data-commitment-prompt]").forEach((button) => {
            button.addEventListener("click", () => {
                const prompt = button.dataset.commitmentPrompt;
                const empty = [...dom.commitmentList.querySelectorAll("[data-commitment-input]")]
                    .find((input) => !input.value.trim());
                const target = empty || addCommitment("");
                if (target) {
                    target.value = prompt;
                    target.dispatchEvent(new Event("input", { bubbles: true }));
                    target.focus();
                }
            });
        });

        dom.stepNav.addEventListener("click", (event) => {
            const button = event.target.closest("[data-step-target]");
            if (button) navigateToStep(Number(button.dataset.stepTarget));
        });
        document.addEventListener("click", (event) => {
            const goButton = event.target.closest("[data-go-step]");
            if (goButton) navigateToStep(Number(goButton.dataset.goStep));
        });

        document.querySelectorAll("[data-lens-filter]").forEach((button) => {
            button.addEventListener("click", () => setLensFilter(button.dataset.lensFilter));
        });
        document.querySelectorAll("[data-ledger-filter]").forEach((button) => {
            button.addEventListener("click", () => setLedgerFilter(button.dataset.ledgerFilter));
        });
        document.querySelectorAll("[data-map-mode]").forEach((button) => {
            button.addEventListener("click", () => {
                state.mapMode = button.dataset.mapMode;
                document.querySelectorAll("[data-map-mode]").forEach((item) => item.classList.toggle("is-active", item === button));
                renderGraph();
            });
        });
        document.querySelectorAll("[data-editor-view]").forEach((button) => {
            button.addEventListener("click", () => setEditorView(button.dataset.editorView));
        });

        dom.scenarioSort.addEventListener("change", () => {
            state.scenarioSort = dom.scenarioSort.value;
            renderScenarios();
        });
        dom.reanalyzeBtn.addEventListener("click", runAnalysis);
        dom.revisedPlan.addEventListener("input", () => {
            markDirty();
            updateRevisionStats();
        });
        dom.restoreOriginalBtn.addEventListener("click", () => {
            if (!state.session) return;
            if (!window.confirm("Replace the revised text with the original research plan?")) return;
            dom.revisedPlan.value = state.session.research_plan;
            markDirty();
            updateRevisionStats();
        });
        dom.saveRevisionBtn.addEventListener("click", () => saveRevisions(false));
        dom.replayBtn.addEventListener("click", () => saveRevisions(true));
        dom.downloadBundleBtn.addEventListener("click", downloadBundle);
        dom.printLedgerBtn.addEventListener("click", () => window.print());

        dom.zoomOutBtn.addEventListener("click", () => {
            state.graphScale = clamp(state.graphScale - .1, .65, 1.45);
            applyGraphScale();
        });
        dom.zoomInBtn.addEventListener("click", () => {
            state.graphScale = clamp(state.graphScale + .1, .65, 1.45);
            applyGraphScale();
        });
        dom.fitGraphBtn.addEventListener("click", () => {
            state.graphScale = 1;
            dom.graphWrap.scrollTo({ top: 0, left: 0, behavior: "smooth" });
            applyGraphScale();
        });

        dom.openLiteratureBtn.addEventListener("click", () => openDialog(dom.literatureDialog));
        dom.showMethodBtn.addEventListener("click", () => openDialog(dom.methodDialog));
        dom.methodTopBtn.addEventListener("click", () => openDialog(dom.methodDialog));
        dom.boundaryDetailsBtn.addEventListener("click", () => openDialog(dom.boundaryDialog));
        document.querySelectorAll("[data-close-dialog]").forEach((button) => {
            button.addEventListener("click", () => button.closest("dialog")?.close());
        });
        [dom.literatureDialog, dom.methodDialog, dom.boundaryDialog].forEach((dialog) => {
            dialog.addEventListener("click", (event) => {
                if (event.target === dialog) {
                    const rect = dialog.getBoundingClientRect();
                    const inside = event.clientX >= rect.left && event.clientX <= rect.right
                        && event.clientY >= rect.top && event.clientY <= rect.bottom;
                    if (!inside) dialog.close();
                }
            });
        });

        dom.loadExampleBtn.addEventListener("click", loadGuidedExample);
        dom.startOverBtn.addEventListener("click", () => resetLocalState(true));
        dom.newMirrorBtn.addEventListener("click", () => resetLocalState(true));
        dom.retryConnectionBtn.addEventListener("click", async () => {
            await loadConfiguration();
            if (state.lastConnectionOk) toast("Connection restored", "The SafeBARS service is ready.");
        });
        dom.resumeBtn.addEventListener("click", () => {
            const id = localStorage.getItem(STORAGE_KEY);
            if (id) restoreSession(id);
        });

        window.addEventListener("beforeunload", (event) => {
            if (!state.dirty) return;
            event.preventDefault();
            event.returnValue = "";
        });
    }

    async function init() {
        cacheDom();
        bindEvents();
        setCommitments([""]);
        renderIntake();
        updatePlanSignals();
        renderLiterature();
        renderAll();
        updateProgress();
        await loadConfiguration();
        const querySession = new URLSearchParams(window.location.search).get("session");
        const savedSession = querySession || localStorage.getItem(STORAGE_KEY);
        if (savedSession) {
            dom.resumeBtn.hidden = false;
            await restoreSession(savedSession, false);
        } else {
            loadUnsavedDraft();
        }
    }

    document.addEventListener("DOMContentLoaded", init);
})();
