#!/usr/bin/env python3
"""Render a narrow, expiring local lab exception; never apply it to a cluster."""

import argparse
import datetime as dt
import json


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minutes", type=int, default=15)
    parser.add_argument("--ticket", required=True)
    parser.add_argument("--approver", required=True)
    parser.add_argument("--reason", required=True)
    args = parser.parse_args()
    if not 1 <= args.minutes <= 120:
        parser.error("local exceptions must expire in 1–120 minutes")
    if any(not value.strip() for value in (args.ticket, args.approver, args.reason)):
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
            "policyRefs": [{"name": "require-resource-limits", "kind": "ValidatingPolicy"}],
            "matchConditions": [{
                "name": "exact-local-pod",
                "expression": "object.kind == 'Pod' && object.metadata.namespace == 'devsecops-reference' && object.metadata.name == 'missing-limits'",
            }, {
                "name": "not-expired",
                "expression": "time.now() < timestamp(" + json.dumps(expiry_text) + ")",
            }],
        },
    }, indent=2))


if __name__ == "__main__":
    main()
