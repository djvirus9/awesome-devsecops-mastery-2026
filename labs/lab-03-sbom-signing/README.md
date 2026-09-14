# Lab 03: image inventory, signing, and verification

Phase 3 · 45–60 minutes after tool installation. Prerequisites: completed local setup, Docker, Syft and Cosign versions from [tool-versions.json](../../tool-versions.json). Keyless signing additionally needs network access and an identity provider. Run commands from the repository root.

On a platform supported by the pinned installer (Linux amd64 or macOS arm64):

```bash
python3 scripts/install_tool.py syft cosign
export PATH="$PWD/.tools/bin:$PATH"
```

The helper verifies committed release-asset checksums before installing into this checkout. Other platforms need separately reviewed official installations; they are outside this helper's supported matrix.

## Build and inventory the actual image

```bash
make test
make container
make container-test
make sbom
```

`make container` builds `devsecops-reference:local`; `make sbom` inventories that image using [configs/syft.yaml](../../configs/syft.yaml) and writes `reports/sbom.cdx.json`. Inspect the document and verify it describes application and image packages. A source-directory inventory has different coverage and is not a substitute for this image inventory.

Record the source commit and local image identity:

```bash
git rev-parse HEAD
docker image inspect devsecops-reference:local --format '{{.Id}}'
```

A local image ID is not an OCI registry manifest digest. Published-image promotion must use the registry digest of the actual uploaded artifact.

## Optional keyless blob exercise

Read [Sigstore blob signing](https://docs.sigstore.dev/cosign/signing/signing_with_blobs/) and understand that public keyless signing records signing metadata in a transparency service. Use only this synthetic inventory. Decide the exact expected signer and issuer from the identity provider you intend to trust before verifying.

```bash
cosign sign-blob --bundle reports/sbom.sigstore.json reports/sbom.cdx.json
```

Complete the identity-provider flow. The retained bundle carries signature and verification material. Do not discard it or invent a detached `.sig` filename that the command never created.

Set the expected values in your shell (enter the actual selected identity and issuer on the following input lines):

```bash
read -r EXPECTED_SIGNER
read -r EXPECTED_ISSUER
cosign verify-blob reports/sbom.cdx.json \
  --bundle reports/sbom.sigstore.json \
  --certificate-identity "$EXPECTED_SIGNER" \
  --certificate-oidc-issuer "$EXPECTED_ISSUER"
```

Expect successful verification. Repeat verification with `--certificate-identity nobody@example.invalid` and the same actual issuer: it must fail. Do not use a wildcard identity to make a mismatch pass. [Sigstore verification documentation](https://docs.sigstore.dev/cosign/verifying/verify/) explains issuer and identity checks.

## Release integration

A signed SBOM proves a signer signed those bytes. It does not alone prove the image is safe, that the SBOM is complete, or that a particular builder produced the image. Promotion needs the exact image digest, inventory association, expected build identity, provenance, and verification before deployment. The [reference architecture](../../docs/reference-architecture.md) shows the trust decisions; the release workflow is a separate optional publishing operation, not part of this lab's local success.

## Verification, troubleshooting, cleanup

Retain the SBOM, bundle, source commit, image identity, expected signer/issuer, command result, tool versions, and limitations. Keep local and externally signed evidence distinct. Refer to the [worked evidence record](../../evidence-packs/example-release.md) without presenting its illustrative values as your results.

If Docker is unavailable, the image inventory step is pending. If the bundle is missing, rerun signing and retain its output. If identity verification fails, inspect the intended account/provider and trust policy rather than disabling verification. If network access is unavailable, complete build/inventory and mark keyless signing pending.

Remove the practice image with `docker image rm devsecops-reference:local` when no longer needed. Keep the selected reports for your evidence pack; do not commit credentials. Challenge: explain how to verify after the SBOM is modified. Solution: the original signature must fail; a reviewed new artifact requires fresh evidence and signing.
