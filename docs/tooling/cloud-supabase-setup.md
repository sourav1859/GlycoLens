# Cloud Supabase setup and prerequisite handoff

## Verified preparation - November 11, 2026

The dedicated `Glycolens` project (`ecynkzptuslkuhjikzfc`, `us-west-2`) is
reachable through authenticated MCP; its `public` schema was empty at inspection.
The cloud URL and active publishable key are saved in ignored root `.env` and
`frontend/.env.local`. The private backend secret, OpenAI key/model and USDA key
are saved only in root `.env`; unrelated existing configuration was preserved.
No key values belong in this guide or test output.

The backend prefers `SUPABASE_SECRET_KEY` on `apikey` without a bearer JWT for
trusted food caching. A legacy `SUPABASE_SERVICE_ROLE_KEY` remains a fallback,
and its old local value was cleared from the current private cloud configuration.
The existing `SUPABASE_ANON_KEY` / `NEXT_PUBLIC_SUPABASE_ANON_KEY` names accept the
modern publishable key. See root and frontend `.env.example` for public templates.

The user selected `LLM_MODEL=gpt-6-luna`, replacing the initial `gpt-5-mini`
setting. Both ignored root `.env` and committed `.env.example` use the selected
model. The existing Responses API strict JSON schema remains compatible with the
documented [GPT-6 Luna capabilities](https://developers.openai.com/api/docs/models/gpt-6-luna).
The user approved USD 5 total live testing. A bounded 16-call smoke comparison
verified inference access and token usage, with estimated combined charges of
USD 0.00763580. Both models passed eight synthetic cases after a documented
offline scoring correction; representative accuracy and production cost are
unproven. Account for prior spend before further paid calls. See the
[recipe validation report](../reports/recipe-model-validation-2026-11-11.md).
Nutrition facts still come from validated providers.
Eight focused offline tests passed; see [setup evidence](../reports/cloud-env-and-email-setup-2026-11-11.md).
Hosted schema, cloud-user RLS, live providers and real email delivery remain open.

## Temporary development Auth configuration - November 11, 2026

The user disabled email confirmation in the dedicated development project. A
read-only request to the cloud Auth `/auth/v1/settings` endpoint, using the saved
publishable key and an exact project-URL guard, succeeded and returned:

- Email/password authentication enabled: `external.email=true`.
- Public signup enabled: `disable_signup=false`.
- Automatic email confirmation enabled: `mailer_autoconfirm=true`.

This permits development signup/login without verification emails or custom SMTP.
The agent did not change cloud settings, create accounts, send messages or apply
schema. The check proves configuration and public-key access, not the application's
registration/login routes, session lifecycle or user-data isolation.

SMTP/domain setup can remain deferred while the application is developed. The
Resend instructions below apply when real email delivery is prepared. Email
ownership is unverified in this temporary configuration; verification and recovery
delivery must be enabled/tested before public release. Do not promote this development
exception into production or mark the email acceptance cases passed.

**Current project preference, November 10, 2026:** dedicated managed cloud Supabase
for application DB/Auth and integration acceptance. Local web/API processes can
connect to it. A local Supabase stack is not required by the new workflow.
See [ADR 0018](../decisions/0018-cloud-supabase-and-staged-webapp-delivery.md) and
the [implementation plan prerequisites](../planning/GlycoLens_17_Webapp_Implementation_Plan.md#2-prerequisites-and-information-needed-from-the-user).

## Prepare the initial information

1. Create or identify the dedicated development project in the user's Supabase
   account. Record its non-secret name/ref, region, URL and quota/plan status. Do
   not reuse a project containing unrelated application data without inventory.
2. Obtain the project public publishable key and backend secret key from its API
   key settings, or identify compatible legacy anon/service-role keys. Key types
   must be tested against the current SDK and raw REST adapter before use.
3. Use one reviewed migration path: the authenticated MCP connection can apply
   migrations while retaining SQL under `supabase/migrations/`. CLI login/link
   plus DB password or TLS connection credentials are alternatives, needed only
   if selected. API keys are not database passwords. An account password/JWT
   signing secret is not an application prerequisite.
4. Configure privately: server `.env`, client `frontend/.env.local`, and protected
   deployment/CI stores. Current browser names are `NEXT_PUBLIC_SUPABASE_URL` and
   `NEXT_PUBLIC_SUPABASE_ANON_KEY`; current server names include `SUPABASE_URL`,
   `SUPABASE_ANON_KEY` and preferred `SUPABASE_SECRET_KEY`; legacy
   `SUPABASE_SERVICE_ROLE_KEY` is a fallback. P00/P01 must verify remaining admin
   paths and application/RLS behavior; no modern key should be treated as a JWT.
5. Confirm local frontend/API origins and callback paths, then configure cloud
   email/password, confirmation/recovery, Site URL/redirect allowlist and suitable
   SMTP sender/inboxes. Record SMTP credentials in Supabase/private configuration,
   not application source. General-user email delivery must be tested.
6. Add `LLM_API_KEY`/`LLM_MODEL`, approved LLM budget, USDA key and Open Food Facts
   identification when P04 live checks are ready. These are not prerequisites to
   draft the UI or establish basic cloud/Auth connectivity.

Secret values belong in ignored/private configuration, not chat, Markdown, JSON
results, screenshots or Git. Only non-secret identifiers and setup status need to
be shared conversationally. No values were populated by preparing this guide.

## Controlled schema and connection workflow

- P00 verifies tools/versions, exact project identity and safe harness configuration.
- P01 first inventories managed/existing schemas, migration history, exposed APIs,
  extensions and capacity through read-only access.
- Review the four existing migration files and proposed forward changes for the
  dedicated target. Keep `public.users` linked to managed Auth, preserve RLS and
  redesign derived-write authority without breaking transaction functions.
- Preview changes using the installed pinned CLI's supported explicit hosted-target
  flags, then apply through one controlled migration path. CLI major versions have
  different defaults/flags; do not run an ambiguous command copied from another version.
- Verify schema/history, keys, Auth user verification, user-token REST/RPC access,
  A/B isolation and trusted-write denials. Run tagged synthetic fixtures and scoped
  cleanup. A working admin SQL connection does not prove browser RLS correctness.
- Record expected/actual results and sanitized evidence under the test-case IDs.
  Scratch replay/restore needs a separate approved cloud target; use no hosted reset.

The intended application schema is created by these reviewed migrations, not a
manual dashboard-only table setup. No cloud schema/connection exists merely because
the guide and migration files exist.

## Historical tooling to avoid for the new workflow

`scripts/dev/Configure-LocalDemo.ps1` writes local project keys into ignored app
configuration. `scripts/database/Test-LocalSupabase.ps1` starts/resets the local
stack. They are retained historical tools and must not be used to establish or
validate the new cloud connection. Existing checks named `--allow-live-local` and
Windows-specific Playwright launch settings must be adapted deliberately; they are
not cloud-safe just because environment URLs are changed.

New cloud preflight/test runners are planned in P00/P01 and do not exist yet.
Offline unit/contract tests remain valid where relevant; their success does not
replace real hosted database/Auth, email/provider, model or physical camera evidence.

## Email setup while the domain is pending

The user has no SMTP provider or DNS-managed domain yet. Resend is the proposed
provider; no account was created, no purchase authorized and no SMTP settings
were changed. Keep custom SMTP disabled until valid provider settings are ready.
Supabase's default service is restricted to project-team addresses and low rate
limits; it cannot close general-user email acceptance.

1. Create a Resend account and obtain a domain whose DNS you control.
2. Add a sending domain/subdomain in Resend, publish its required DNS records and
   wait for verification. Use the provider's generated records, not guessed values.
3. Create a Resend sending API key privately and configure Supabase's SMTP form:

| Supabase field | Resend value |
|---|---|
| Sender email address | An address at the verified sending domain, such as `noreply@auth.example.com` |
| Sender name | `GlycoLens` |
| Host | `smtp.resend.com` |
| Port | `465` |
| Username | `resend` |
| Password | Resend API key, entered privately in Supabase |

4. Save only when the domain and all credentials are ready. Keep email confirmation
   enabled. Match the development Site URL to `http://localhost:3000` and add exact
   verification/recovery callbacks when the account routes are implemented.
5. Run bounded verification and reset journeys with controlled inboxes after the
   email-test scope is agreed. Check inbox/spam, link expiry/reuse and application
   redirects; saving SMTP settings alone is not delivery verification.

References: [Resend Supabase SMTP](https://resend.com/docs/send-with-supabase-smtp),
[Supabase SMTP restrictions](https://supabase.com/docs/guides/auth/auth-smtp),
[Auth redirect URLs](https://supabase.com/docs/guides/auth/redirect-urls).

## Official implementation references

- Key headers and types: [Supabase API keys](https://supabase.com/docs/guides/getting-started/api-keys).
- Explicit hosted target selection and CLI versions: [local/hosted projects](https://supabase.com/docs/guides/local-development/local-and-hosted-projects), [CLI reference](https://supabase.com/docs/reference/cli/introduction).
- Real verification/recovery delivery: [custom SMTP](https://supabase.com/docs/guides/auth/auth-smtp), [password Auth](https://supabase.com/docs/guides/auth/passwords).
- Schema/authorization assertions: [database testing](https://supabase.com/docs/guides/database/testing).
