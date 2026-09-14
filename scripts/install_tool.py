#!/usr/bin/env python3
"""Install reviewed release pins into this checkout's .tools/bin.

Usage: python3 scripts/install_tool.py TOOL [TOOL...]
Supports Linux amd64 and macOS arm64. No sudo, shell installers or execution
of downloaded files. Put the checkout's .tools/bin on PATH explicitly.

Trust model: committed SHA256 pins bind bytes to a reviewed upstream release
asset. They are not provenance verification or a guarantee of safe behavior.
Review the official repository/release and attestations separately on updates.
This script assumes the checkout and its parent directories are locally trusted.
"""
import argparse
import hashlib
import hmac
import json
import os
from pathlib import Path
import platform
import re
import tarfile
import tempfile
from urllib.error import URLError
from urllib.parse import urlparse
from urllib.request import HTTPRedirectHandler, Request, build_opener

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "tool-versions.json"
PLATFORMS = {"linux-amd64", "darwin-arm64"}
DOWNLOAD_HOSTS = {
    "github.com", "release-assets.githubusercontent.com", "objects.githubusercontent.com",
    "get.helm.sh", "dl.k8s.io", "cdn.dl.k8s.io",
}
MAX_DOWNLOAD = 512 * 1024 * 1024
MAX_BINARY = 512 * 1024 * 1024
MAX_EXPANDED = 768 * 1024 * 1024
CHUNK = 1024 * 1024


def require_match(pattern, value, description):
    if not isinstance(value, str) or not re.fullmatch(pattern, value):
        raise ValueError(f"invalid {description}")
    return value


def validate_archive_member(member):
    # Exact POSIX names only: no normalization, traversal, absolute paths or
    # archive-wide extraction. Helm places its binary one directory deep.
    require_match(r"[A-Za-z0-9][A-Za-z0-9._-]*(?:/[A-Za-z0-9][A-Za-z0-9._-]*){0,3}", member, "archive member")
    if len(member) > 256:
        raise ValueError("archive member exceeds length limit")
    return member


def release_url(spec, pin, platform_name):
    if "url" not in pin:
        if spec["repository"] in {"helm/helm", "kubernetes/kubernetes"}:
            raise ValueError("Helm and kubectl pins require an explicit official download URL")
        return f"https://github.com/{spec['repository']}/releases/download/v{spec['version']}/{pin['asset']}"
    # These two official distributions do not publish binaries as GitHub
    # release assets. Keep overrides bound to their exact version/platform
    # routes, rather than accepting an arbitrary URL on an approved host.
    if spec["repository"] == "helm/helm":
        asset = f"helm-v{spec['version']}-{platform_name}.tar.gz"
        expected = f"https://get.helm.sh/{asset}"
        member = f"{platform_name}/helm"
    elif spec["repository"] == "kubernetes/kubernetes":
        asset = "kubectl"
        expected = f"https://dl.k8s.io/release/v{spec['version']}/bin/{platform_name.replace('-', '/')}/kubectl"
        member = None
    else:
        raise ValueError("explicit download URLs are limited to official Helm and kubectl distributions")
    if pin["url"] != expected or pin["asset"] != asset or pin["member"] != member:
        raise ValueError("download URL, asset and member must match the pinned official version/platform")
    return validate_url(pin["url"])


def validate_manifest(manifest):
    if not isinstance(manifest, dict) or manifest.get("schema_version") != 1:
        raise ValueError("unsupported manifest schema")
    tools = manifest.get("tools")
    if not isinstance(tools, dict) or not tools:
        raise ValueError("manifest must contain tools")
    for name, spec in tools.items():
        require_match(r"[a-z][a-z0-9-]*", name, "tool name")
        if not isinstance(spec, dict):
            raise ValueError("invalid tool specification")
        require_match(r"[0-9]+\.[0-9]+\.[0-9]+", spec.get("version"), "version")
        require_match(r"[A-Za-z0-9_-]+/[A-Za-z0-9_.-]+", spec.get("repository"), "repository")
        platforms = spec.get("platforms")
        if not isinstance(platforms, dict) or set(platforms) != PLATFORMS:
            raise ValueError("both supported platforms must have reviewed pins")
        for platform_name, pin in platforms.items():
            required = {"asset", "sha256", "member"}
            if not isinstance(pin, dict) or not required <= set(pin) or set(pin) - required - {"url"}:
                raise ValueError("asset pins require asset, sha256, member and only an optional url")
            asset = require_match(r"[A-Za-z0-9][A-Za-z0-9._-]*", pin["asset"], "asset name")
            require_match(r"[0-9a-f]{64}", pin["sha256"], "SHA256 pin")
            if pin["member"] is not None:
                validate_archive_member(pin["member"])
                if not asset.endswith(".tar.gz"):
                    raise ValueError("only tar.gz archives are supported")
            release_url(spec, pin, platform_name)
    return manifest


