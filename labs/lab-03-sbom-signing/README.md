# Lab 03: SBOM and Signing

## Overview

Generate an SBOM and sign artifacts to improve supply chain integrity.

## Objectives

- Generate an SBOM in CI
- Sign artifacts and SBOMs
- Verify signatures before deployment

## Time

45-60 minutes

## Prerequisites

- Container build or artifact output
- Access to a container registry
- [Syft](https://github.com/anchore/syft) and [Cosign](https://github.com/sigstore/cosign) installed

## Steps

1. Generate an SBOM.
   ```bash
   syft dir:. -o cyclonedx-json > sbom.json
   ```

2. Sign the SBOM.
   ```bash
   COSIGN_EXPERIMENTAL=1 cosign sign-blob --yes sbom.json
   ```

3. Verify the signature.
   ```bash
   COSIGN_EXPERIMENTAL=1 cosign verify-blob --signature sbom.json.sig sbom.json
   ```

4. Store the SBOM with the build artifact.

5. Add a CI gate that fails if SBOM generation or verification fails.

## Validation

- SBOM file is generated and stored as a build artifact.
- Signatures are verified before deployment.

## Extensions

- Add [SLSA](https://slsa.dev/) provenance attestations.
- Scan SBOMs with [Grype](https://github.com/anchore/grype).
- Enforce signed images in K8s admission policies.
