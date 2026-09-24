# Security and Privacy

GlycoLens is a research and educational project involving health-related data. It is not a medical device and must not be used to make insulin-dosing or emergency-care decisions.

## Never commit

- API keys, passwords, or client secrets
- Dexcom access or refresh tokens
- identifiable CGM, insulin, meal, activity, or health records
- private research datasets
- production database dumps
- model artifacts containing sensitive training data

Use `.env.example` only as a list of variable names. Keep real values in an ignored local `.env` file or a managed secret store.

## Demo and research data

Prefer public/de-identified datasets, Dexcom sandbox data, and virtual-patient scenarios. Synthetic fixtures must not be derived from identifiable records unless they have been properly anonymized and approved.

## Reporting concerns

Do not open a public issue containing a credential or personal health information. Revoke exposed credentials immediately and remove sensitive data from Git history before continuing work.
