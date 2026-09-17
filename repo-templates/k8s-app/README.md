# Kubernetes application template profile

This profile generates the same complete API/control reference plus the supplied [Kubernetes deployment guide](../../projects/k8s-gitops/README.md) and policy fixtures. It does not install a cluster or controller.

From the source repository root:

```bash
python3 scripts/bootstrap_template.py --profile k8s-app --destination ../my-k8s-reference
cd ../my-k8s-reference
make setup
make test
make validate
```

See the [template guide](../README.md) for structure and pre-publication review. Install the pinned policy CLIs, run `make policy-test`, and follow [Lab 04](../../labs/lab-04-k8s-admission-policies/README.md) for optional admission validation in a disposable supported cluster.

Local fixture success is distinct from webhook admission, CNI/network enforcement, image trust, and live rollback. Record those separately. The generated `.github/workflows/devsecops-golden-pipeline.yml` uses the canonical shared checks. The old [ci.yml](ci.yml) is a compatibility notice, not an alternative pipeline.
