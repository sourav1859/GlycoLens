# ADR 0016: Initial Hostinger KVM 2 deployment with managed Supabase

**Date:** November 7, 2026

**Status:** Accepted by the user as the initial deployment design. Provisioning,
deployment implementation and hosted acceptance remain pending.

## Context

The user selected Hostinger KVM 2 after reviewing separate frontend/backend hosting,
managed Supabase, memory evidence, costs and the option to upgrade later. The target
is a small research/education capstone deployment with occasional forecasts and
bounded simulator runs. This is not a measured production-capacity claim.

The current application uses the Chronos-2 C3 adapter on CPU. The local
[Chronos smoke report](../reports/milestone-1-phase-3-chronos2-smoke.md#measured-smoke-result)
records 810.83 MiB observed peak process RSS and a 455.79 MiB checkpoint cache on a
different Windows machine. These are single-process feasibility measurements, not
an end-to-end Linux or concurrency benchmark.

## Decision

- Use one **Hostinger KVM 2 VPS: 2 vCPU, 8 GB RAM, 100 GB NVMe** for the Next.js PWA,
  HTTPS reverse proxy, FastAPI modular monolith, CPU forecasting and isolated
  py-mgipsim execution.
- Keep **managed Supabase** for PostgreSQL, Auth, user-token PostgREST/RPC, RLS and
  pgvector. Start with Free while actual database size, egress and performance fit
  its allowances; do not install the Supabase stack on the VPS.
- Keep the forecasting adapter boundary and current application model. Hosting does
  not promote the separately evaluated LightGBM research candidate.
- Begin with one backend worker/model instance, bounded simulator execution and
  explicit CPU thread limits appropriate to two vCPUs. Validate overlapping requests
  before increasing workers; existing process-local locks do not coordinate workers.
- Retain the working local demo as a fallback. Bulk research data, model training,
  batch experiments and Graphify remain outside the hosted application runtime.
- Keep existing nutrition APIs and the recipe-parser API external, with private
  server-side configuration. Corrected Azure recipe/catalog activation remains
  governed separately by [ADR 0015](0015-corrected-nutrition-catalog-migration.md).

See the [deployment topology](../planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md#13-deployment).
Vercel, Railway and Render are alternatives, not required services for this initial
deployment. Reusing the existing Supabase account is compatible with this design;
the actual destination project and its capacity still require verification.

## Cost and operational assumptions

Hostinger's reviewed offer is **$210.96 paid upfront for 24 months**, equivalent to
$8.79/month, with advertised renewal at $14.99/month for the same term. Prices are
not a purchased contract; verify term, taxes, region and renewal at checkout.
Managed Supabase Free adds no subscription charge within its allowances. A later
Supabase Pro choice currently starts at $25/month for the first project and would
make the initial combined subscription equivalent $33.79/month, before extras.
Recipe-model API calls, domains, optional off-site backups and overages are separate.

The VPS is self-managed: application releases, OS/software updates, HTTPS, firewall
configuration, monitoring and recovery are our responsibility. VPS backups do not
back up the separate managed Supabase database; establish database backup/restore
evidence for the chosen plan.

Hostinger uses CPU credits and can reduce available CPU capacity after sustained
heavy use. Do not treat the advertised vCPU count as guaranteed continuous full
CPU throughput. The current CPU-credit article contains inconsistent numerical
details, so no exact sustained-performance calculation is used for this decision.
Profile the actual workload and avoid running long research jobs on the app host.

Supabase's storage/egress limits and inactivity pausing remain independent of VPS
capacity. The proposed corrected catalog budget is 150-250 MiB, not a measured
restore; apply the [migration capacity gate](../reports/azure-to-supabase-catalog-migration-strategy-2026-11-06.md#4-check-target-capacity-before-cloud-loading)
before import. Do not copy the 737.72 MiB source layout into a 500 MB Free database.

## Alternatives and tradeoffs

- **Vercel plus Railway or Render plus managed Supabase:** shorter financial
  commitment and less server administration, with a separate backend bill and
  additional provider configuration. Remains the migration option if VPS upkeep or
  CPU-credit behavior obstructs the demo.
- **KVM 4 with managed Supabase:** more compute/memory headroom at higher cost.
  Upgrade only when measured latency, memory pressure or CPU-credit exhaustion
  justifies it. The larger plan also uses CPU credits.
- **Self-hosted Supabase:** greater control and disk capacity, but adds database,
  authentication and recovery responsibilities. It is not part of this decision.
- **Local/RIT hosting:** retain for experiments and demo recovery; not the selected
  public application endpoint.

## Readiness and acceptance

The following are requirements, not completed checks:

1. Build reproducible Linux containers using pinned Python/Node dependencies,
   including the Chronos runtime group and the pinned simulator source/environment.
   Replace the Windows-specific simulator interpreter path with portable runtime
   configuration. Version runtime images; do not commit checkpoints or secrets.
2. Persist the model cache and required simulator/replay files across restarts.
   Warm the pinned model and expose readiness that reflects model/simulator
   availability; the current basic `/health` response is insufficient by itself.
3. Configure DNS/HTTPS, frontend API/Auth variables, explicit CORS origins and private
   backend secrets. Preserve existing `/api/v1` routes and user-token RLS behavior.
   Do not use a service-role key in browser code or to bypass owner isolation.
4. Select and inspect the managed Supabase destination. Apply reviewed migrations
   with a retained recovery path and validate anonymous demo Auth, RPCs, pgvector,
   cross-user isolation, database size and quotas. Keep Azure corrections on hold.
5. Define and verify overlap behavior: the current model/simulator locks return
   HTTP 429 while busy. Test clear retry/loading behavior or add bounded queueing;
   do not assume additional VPS resources change this application behavior.
6. Exercise login, reviewed nutrition, simulation, meal saving, forecast persistence
   and retrieval on desktop/mobile over HTTPS. Record cold/warm latency, p95 under
   intended concurrent requests, whole-stack peak memory, CPU/credits, errors,
   restart recovery and database restore evidence. Do not infer a supported user
   count from the local model smoke test.
7. Keep an independently runnable local demo and verify recovery before the defense.
   Add Compose packaging for the fallback; it does not currently exist in the repo.

Track execution in the [M3 deployment checklist](../planning/GlycoLens_06_Milestones_and_Schedule.md#initial-hostinger-kvm-2-deployment).
Selecting the provider does not close M2 live-provider/camera acceptance or M3
deployment gates. This work records the design; it does not purchase a plan, change
external services, apply hosted migrations or publish an endpoint.

## Rollback and review

Retain the previous application image/configuration and compatible persistent
volumes. Use forward-only reviewed database migrations with a tested recovery
package; never reset a hosted database to imitate a local reset. Fall back to the
verified local workflow if hosted acceptance fails. Keep application contracts and
Supabase separate so the compute workload can move to another VPS/PaaS without a
model or database redesign. Record new capacity evidence before upgrading to KVM 4
or changing providers.

## Documentation alignment

| Planning document reviewed and updated | Reason |
|---|---|
| [00 - Planning README](../planning/GlycoLens_00_README.md) | Record the accepted direction and link execution tracking. |
| [01 - Project summary](../planning/GlycoLens_01_Updated_Project_Summary.md) | Summarize placement and distinguish selection from deployment. |
| [04 - Architecture](../planning/GlycoLens_04_Tech_Stack_and_System_Architecture.md) | Replace the unspecified host with the selected topology and readiness gates. |
| [06 - Milestones](../planning/GlycoLens_06_Milestones_and_Schedule.md) | Track M3 deployment tasks without closing M2 or moving deadlines. |
| [08 - Risks](../planning/GlycoLens_08_Risks_Safety_and_Scope.md) | Record CPU credits, maintenance, persistence, quotas and recovery. |
| [09 - Project specification](../planning/GlycoLens_09_Project_Specification_Draft.md) | Align the formal app specification with the initial deployment choice. |
| [10 - M2 implementation](../planning/GlycoLens_10_Milestone_2_Implementation.md) | Separate the new target from historical local evidence and pending M2 acceptance. |

The root README and ADR index link the decision. This documentation change does
not alter product features, model selection, research protocols, schemas or code.

## Sources reviewed November 7, 2026

- [Hostinger VPS specifications, prepaid offer and renewal](https://www.hostinger.com/vps-hosting)
- [Hostinger VPS management responsibilities](https://www.hostinger.com/support/8852150-what-is-a-self-managed-vps-at-hostinger/)
- [Hostinger CPU credits](https://www.hostinger.com/support/how-cpu-credits-work-on-hostinger-vps/)
- [Supabase plans and limits](https://supabase.com/pricing)
- [Railway resource pricing](https://docs.railway.com/pricing)
- [Render compute pricing](https://render.com/pricing)
