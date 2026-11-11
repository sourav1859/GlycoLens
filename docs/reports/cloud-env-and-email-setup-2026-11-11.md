# Cloud environment and email setup - November 11, 2026

## Follow-up: GPT-6 Luna selected and smoke-validated

The user subsequently selected `gpt-6-luna` and approved USD 5 total live testing.
The private environment and public template were updated without changing other
values or exposing the API key. Read-only model discovery and 16 bounded synthetic
inference calls verified access; both models passed eight cases after a documented
offline oracle correction. Estimated combined charges were USD 0.00763580.
Seventeen offline checks passed. See the [model validation report](recipe-model-validation-2026-11-11.md)
for raw/scored evidence and limits. The earlier GPT-5 mini and unapproved-budget
statements below describe initial preparation and are superseded by this follow-up;
representative accuracy/full application acceptance remain open.

## Follow-up: development Auth settings verified

After the user reported disabling confirmation, a read-only cloud Auth settings
request returned HTTP 200 with `external.email=true`, `disable_signup=false` and
`mailer_autoconfirm=true`. The saved publishable key and exact cloud target guard
were used; response/credential values outside these settings were not logged.
The sandbox's network restriction blocked the first request; the approved
read-only retry outside that restriction succeeded.

The agent did not create test accounts, send emails or change hosted settings.
This proves that automatic-confirmation development Auth is configured, not that
application signup/login, sessions or RLS pass. SMTP is deferred during development;
real verification/recovery delivery remains a public-release gate. The phase test
ledger remains unchanged and no full acceptance case is marked passed.

The earlier email-provider discussion below is historical preparation. Resend
remains an option when a domain is available; Mailtrap was discussed as an optional
test sandbox but was not configured. Neither is needed to start development under
the user's temporary automatic-confirmation setting.

## Scope and observed configuration

The user requested saving development credentials and help with email delivery.
Only ignored root `.env` and `frontend/.env.local` contain credential values.
The cloud target is `Glycolens`, ref `ecynkzptuslkuhjikzfc`, region `us-west-2`.
Authenticated MCP project discovery, table inventory and a read-only schema query
worked earlier in this session; `public` contained no tables. This does not prove
runtime API-key acceptance, permanent Auth, user isolation or schema deployment.

- Root configuration: cloud URL, modern publishable key under the existing
  `SUPABASE_ANON_KEY` name, private `SUPABASE_SECRET_KEY`, OpenAI extraction key,
  `LLM_MODEL=gpt-5-mini` and USDA key. The stale legacy service-role value was cleared.
- Browser configuration: cloud URL and publishable key only. Existing unrelated
  configuration was preserved; no private provider/backend key was copied there.
- Read-back verified updated values without printing them. Git confirmed both
  environment files are ignored. The committed examples contain no real keys.
- Because secret values were supplied in chat, rotate them through their provider
  dashboards and replace values directly in private configuration. Rotation was
  not performed automatically.

## Runtime change and checks

Trusted provider food caching prefers the modern secret key on the `apikey` header,
without using it as a JWT. Legacy-only configuration retains its bearer header.
Ordinary user-token calls and RLS behavior were not changed.

Requirement mapping: modern key preference/no JWT header; legacy compatibility;
whitespace fallback; missing credentials fail before HTTP and remain redacted.
All tests use synthetic values and mocked HTTP, not real credentials or patient data.

| Check | Observed result |
|---|---|
| New key tests before the fix | 1 failed, 3 passed; modern preference failed as expected |
| `python -m pytest backend/tests/test_supabase_admin_keys.py backend/tests/test_m2_nutrition.py -q` | 8 passed |
| `python -m ruff check backend/app/services/nutrition/providers.py backend/tests/test_supabase_admin_keys.py` | Passed |
| `python -m ruff format --check backend/app/services/nutrition/providers.py backend/tests/test_supabase_admin_keys.py` | Passed |
| Environment read-back, private/browser separation, Git ignore | Passed; values omitted |
| Credential-free tracked diff/new setup files and relative documentation links | Passed |
| Cloud Auth/RLS, schema application, USDA/OpenAI live requests, SMTP delivery | Not run |

The sandbox could not access the existing base Python installation; focused
offline Python checks passed with approved execution outside that restriction.
No paid call, Auth email, database write, migration, deployment or key rotation ran.
The 144-case phase ledger remains unchanged; these checks do not close P00/P01/P03/P04.
Graphify was available at the start and final review. Its code-only update needs
no LLM; semantic document extraction was not enabled because no backend approval
was supplied. The setup evidence and source files remain authoritative.

## Email and remaining gates

The user confirmed there is no SMTP provider and no domain yet. The
[cloud setup guide](../tooling/cloud-supabase-setup.md#email-setup-while-the-domain-is-pending)
documents proposed Resend account/domain verification and field-by-field values.
No SMTP credentials exist in this handoff and no external email settings changed.
General-user delivery remains blocked on provider/domain readiness and actual
controlled inbox tests; limited default Supabase email has team-address restrictions.

OpenAI model access and paid-test request/spending cap remain unverified/unapproved.
The selected `gpt-5-mini` API ID is preserved; official
[deprecations](https://developers.openai.com/api/docs/deprecations) list December 11,
2026 shutdown. Choose any replacement explicitly before release; it was not switched.
Corrected catalog, VPS/domain, scratch replay/restore and full phase acceptance
remain separate pending prerequisites.

Planning 00/01/04/17, AGENTS.md, cloud setup and root/backend/frontend READMEs were
updated for configuration/key handling and the selected parser model. Product UX,
research/forecasting protocols, medical boundaries and phase milestone completion
were unchanged; their acceptance was not reclassified.
