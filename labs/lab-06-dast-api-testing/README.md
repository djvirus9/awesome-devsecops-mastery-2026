# Lab 06: DAST and API Testing

## Overview

Run dynamic application security testing in staging and validate API security using the OpenAPI spec.

## Objectives

- Run a DAST baseline scan
- Test APIs using an OpenAPI schema
- Track and triage findings

## Time

60-90 minutes

## Prerequisites

- Staging environment URL
- OpenAPI spec (JSON or YAML)
- Docker installed

## Steps

1. Run a ZAP baseline scan against staging.
   ```bash
   docker run --rm -t owasp/zap2docker-stable zap-baseline.py \
     -t https://staging.example.com \
     -r zap-report.html
   ```

2. Run an API scan using the OpenAPI spec.
   ```bash
   docker run --rm -t -v $(pwd):/zap/wrk owasp/zap2docker-stable zap-api-scan.py \
     -t /zap/wrk/openapi.yaml -f openapi \
     -r zap-api-report.html
   ```

3. Review the report and categorize findings.

4. Add a CI job that fails on high-severity results.

## Validation

- ZAP reports are generated and archived.
- High-severity issues fail the pipeline.

## Extensions

- Add authenticated scans with session scripts.
- Run fuzzing on high-risk endpoints.
- Add regression testing for fixed findings.
