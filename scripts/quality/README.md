# Quality Scripts

Store deterministic repository validation utilities here. Every script must have a real local invocation and must fail clearly when prerequisites are missing.

`validate_skills.py` checks repository skill structure, unfinished placeholders, and literal email-address leakage. Private contact values belong in ignored environment configuration and skills should reference variable names only.

`validate_codex_config.py` parses project and custom-agent TOML, checks required agent fields and unique names, enforces the intended Sol/Luna routing and concurrency cap, rejects deprecated profiles, dangerous sandbox defaults, Fast/Ultrafast service tiers, literal email addresses, and overlong skill descriptions.
