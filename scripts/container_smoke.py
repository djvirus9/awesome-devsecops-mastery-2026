"""Exercise only a fresh, loopback-bound instance of the reference image."""

import argparse
import json
import re
import subprocess
import time
import urllib.error
import urllib.request
import uuid


def run(*args):
    return subprocess.check_output(["docker", *args], text=True).strip()


def check(url, status, token=None):
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    request = urllib.request.Request(url, headers=headers)
    opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
    try:
        response = opener.open(request, timeout=3)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        if response.status != status:
            raise RuntimeError(f"Expected HTTP {status}, received {response.status}")
        return json.load(response)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--image", default="devsecops-reference:local")
    args = parser.parse_args()
    name = f"devsecops-smoke-{uuid.uuid4().hex[:12]}"
    tokens = json.dumps({"demo-alice-token": "alice", "demo-bob-token": "bob"})
    container = run("run", "--detach", "--rm", "--name", name,
                    "--publish", "127.0.0.1::8080", "--read-only",
                    "--cap-drop", "ALL", "--security-opt", "no-new-privileges",
                    "--tmpfs", "/tmp:rw,nosuid,nodev,size=16m",
                    "--env", f"API_TOKENS_JSON={tokens}", args.image)
    if not re.fullmatch(r"[a-f0-9]{64}", container):
        raise RuntimeError("Docker did not return a container ID")
    try:
        address = run("port", container, "8080/tcp")
        if not re.fullmatch(r"127\.0\.0\.1:[0-9]+", address):
            raise RuntimeError("Expected a loopback-only port binding")
        base = f"http://{address}"
        deadline = time.monotonic() + 30
        while True:
            try:
                if check(base + "/health", 200) != {"status": "ok"}:
                    raise RuntimeError("Unexpected health response")
                break
            except (OSError, ValueError, RuntimeError):
                if time.monotonic() >= deadline:
                    raise RuntimeError("Reference container did not become healthy") from None
                time.sleep(0.5)
        check(base + "/v1/items", 401)
        owned = check(base + "/v1/items", 200, "demo-alice-token")
        if [item["id"] for item in owned["items"]] != ["item-1"]:
            raise RuntimeError("List response violated the ownership boundary")
        check(base + "/v1/items/item-1", 404, "demo-bob-token")
        run("exec", container, "python", "-c",
            "from pathlib import Path; "
            "assert 'gunicorn.ctl' not in Path('/proc/net/unix').read_text(); "
            "assert not Path('/home/app/.gunicorn/gunicorn.ctl').exists()")
        print("Container smoke passed: health, authentication, ownership, read-only runtime, no control socket")
    finally:
        subprocess.run(["docker", "stop", "--time", "5", container], check=True,
                       stdout=subprocess.DEVNULL)


if __name__ == "__main__":
    main()
