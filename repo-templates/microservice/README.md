# Microservice template profile

This profile generates the complete [sample API reference](../../projects/microservice-api/README.md), including real local/CI checks, dependency locks, image build/inventory support, policy fixtures, and offline detection/response exercises.

From the source repository root:

```bash
python3 scripts/bootstrap_template.py --profile microservice --destination ../my-microservice-reference
cd ../my-microservice-reference
make setup
make test
make validate
```

See the [template guide](../README.md) for prerequisites, exact generated structure, refusal/cleanup behavior, and review before publishing. Read generated `TEMPLATE-SETUP.md`, then follow the root quick start. The canonical workflow is at `.github/workflows/devsecops-golden-pipeline.yml`; its shared dependencies are copied together.

Docker/scanner/policy tools need the declared installations. Keyless signing, manual registry release, and deployed promotion are separate steps with explicit identity/environment prerequisites. No DAST target URL, production service, or externally delivered alert is created. The old [ci.yml](ci.yml) is a compatibility notice only.
