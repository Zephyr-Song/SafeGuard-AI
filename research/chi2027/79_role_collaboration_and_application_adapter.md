# SafeBARS Role Collaboration and Application Adapter

## Outcome

The local prototype now implements one complete three-party review loop:

1. a researcher creates a protocol session and receives separate researcher and expert capability tokens;
2. the researcher shares the expert-only invitation;
3. an expert advises, requests clarification, redirects, resolves, or reopens a handoff;
4. the researcher links a response and exact revised protocol text to that handoff;
5. the expert can inspect the revision and close the issue;
6. SafeBARS preserves the review record and requires a new protocol version before rerunning the audit.

Researchers can resume the current protocol after a page refresh in the same browser session. Experts who open multiple invitations receive a browser-local caseload that summarizes unresolved, high-priority, and resolved handoffs across those invited protocols.

## Authorization Model

Raw capability tokens are returned only when a session or invitation is created. SQLite stores SHA-256 token hashes, not raw tokens. Researcher and expert endpoints enforce different permissions when `SAFEBARS_REQUIRE_ROLE_AUTH=1`.

The expert token is transferred in the URL fragment, read into browser session storage, and removed from the visible address. It is sent to the API in the `X-SafeBARS-Access` header. Export downloads also use the header rather than putting the token in a query string.

This is suitable for prototype validation, not production institutional use. A deployment handling real confidential applications still needs institution-managed identity, account recovery, case assignment, audit administration, retention and deletion policy, encryption review, and security testing.

## Application Profiles

Two non-official adapters are available:

- Generic human-research application;
- Generic AI-enabled human-research application.

The AI profile adds prompts for AI role and disclosure, human oversight, data/model governance, and failure, contestability, and redress. Every field is classified as documented, partial, or missing using visible evidence and minimum completeness checks.

The resulting percentage measures documentation coverage only. It is not an ethical score, compliance decision, or approval prediction.

## Versioning Rule

Once a human decision, expert review, or researcher revision exists, SafeBARS blocks map changes and full audit reruns that would overwrite the record. The researcher can create a new protocol version, which copies source materials into a new session while preserving the parent review.

## Implemented Endpoints

- session creation returns researcher and expert tokens;
- researcher-only session, map, plan, audit, decision, response, version, and application-export routes;
- expert-only summary, review, and expert-export routes;
- researcher-only expert-invitation rotation;
- application-profile selection and readiness state.

## Remaining Work

1. obtain one current university ethics form and build a field-by-field official adapter;
2. add participant information sheet and consent-form generators;
3. replace capability-only access and the browser-local caseload with institution-managed accounts and a server-side multi-case expert dashboard;
4. add notification delivery and deadlines without exposing protocol content in email;
5. persist trade-off rationales and connect them to application revisions;
6. validate profile fields, routing rules, and stopping rules with real ethics and governance experts.
