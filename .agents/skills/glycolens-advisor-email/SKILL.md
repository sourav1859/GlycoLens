---
name: glycolens-advisor-email
description: Draft and send GlycoLens capstone email to advisor Professor Haibo Yang using private runtime account configuration, with mandatory user approval immediately before every send.
---

# GlycoLens Advisor Email

Use this skill when the user asks to email, contact, or send a GlycoLens update to "my advisor," "Professor Yang," or Haibo Yang.

## Private identity configuration

- Advisor: Professor Haibo Yang
- Sender address variable: `GLYCOLENS_ADVISOR_EMAIL_SENDER`
- Recipient address variable: `GLYCOLENS_ADVISOR_EMAIL_RECIPIENT`

Resolve both addresses from the process environment or the repository's ignored `.env` file. Never print the configured values in logs or write them into tracked files, generated documentation, commit messages, or Graphify input. If either value is missing, stop and ask the user to configure it locally. Never infer or substitute another address based on autocomplete, prior messages, or similar names.

## Workflow

1. Prepare a concise, professional, human-friendly draft using only information relevant to the user's request. Verify requested repository links and attachment paths before including them.
2. Prefer an authenticated email connector for the resolved sender account. Otherwise, use an already signed-in webmail session. Do not install software, change accounts, enter credentials, or alter authentication settings on the user's behalf.
3. Before sending, present the complete final preview to the user: From, To, Subject, body, and every attachment. Ask for explicit approval to send that exact email.
4. Treat the approval checkpoint as mandatory for every email. The initial request to "send an email" and this standing skill are not final approval. Do not click Send, invoke a send API, schedule delivery, or otherwise transmit the message until the user approves the displayed final preview.
5. After approval, re-check that the interface still shows the resolved sender and recipient values, send once, and verify visible confirmation or the Sent folder. If the outcome is uncertain, report the uncertainty instead of retrying and risking a duplicate.
6. If no usable authenticated email capability is available, provide the completed draft and state what prevented sending.

## Data safeguards

- Attach only files the user explicitly requested for that email.
- Never attach research datasets, private CGM exports, credentials, tokens, environment files, or other sensitive project material.
- Do not expose addresses through CC or BCC unless the user explicitly requests it and approves the final preview.
- Keep a medical/research email informational; do not add clinical advice, insulin-dose recommendations, or claims not supported by the project sources.
