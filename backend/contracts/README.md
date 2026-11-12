# Application API contract

`openapi.json` freezes the executable `/api/v1` schema. Check it with
`python -m scripts.quality.check_api_contract`; deliberately update it with
`--update` alongside affected frontend clients and tests. Existing error payloads
use FastAPI's `detail` field (a safe string or validation-error array). Authentication
is verified independently by the API; client-side routing is not authorization.

The forecast browser validator and fixture tests supplement this backend snapshot.
Snapshot equality alone does not prove cloud behavior, user isolation, or that a
new client field has runtime validation.
