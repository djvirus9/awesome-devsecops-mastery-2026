# Phase 03: Supply Chain

## Goals

- Ensure artifact integrity and traceability
- Reduce dependency risk and improve transparency

## Practices

- Generate SBOMs for every release
- Sign artifacts and SBOMs
- Require provenance for deployments

## Tools

- SBOM: [Syft](https://github.com/anchore/syft), [CycloneDX](https://cyclonedx.org/)
- Vulnerability scanning: [Grype](https://github.com/anchore/grype)
- Signing: [Cosign](https://github.com/sigstore/cosign)
- Provenance: [SLSA](https://slsa.dev/), [in-toto](https://in-toto.io/)

## Deliverables

- SBOMs stored with releases
- Signed artifacts and verification gate
- Provenance attestations

## Lab

- [Lab 03: SBOM and Signing](../../labs/lab-03-sbom-signing/README.md)
