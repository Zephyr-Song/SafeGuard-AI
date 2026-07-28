# SafeBARS Study Materials

Status: draft research package for institutional review, supervisor approval,
dry runs, and preregistration. These files are **not yet approved participant
materials**.

No participant or expert data may be collected until the institution has
issued a written approval, exemption, or other determination covering the
actual protocol, external LLM data flow, logging, compensation, retention, and
withdrawal procedure.

## Canonical design

- `../CURRENT_CANONICAL_PLAN.md`
- `../86_evalLM_blueprint_final_rqs.md`
- `../88_final_comparative_study_protocol.md`
- `../90_blinded_artifact_quality_rubric.md`

## Materials in this directory

- `shared_task_instruction.md`: condition-neutral participant task;
- `formative_interview_guide.md`: six-person requirements check;
- `post_task_questionnaire.md`: frozen item families requiring final wording
  and approved presentation;
- `expert_triage_task.md`: expert packet-rating and triage procedure;
- `study_assignment_schedule.csv`: pseudonymous 24-participant,
  eight-sequence allocation;
- `study_assignment_schedule.manifest.json`: seed and balance audit.

The assignment files contain no names, emails, recruitment contacts, or
outcomes. Regenerate them with:

```powershell
python scripts/generate_safebars_study_schedule.py
```

## Still institution-specific

The following cannot be made final without the supervisor and institutional
ethics route:

- participant information sheet;
- consent form;
- expert information and consent;
- recruitment message and screening form;
- compensation statement;
- data controller and contact details;
- external model-provider disclosure;
- retention, deletion, and withdrawal dates;
- incident and complaint procedure; and
- approval or exemption reference.

Do not reuse the older synthetic-stakeholder participant materials.
