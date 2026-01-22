# Authenticated ZAP Scan

## Goal

Run a ZAP scan against a staging app that requires authentication.

## Steps

1. Export an auth token or session cookie.
2. Run ZAP with a replacer rule or script for authentication.

Example:
```bash
TOKEN="your-token"

docker run --rm -t owasp/zap2docker-stable zap-baseline.py \
  -t https://staging.example.com \
  -z "-config replacer.full_list(0).description=auth \
      -config replacer.full_list(0).enabled=true \
      -config replacer.full_list(0).matchtype=REQ_HEADER \
      -config replacer.full_list(0).matchstr=Authorization \
      -config replacer.full_list(0).replacement=\"Bearer ${TOKEN}\"" \
  -r zap-auth-report.html
```
