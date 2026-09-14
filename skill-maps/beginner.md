# Beginner skill map

Prerequisite: [foundation](../docs/foundation.md). Complete [Lab 01](../labs/lab-01-precommit-sast/README.md) → [Lab 02](../labs/lab-02-ci-pr-gates/README.md) → [Lab 03](../labs/lab-03-sbom-signing/README.md). Allow 2–4 weeks of part-time practice.

## Assessable outcomes

- Run the sample and explain how server-side identity differs from record ownership.
- Show a harmless rule fixture that fails, explain the correction, and show local/CI checks passing.
- Explain why a local hook can be skipped and why required CI checks matter.
- Generate an inventory of the built image and distinguish SBOM, signature, verification, and provenance.
- Record the exact commit, command, result, and limitation in a small evidence pack.

Passing local checks completes the local part. Repository-required checks and keyless signing need their stated external prerequisites; record those separately. An assessor should be able to rerun the local steps and ask you to explain one failure without copying a tool description.

Continue to [intermediate](intermediate.md) when the application tests and source checks are understood, even if an optional registry is unavailable.
