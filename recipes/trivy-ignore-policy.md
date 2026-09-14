# Time-bounded Trivy exceptions

An accepted unresolved vulnerability and a false positive need different recorded reasons. Both require evidence, an owner, bounded scope and approval under [C11](../templates/control-catalog.md). Use the same exception ID in the [exception record](../templates/security-exception-template.md), report and ignore-file comment.

The supplied [example ignore file](trivyignore.example) is deliberately **expired** and is not active repository policy. It demonstrates Trivy's supported expiry syntax without creating a permanent waiver.

```bash
trivy fs --ignorefile recipes/trivyignore.example --show-suppressed .
```

Record your Trivy/database versions and review ordinary as well as suppressed results. The example entry must not suppress a result after its expiry. An expired example can still produce no findings if its named CVE is absent; that alone is not proof of suppression enforcement. Use a known local finding fixture when validating your own exception lifecycle.

The plaintext format is ID-wide. For package/path scoping, Trivy's YAML ignore format supports `purls`, `paths`, `expired_at` and `statement`, but is documented as experimental and requires an explicit ignore-file path. Evaluate version compatibility before adopting it. No result should be silently excluded because a review date was written only in a comment.

Reference checked 2026-09-15: [Trivy filtering and expiration](https://trivy.dev/docs/latest/configuration/filtering/). No scan result is claimed here.
