#!/usr/bin/env bash
set -euo pipefail

policy_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kyverno_bin="${KYVERNO_BIN:-kyverno}"
gator_bin="${GATOR_BIN:-gator}"
"$kyverno_bin" version 2>&1 | grep -E '^Version: 1\.19\.1$' >/dev/null || {
  echo 'Install Kyverno CLI 1.19.1 using the pinned repository tool installer.' >&2
  exit 1
}
"$gator_bin" version 2>&1 | grep -E 'GitVersion:[[:space:]]+v3\.23\.1([+[:space:]]|$)' >/dev/null || {
  echo 'Install Gator 3.23.1 using the pinned repository tool installer.' >&2
  exit 1
}
"$kyverno_bin" test "$policy_root/kyverno/tests" --fail-only
"$gator_bin" verify "$policy_root/opa/tests/suite.yaml"
"$kyverno_bin" apply "$policy_root/kyverno/require-non-root.yaml" \
  "$policy_root/kyverno/disallow-privileged.yaml" \
  "$policy_root/kyverno/require-resource-limits.yaml" \
  "$policy_root/kyverno/restrict-workload.yaml" \
  --resource "$policy_root/../projects/k8s-gitops/base/deployment.yaml" \
  --resource "$policy_root/../projects/k8s-gitops/network-check.yaml" \
  --detailed-results --warn-no-pass --warn-exit-code 1
