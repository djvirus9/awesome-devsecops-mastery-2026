# Lab 04: K8s Admission Policies

## Overview

Use policy-as-code to block risky Kubernetes workloads at deploy time.

## Objectives

- Install a policy engine
- Enforce baseline policies
- Add an exception path

## Time

60-90 minutes

## Prerequisites

- Access to a Kubernetes cluster
- `kubectl` configured
- [Kyverno](https://kyverno.io/) or [OPA Gatekeeper](https://open-policy-agent.github.io/gatekeeper/)

## Steps

1. Install Kyverno.
   ```bash
   kubectl create -f https://raw.githubusercontent.com/kyverno/kyverno/main/config/install.yaml
   ```

2. Apply a baseline policy (example: non-root).
   ```yaml
   apiVersion: kyverno.io/v1
   kind: ClusterPolicy
   metadata:
     name: baseline-pod-security
   spec:
     validationFailureAction: enforce
     rules:
       - name: require-non-root
         match:
           resources:
             kinds: [Pod]
         validate:
           message: "Run as non-root is required."
           pattern:
             spec:
               securityContext:
                 runAsNonRoot: true
   ```

3. Attempt to deploy a privileged pod and confirm it is blocked.

4. Add an exception namespace with a label and documented approval.

## Validation

- Non-compliant pods are rejected.
- Exceptions are explicit and auditable.

## Extensions

- Require image signatures with [Cosign](https://github.com/sigstore/cosign).
- Enforce allowed registries.
- Apply [Pod Security Standards](https://kubernetes.io/docs/concepts/security/pod-security-standards/).
