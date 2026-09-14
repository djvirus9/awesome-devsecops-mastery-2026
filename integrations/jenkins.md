# Jenkins adaptation plan

Status: **design guidance; no Jenkinsfile or Jenkins runtime validation is supplied**. Use the [GitHub reference pipeline](../pipelines/github-actions/devsecops.yml) to understand required behavior, not as Jenkins syntax.

Prerequisites: a maintained Jenkins installation, an isolated agent with Python 3.12+ and required tools, and credentials scoped only to trusted publishing stages.

| Stage | Required behavior / acceptance |
| --- | --- |
| Checkout and setup | Record exact commit; install the documented pinned dependencies on an isolated agent |
| Test and validate | Run `make test` and `make validate`; preserve failing exit status |
| Security checks | Run declared SAST/SCA/secret checks; test both finding and tool-error handling |
| Evidence | Archive relevant reports/SBOM with access/retention settings, including safe failure evidence |
| Promotion, if adopted | Trusted branch/context only; verify artifact digest and signature identity before deployment |

Implement a Jenkinsfile in your project, validate its syntax using your installed Jenkins, then record one passing and one controlled failing build. Verify source-control merge checks consume the Jenkins status; merely adding a stage does not block merging. Do not claim C03/C06 until those platform behaviors have evidence.

Reference: [Jenkins Pipeline](https://www.jenkins.io/doc/book/pipeline/). Use [secure CI criteria](../templates/secure-ci-guidelines.md) and [evidence indexing](../evidence-packs/evidence-index.md).
