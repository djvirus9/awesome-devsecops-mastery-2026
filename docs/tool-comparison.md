# Tool Comparison

Quick comparisons to help pick tools based on scale, complexity, and budget.

## SAST

| Tool | Strengths | Notes |
| --- | --- | --- |
| [Semgrep](https://semgrep.dev/) | Fast, custom rules | Great for CI gating |
| [CodeQL](https://codeql.github.com/) | Deep analysis | Strong for GitHub users |
| [SonarQube](https://www.sonarqube.org/) | Broad quality + security | Heavier setup |

## SCA

| Tool | Strengths | Notes |
| --- | --- | --- |
| [Trivy](https://github.com/aquasecurity/trivy) | Open source, multi-target | Fast and simple |
| [Snyk](https://snyk.io/) | Managed platform | Strong UI and policies |

## SBOM

| Tool | Strengths | Notes |
| --- | --- | --- |
| [Syft](https://github.com/anchore/syft) | Simple, fast | Great default |
| [CycloneDX](https://cyclonedx.org/) | Standard format | Use with generators |

## DAST / API

| Tool | Strengths | Notes |
| --- | --- | --- |
| [OWASP ZAP](https://www.zaproxy.org/) | Open source | Baseline + API scan |
| [Burp Suite](https://portswigger.net/burp) | Best-in-class manual | Paid for advanced |
| [42Crunch](https://42crunch.com/) | API-focused | Strong for governance |

## Runtime Detection

| Tool | Strengths | Notes |
| --- | --- | --- |
| [Falco](https://falco.org/) | eBPF detections | Kubernetes-focused |
