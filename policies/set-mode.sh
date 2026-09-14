#!/usr/bin/env bash
set -euo pipefail

# Only the dedicated disposable Kind context is accepted.
mode="${1:-}"
case "$mode" in
  audit) actions='["Audit","Warn"]' ;;
  enforce) actions='["Deny"]' ;;
  *) echo 'Usage: bash policies/set-mode.sh audit|enforce' >&2; exit 2 ;;
esac
context=kind-devsecops-reference
kubectl --context "$context" get namespace devsecops-reference >/dev/null
for name in require-non-root disallow-privileged require-resource-limits restrict-workload; do
  kubectl --context "$context" patch validatingpolicy "$name" --type=merge \
    -p "{\"spec\":{\"validationActions\":$actions}}"
done
echo "Reference policies now use $mode mode in $context."
