# Recipe model switch and bounded validation - November 11, 2026

## Configuration and authorization

The user selected `gpt-6-luna` to replace `gpt-5-mini` for structured recipe
extraction, and approved a USD 5 total live-test budget. Ignored root `.env` and
committed `.env.example` now set `LLM_MODEL=gpt-6-luna`. Other environment values
were preserved without printing credentials. The model/API key remain server-only.

The existing parser already uses OpenAI Responses, strict JSON Schema, local
Pydantic validation and explicit user confirmation. No prompt, reasoning-effort,
timeout, output-token-limit or application request-schema change was needed.
Forecasting adapters, research protocols and validated nutrition authority are
unchanged. Read-only model metadata requests verified both IDs before inference.

## Live protocol and spend

Eight independently specified synthetic cases cover gram amounts, fractions,
decimals, mixed units, repeated ingredients, cooking-time exclusion, instruction
injection and an ambiguous portion. No patient context, private CGM data or real
user records were sent. Each model received the same fixture text through the
actual application parser; requests were sequential with no retries or tuning.

The opt-in runner defaults to dry-run. Its fixed 16-call plan reserves USD 0.2192
using a conservative 64,000-input-token allowance and the existing 2,000-output
limit per request, below the user cap. It rejects unapproved/insufficient budgets,
unexpected models/endpoints, non-fixture inputs, oversized payloads, excess calls
and changed output limits before dispatch. Unknown usage retains its reserve.

Reproduction command (another run spends additional budget; deduct prior spend):

```powershell
python -m scripts.validation.validate_recipe_model --allow-paid --budget-usd 4.99 --compare --output docs/reports/recipe-model-validation-repeat.json
```

| Observed metric | GPT-6 Luna | GPT-5 mini |
|---|---:|---:|
| Live calls | 8 | 8 |
| Passed synthetic cases after scoring correction | 8/8 | 8/8 |
| Input tokens | 1,318 | 1,318 |
| Billed output tokens, including reasoning | 841 | 3,377 |
| Estimated token charge, USD | 0.00055230 | 0.00708350 |
| Mean observed request seconds | 2.435 | 5.631 |

Combined estimated token charge: **USD 0.00763580**. Every response supplied usage;
unpriced request reserve is zero. Rates are USD 0.10/0.50 per million input/output
tokens for Luna and USD 0.25/2.00 for GPT-5 mini. Cached input, if present, is priced
separately; reasoning tokens are already included in output, not charged twice.
These are calculations from returned usage and published prices, not an account
billing reconciliation or a claim about other project usage.

Sources: [Luna model](https://developers.openai.com/api/docs/models/gpt-6-luna),
[GPT-5 mini model](https://developers.openai.com/api/docs/models/gpt-5-mini),
[API pricing](https://developers.openai.com/api/docs/pricing).

## Scoring correction and limits

The first run scored each model 7/8 because the exact-name oracle accepted only
`flour`, rejecting valid source-derived names such as `flour for dusting` and
`flour (for the dough)`. Both models actually retained 100 g plus 50 g flour and
100 ml water with two servings. The allowed role-name aliases were corrected and
the same saved outputs were rescored offline. No prompts or model outputs changed,
and no additional API calls were made. This is a post-run oracle correction,
explicitly preserved in both artifacts rather than hidden as a clean first pass:

- [Original results and usage](recipe-model-validation-2026-11-11.json).
- [Offline rescoring and model summaries](recipe-model-validation-2026-11-11-rescored.json).
- [Synthetic inputs and expected values](../../tests/fixtures/recipe_extraction_cases.json).

The comparison demonstrates working live extraction on this small set and lower
observed Luna cost. It does not demonstrate higher general recipe accuracy,
statistical superiority, production latency or invoice savings. Larger varied
recipes, ambiguous inputs, human review and grounded downstream nutrition remain
required for P04 acceptance. The 144-case phase ledger was not marked passed.

## Offline validation and documentation

Seventeen focused tests passed: existing nutrition/recipe constraints and privacy
contracts, budget rejection before HTTP, no-call dry-run, incorrect quantity/unit/
serving/invented-food detection, ambiguity review and role-label aggregation.
The role tests also reject a 149 g total, preserving the independent quantity oracle.
The code was linted and formatting checked. No provider or account secrets appear
in committed examples, fixtures, reports or command output.

Planning 00/01/04/17, AGENTS.md, root/backend READMEs and cloud setup were updated.
Historical setup evidence retains the original selection with an explicit follow-up.
Research/forecast model selection, product scope and release acceptance were not changed.
Environment/template consistency, Git ignore, private/browser separation,
credential-free diff/artifacts and local report links were checked. Graphify is
limited to local code extraction in this work; no semantic document backend was enabled.
