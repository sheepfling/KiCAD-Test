"""Cross-platform typed product policy and deterministic review artifacts."""
from __future__ import annotations

import argparse
import subprocess
from pathlib import Path

from .hwrepo.generation import check_generation, generate, snapshot, verify_snapshot
from .hwrepo.product import check


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("command", choices=("check", "generate", "snapshot", "verify-snapshot"))
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--release", action="store_true", help="Fail closed: build/release authorization is not implemented")
    parser.add_argument("--output", type=Path, help="New directory for a review snapshot")
    args = parser.parse_args()
    root = args.root.resolve()
    try:
        if args.release and args.command != "check":
            parser.error("--release is only valid with check")
        if args.command == "check":
            policy = check(root, args.release)
            result: dict[str, object] = policy.model_dump(mode="json")
            if policy.status == "PASS":
                generation_drift = check_generation(root)
                result["generation_drift"] = generation_drift
                if generation_drift:
                    result["status"] = "FAIL"
        elif args.command == "generate":
            result = {
                "status": "PASS",
                "generated": generate(root),
                "build_authorized": False,
            }
        elif args.command == "snapshot":
            if args.output is None:
                parser.error("snapshot requires --output")
            result = {
                "status": "PASS",
                "manifest": snapshot(root, args.output).model_dump(mode="json"),
            }
        else:
            if args.output is None:
                parser.error("verify-snapshot requires --output")
            result = verify_snapshot(args.output.resolve()).model_dump(mode="json")
    except (OSError, ValueError, KeyError, TypeError, subprocess.SubprocessError) as exc:
        result = {"status": "FAIL", "error": str(exc), "build_authorized": False}
    import json  # CLI serialization boundary; the service layer returns models.

    print(json.dumps(result, indent=2))
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
