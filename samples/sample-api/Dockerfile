FROM python:3.14-alpine3.24@sha256:c6ead215bfd31f1e433d968853b7a769989117115b728874824e6c0a27cb96fc

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

WORKDIR /app
COPY requirements.txt ./requirements.txt
# The published base predates this Alpine security update. Keep the package pin
# reviewed alongside the base digest; do not suppress the image vulnerability gate.
RUN apk add --no-cache 'libuuid=2.42.3-r1' \
    && pip install --no-cache-dir --only-binary=:all: --require-hashes -r requirements.txt \
    && addgroup -S -g 10001 app \
    && adduser -S -D -H -u 10001 -G app -s /sbin/nologin app
COPY --chown=10001:10001 app.py ./app.py
USER 10001:10001
EXPOSE 8080
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:8080/health', timeout=2).close()"
CMD ["gunicorn", "--no-control-socket", "--bind", "0.0.0.0:8080", "--workers", "2", "--worker-tmp-dir", "/tmp", "--access-logfile", "-", "--error-logfile", "-", "app:app"]
