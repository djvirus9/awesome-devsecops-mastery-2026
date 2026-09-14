#!/usr/bin/env python3
"""Render a local exception or its required deadline guard; never apply either."""

import argparse
import copy
import datetime as dt
import json
from pathlib import Path

GUARD_NAME = "reference-limits-deadline"
EXACT_OBJECT = "object.kind == 'Pod' && object.metadata.namespace == 'devsecops-reference' && object.metadata.name == 'missing-limits'"
POLICY_REFS = [{"name": "require-resource-limits", "kind": "ValidatingPolicy"}]


def deadline_guard(exception):
    """Derive limits from the canonical policy, but evaluate time per admission.

    Kyverno 1.19.1 does not evict a cached exception on expiresAt alone. This
    separate policy is deliberately NOT referenced by the exception.
    """
    import yaml

    spec = exception["spec"]
    if (exception.get("apiVersion") != "policies.kyverno.io/v1"
            or exception.get("kind") != "PolicyException"
            or exception.get("metadata", {}).get("name") != "reference-limits-exercise"
            or exception.get("metadata", {}).get("namespace") != "policy-exceptions"
            or spec.get("policyRefs") != POLICY_REFS
            or spec.get("matchConditions") != [{"name": "exact-local-pod", "expression": EXACT_OBJECT}]):
        raise ValueError("Guard input must be the unmodified exact-object reference exception")
    # Parse then serialize: never interpolate arbitrary input into CEL.
    expiry = dt.datetime.fromisoformat(spec["expiresAt"].replace("Z", "+00:00"))
    if expiry.tzinfo is None:
        raise ValueError("Exception expiry must include its timezone")
    deadline = expiry.astimezone(dt.timezone.utc).isoformat(timespec="seconds").replace("+00:00", "Z")
    source = yaml.safe_load((Path(__file__).parent / "kyverno/require-resource-limits.yaml").read_text())
    guard = copy.deepcopy(source)
    guard["metadata"] = {"name": GUARD_NAME, "annotations": {
        **exception["metadata"].get("annotations", {}),
        "devsecops.example/derived-from": source["metadata"]["name"],
        "devsecops.example/expires-at": deadline,
    }}
    guarded = guard["spec"]
    guarded["validationActions"] = ["Deny"]
    guarded["failurePolicy"] = "Fail"
    guarded["evaluation"] = {"background": {"enabled": False}}
    guarded["matchConstraints"] = {"resourceRules": [rule for rule in guarded["matchConstraints"]["resourceRules"]
        if "pods" in rule["resources"]]}
    guarded["matchConditions"].append({"name": "exact-local-pod", "expression": EXACT_OBJECT})
    for validation in guarded["validations"]:
        validation["expression"] = f'time.now() < timestamp("{deadline}") || ({validation["expression"]})'
        validation["message"] = "Exception deadline reached. " + validation["message"]
    return guard


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=int, default=15)
    parser.add_argument("--ticket")
    parser.add_argument("--approver")
    parser.add_argument("--reason")
    parser.add_argument("--guard-for", type=Path, help="Render the guard for an existing exception JSON file")
    args = parser.parse_args()
    if args.guard_for:
        try:
            guard = deadline_guard(json.loads(args.guard_for.read_text()))
        except (OSError, KeyError, TypeError, ValueError) as error:
            parser.error(str(error))
        print(json.dumps(guard, indent=2))
        return
    if not 1 <= args.minutes <= 120:
        parser.error("local exceptions must expire in 1–120 minutes")
    if any(not value or not value.strip() for value in (args.ticket, args.approver, args.reason)):
        parser.error("ticket, approver, and reason cannot be blank")
    expiry = (dt.datetime.now(dt.timezone.utc) + dt.timedelta(minutes=args.minutes))
    expiry_text = expiry.isoformat(timespec="seconds").replace("+00:00", "Z")
    print(json.dumps({
        "apiVersion": "policies.kyverno.io/v1",
        "kind": "PolicyException",
        "metadata": {
            "name": "reference-limits-exercise",
            "namespace": "policy-exceptions",
            "annotations": {
                "devsecops.example/ticket": args.ticket,
                "devsecops.example/approved-by": args.approver,
                "devsecops.example/reason": args.reason,
            },
        },
        "spec": {
            "expiresAt": expiry_text,
            "policyRefs": POLICY_REFS,
            "matchConditions": [{
                "name": "exact-local-pod",
                "expression": EXACT_OBJECT,
            }],
        },
    }, indent=2))


if __name__ == "__main__":
    main()
