"""Verify release provenance using a single exact certificate identity policy."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys


def verification_command(repository, source_commit, image_reference):
    if not re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9_-]*/[A-Za-z0-9_.-]+", repository):
        raise ValueError("Expected an owner/repository name")
    if not re.fullmatch(r"[0-9a-f]{40}", source_commit):
        raise ValueError("Expected a full GitHub source commit")
    expected_image = "ghcr.io/" + repository.lower() + "/sample-api@sha256:"
    if not image_reference.startswith(expected_image) or not re.fullmatch(
        r"[0-9a-f]{64}", image_reference.removeprefix(expected_image)
    ):
        raise ValueError("Expected this repository's immutable sample-api digest")
    identity = f"https://github.com/{repository}/.github/workflows/release.yml@refs/heads/main"
    # gh treats cert-identity, signer-workflow and signer-repo as alternatives.
    # Exact SAN equality already binds the full workflow path AND branch.
    return [
        "gh", "attestation", "verify", "oci://" + image_reference,
        "--repo", repository, "--bundle-from-oci",
        "--source-digest", source_commit, "--source-ref", "refs/heads/main",
        "--cert-identity", identity,
        "--cert-oidc-issuer", "https://token.actions.githubusercontent.com",
        "--deny-self-hosted-runners", "--format", "json",
    ]


def verify(repository, source_commit, image_reference, output):
    command = verification_command(repository, source_commit, image_reference)
    result = subprocess.run(command, check=True, text=True, capture_output=True)
    evidence = json.loads(result.stdout)
    if not isinstance(evidence, list) or not evidence:
        raise ValueError("Provenance verifier returned no verified attestations")
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(evidence, indent=2) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repository", required=True)
    parser.add_argument("--source-commit", required=True)
    parser.add_argument("--image-reference", required=True)
    parser.add_argument("--output", type=Path, default=Path("reports/provenance-verification.json"))
    args = parser.parse_args()
    try:
        verify(args.repository, args.source_commit, args.image_reference, args.output)
    except subprocess.CalledProcessError as error:
        print(error.stderr.strip(), file=sys.stderr)
        return error.returncode or 1
    except (ValueError, OSError) as error:
        print(f"Release verification failed: {error}", file=sys.stderr)
        return 1
    print("Provenance verified: exact image, source commit/ref, workflow identity and hosted runner")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
