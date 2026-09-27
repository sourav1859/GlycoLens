# Safety Checklist

## Medical communication

- Label the system research/education only and forecasts as uncertain estimates.
- Show provenance, model/config identity where appropriate, and limitations.
- Avoid treatment instructions, causal certainty, clinical validation claims, and unsafe reassurance.

## Data and model behavior

- Reject or visibly degrade on missing, stale, implausible, or insufficient CGM context.
- Surface uncertainty and out-of-distribution limitations.
- Prevent future CGM/events and later meal outcomes from entering evaluation context.
- Use subject-aware and temporal splits and account for unusable runs.

## Security and privacy

- Keep service-role keys, API secrets, and OAuth tokens server-side and out of logs.
- Enforce row-level security and ownership checks.
- Review dependency, secret, and static-analysis results when configured.
- Validate inputs, authorization, rate/abuse behavior, retries, and error redaction.
- Keep real PHI, private exports, downloaded datasets, model weights, and sensitive artifacts out of Git.
