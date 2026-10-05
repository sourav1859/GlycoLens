# Codex Token-Efficient Workflow

## Purpose and evidence

This workflow responds to a 14-day local audit that recorded 196.08 million tokens, 96.3% cached input, one session with 80.6% of recorded usage, 1,639 usage increments, 1,208 tool calls, and 23.29 million tokens in child sessions. These are diagnostic local records, not subscription-credit or allowance measurements.

The goal is to reduce avoidable context, retries, duplicate validation, and overlapping delegation while preserving scientific validity, medical safety, privacy, security, testing, and living documentation.

## Model routing

| Work | Start with |
|---|---|
| Parsing, formatting, aggregation, schema checks | Deterministic local script |
| Exact wording, extraction, narrow config edits | Luna low or medium |
| Bounded navigation and routine implementation | Luna medium or high |
| Normal multi-file implementation and test design | Sol medium |
| Architecture, leakage, medical safety, privacy, RLS/auth, conflicting evidence | Sol high |
| Extremely demanding unresolved analysis | Explicit escalation only |

Keep a lighter model only when it meets the quality bar without repeated repairs. Model availability varies by account, workspace, client, and rollout.

## Primary and custom agents

Use the primary agent for coordinated multi-file delivery and all decisions. Delegate only independent bounded work:

- `evidence-reader`: targeted read-only navigation and concise evidence.
- `routine-worker`: small unambiguous edits and narrow validation; it must return decisions to the primary agent.
- `critical-reviewer`: read-only consequential architecture, scientific, authorization, privacy, security, or medical-safety review.

Invoke a role explicitly by name and provide its goal, file boundary, expected evidence, and return format. Do not delegate trivial, sequential, or overlapping work. At most two child threads may be open.

## Session boundaries and handoffs

Keep one session to one milestone, feature, defect, or review domain. Start a fresh session after completion or before an unrelated subsystem. Carry forward only the structured [session handoff](templates/codex-session-handoff.md), not the full transcript.

## Reading and tool output

Read the planning README and Updated Project Summary before substantive work. Within a focused session, reuse unchanged content already in context. Reopen it only when it changed, a needed section is absent, a new decision depends on it, or verification requires current content. Use the planning impact map before opening specialized planning documents, and never skip an affected document.

Prefer `rg`, bounded ranges, filtered commands, quiet test modes, and local ignored logs. Do not return entire lockfiles, large JSON, database dumps, full test logs, Graphify exports, dataset rows, or generated artifacts to the model. Configuration limits an individual retained tool result to 4,000 tokens.

## Verification reuse

Use the narrow-to-broad verification ladder. Record a check, relevant file set, environment, and result. Reuse a pass until a relevant file or environment changes or another result creates doubt. Full application, database, model, presentation, scientific, or milestone suites run only when the change or gate requires them.

## Graphify policy

Check status once before the first eligible broad exploration or impact analysis and reuse it until relevant files change. Use Graphify for cross-file relationship questions; use direct search for a known file or symbol. Verify graph findings against source. Refresh once after final supported edits, first checking whether a hook already refreshed it.

Graphify 0.9.69 `query` performs deterministic local graph traversal in the inspected installation and does not accept a backend option. Semantic document extraction is separate and remains disabled; never enable it without explicit approval and a verified data boundary.

## Deterministic work and retry discipline

Use local scripts first for parsing, formatting, aggregation, configuration/schema validation, and repeatable calculations. Do not repeat a failure without changing a prerequisite, hypothesis, input, or diagnostic scope. After two materially different failed approaches, summarize evidence and reassess. Avoid installation, environment, and Graphify retry loops.

## Configuration

`.codex/config.toml` selects GPT-6.1 Sol at medium reasoning, bounds retained tool output, caps child concurrency at two, and defaults bounded children to GPT-6 Luna at medium reasoning. Agent files add narrower sandbox and task rules. `model_verbosity` is intentionally unset because the inspected official reference describes it as a GPT-5 Responses override, not an explicit GPT-6.1 guarantee. Manual context-window and auto-compaction limits remain unset pending controlled evidence.

For one session, select a model with `/model` or start the CLI with `codex --model <verified-model>`; use `-c model_reasoning_effort='"high"'` only when the task requires it. A session override does not change repository defaults.

## Controlled measurement plan

Choose several comparable completed task types, record scope and acceptance criteria, then repeat them under the new workflow without changing datasets, environment, or quality gates. Compare local recorded input/cached/output/reasoning tokens, tool and model-call counts, elapsed time, repairs, test results, and review findings. Report limitations and do not claim savings until samples are comparable.

Known limitations:

- Recorded tokens do not equal subscription credits.
- Cached tokens are included in input.
- Smaller models can lose savings when repairs increase.
- Multi-agent work can use more tokens than a single-agent run.
- Model availability depends on account, workspace, client, and rollout.