def native_platform():
    system = platform.system().lower()
    machine = platform.machine().lower()
    architecture = {"x86_64": "amd64", "amd64": "amd64", "aarch64": "arm64", "arm64": "arm64"}.get(machine)
    result = f"{system}-{architecture}"
    if result not in PLATFORMS:
        raise ValueError(f"unsupported platform: {system}/{machine}; use Linux amd64 or macOS arm64")
    return result


def validate_url(url):
    if not isinstance(url, str) or len(url) > 4096 or re.search(r"[\x00-\x20\x7f]", url):
        raise ValueError("invalid download URL")
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.hostname not in DOWNLOAD_HOSTS
            or parsed.username is not None or parsed.password is not None
            or parsed.port not in (None, 443) or parsed.fragment):
        raise ValueError("download URL must use HTTPS on an approved official release host")
    return url


class ReleaseRedirects(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        validate_url(newurl)
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def download_asset(url, expected_sha256, output):
    validate_url(url)
    digest = hashlib.sha256()
    size = 0
    request = Request(url, headers={"User-Agent": "devsecops-reference-tool-installer"})
    opener = build_opener(ReleaseRedirects())
    with opener.open(request, timeout=30) as response:
        while True:
            block = response.read(CHUNK)
            if not block:
                break
            size += len(block)
            if size > MAX_DOWNLOAD:
                raise ValueError("release asset exceeds download size limit")
            digest.update(block)
            output.write(block)
    if not size:
        raise ValueError("release asset is empty")
    if not hmac.compare_digest(digest.hexdigest(), expected_sha256):
        raise ValueError("release asset SHA256 mismatch; existing executable was not changed")
    output.seek(0)


def executable_bytes(source, member):
    if member is None:
        data = source.read(MAX_BINARY + 1)
    else:
        validate_archive_member(member)
        with tarfile.open(fileobj=source, mode="r:gz") as archive:
            selected = []
            expanded = 0
            for count, item in enumerate(archive, start=1):
                expanded += item.size
                if count > 10000 or expanded > MAX_EXPANDED:
                    raise ValueError("archive exceeds inspection limits")
                if item.name == member:
                    selected.append(item)
            if len(selected) != 1:
                raise ValueError("archive must contain exactly one expected binary member")
            item = selected[0]
            if not item.isfile() or item.size > MAX_BINARY:
                raise ValueError("expected binary must be a bounded regular file")
            with archive.extractfile(item) as binary:
                data = binary.read(MAX_BINARY + 1)
            if len(data) != item.size:
                raise ValueError("archive binary was truncated")
    if not data or len(data) > MAX_BINARY:
        raise ValueError("binary is empty or exceeds size limit")
    return data


def write_executable(root, name, data):
    require_match(r"[a-z][a-z0-9-]*", name, "tool name")
    root = Path(root).resolve()
    directory = root
    for component in (".tools", "bin"):
        directory = directory / component
        if directory.is_symlink():
            raise ValueError("refusing a symlinked tool directory")
        directory.mkdir(exist_ok=True)
        if not directory.is_dir():
            raise ValueError("tool destination is not a directory")
    destination = directory / name
    if destination.is_symlink() or (destination.exists() and not destination.is_file()):
        raise ValueError("refusing a non-regular existing tool destination")
    temporary = None
    try:
        with tempfile.NamedTemporaryFile(prefix=f".{name}-", dir=directory, delete=False) as output:
            temporary = Path(output.name)
            output.write(data)
            output.flush()
            os.fsync(output.fileno())
            os.fchmod(output.fileno(), 0o755)
        os.replace(temporary, destination)
        temporary = None
    finally:
        if temporary is not None:
            temporary.unlink(missing_ok=True)
    return destination


def install(name, manifest, platform_name, root=ROOT):
    validate_manifest(manifest)
    if name not in manifest["tools"]:
        raise ValueError(f"unknown tool: {name}")
    if platform_name not in PLATFORMS:
        raise ValueError("unsupported platform")
    spec = manifest["tools"][name]
    pin = spec["platforms"][platform_name]
    url = release_url(spec, pin, platform_name)
    with tempfile.TemporaryFile() as source:
        download_asset(url, pin["sha256"], source)
        payload = executable_bytes(source, pin["member"])
    return write_executable(root, name, payload)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("tools", nargs="+", help="tool names from tool-versions.json")
    args = parser.parse_args()
    try:
        with MANIFEST.open(encoding="utf-8") as source:
            manifest = validate_manifest(json.load(source))
        target_platform = native_platform()
        unknown = set(args.tools) - manifest["tools"].keys()
        if unknown:
            raise ValueError("unknown tools: " + ", ".join(sorted(unknown)))
        for name in dict.fromkeys(args.tools):
            destination = install(name, manifest, target_platform)
            print(f"{name} {manifest['tools'][name]['version']}: {destination}", flush=True)
    except (ValueError, OSError, tarfile.TarError, URLError) as error:
        parser.exit(1, f"Installation failed: {error}\n")


if __name__ == "__main__":
    main()
