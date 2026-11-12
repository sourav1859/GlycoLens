"""Check the versioned OpenAPI snapshot; --update is an explicit review operation."""

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SNAPSHOT = ROOT / "backend/contracts/openapi.json"


def current_contract() -> dict:
    from backend.app.main import app

    return app.openapi()


def contract_matches(actual: dict) -> bool:
    return SNAPSHOT.is_file() and json.loads(SNAPSHOT.read_text(encoding="utf-8")) == actual


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--update", action="store_true")
    args = parser.parse_args()
    contract = current_contract()
    if args.update:
        SNAPSHOT.parent.mkdir(parents=True, exist_ok=True)
        SNAPSHOT.write_text(json.dumps(contract, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        print("Updated API snapshot; review its diff with the matching client/tests")
        return 0
    if not contract_matches(contract):
        print("API contract drift: update the reviewed snapshot and affected clients/tests")
        return 1
    print("API contract matches reviewed snapshot")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
