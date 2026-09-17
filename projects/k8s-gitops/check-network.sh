#!/usr/bin/env bash
set -euo pipefail

project_root="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
kube=(kubectl --context kind-devsecops-reference --namespace devsecops-reference)
"${kube[@]}" rollout status deployment/sample-api --timeout=120s
"${kube[@]}" delete job reference-network-allowed reference-network-denied --ignore-not-found
"${kube[@]}" apply -f "$project_root/network-check.yaml"
if ! "${kube[@]}" wait --for=condition=Complete \
  job/reference-network-allowed job/reference-network-denied --timeout=90s; then
  "${kube[@]}" logs job/reference-network-allowed || true
  "${kube[@]}" logs job/reference-network-denied || true
  exit 1
fi
"${kube[@]}" logs job/reference-network-allowed
"${kube[@]}" logs job/reference-network-denied
