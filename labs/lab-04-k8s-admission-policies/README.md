# Lab 04: K8s Admission Policies

## Overview

Use policy-as-code to block risky Kubernetes workloads at deploy time.

## Objectives

- Install a policy engine (Kyverno or Gatekeeper)
- Enforce baseline policies
- Add an exception path

## Time

60-90 minutes

## Prerequisites

- Access to a Kubernetes cluster
- `kubectl` configured

## Steps

1. Install Kyverno.
   ```bash
   kubectl create -f https://raw.githubusercontent.com/kyverno/kyverno/main/config/install.yaml
   ```

2. Apply a baseline policy (example: non-root + resource limits).
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

4. Add an exception namespace with a policy exception label.

5. Re-test deployment into the exception namespace.

## Validation

- Non-compliant pods are rejected.
- Exceptions are explicit and auditable.

## Extensions

- Require image signatures.
- Enforce allowed registries.
- Add pod security standards (restricted baseline).
