# Phase 3: supply-chain evidence

Start from the built image. [Lab 03](../../labs/lab-03-sbom-signing/README.md) produces its inventory and demonstrates retained blob-signature verification.

| Evidence | Question answered | Limitation |
| --- | --- | --- |
| SBOM | Which packages did the generator identify in this artifact? | Completeness depends on generator/input coverage. |
| Vulnerability report | Which identified packages match the current advisory data? | Results depend on database time and package identification. |
| Signature and bundle | Did the expected identity sign these bytes? | Does not prove safe code or a trusted build process by itself. |
| Provenance | Which builder/source/process are claimed for this subject? | Claims need trusted identity, builder policy, and subject verification. |
| Promotion record | Which immutable digest passed the selected controls? | Configuration alone does not prove deployment used it. |

The release owner binds source commit, image digest, SBOM, reports, expected issuer/identity, provenance, and verification result. A local image ID differs from an OCI registry manifest digest; do not interchange them. Review dependency updates, unsupported packages, lock changes, and scanner database freshness.

Definition of done for the local lab: built-image inventory exists and its scope is understood. Optional keyless exercise: bundle retained, expected identity passes, wrong identity fails. Deployment completion additionally requires registry-digest association and verification before promotion; record it separately. No SLSA level is inferred from these examples.

References: [Syft configuration](https://oss.anchore.com/docs/reference/configuration/), [Sigstore signing](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/), [verification](https://docs.sigstore.dev/cosign/verifying/verify/), [SLSA build track](https://slsa.dev/spec/v1.2/build-track-basics).
