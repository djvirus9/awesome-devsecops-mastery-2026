import copy
import hashlib
import importlib.util
import io
import json
from pathlib import Path
import stat
import tarfile
import tempfile
import unittest
from unittest.mock import Mock, patch

SPEC = importlib.util.spec_from_file_location("tool_installer", Path(__file__).resolve().parents[1] / "scripts/install_tool.py")
installer = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(installer)


def archive_bytes(entries):
    output = io.BytesIO()
    with tarfile.open(fileobj=output, mode="w:gz") as archive:
        for name, content, kind in entries:
            item = tarfile.TarInfo(name)
            item.type = kind
            if kind == tarfile.REGTYPE:
                item.size = len(content)
                archive.addfile(item, io.BytesIO(content))
            else:
                item.linkname = "unrelated"
                archive.addfile(item)
    return output.getvalue()


def manifest_for(payload, member=None):
    pin = {"asset": "sample.tar.gz" if member else "sample-bin", "sha256": hashlib.sha256(payload).hexdigest(), "member": member}
    return {"schema_version": 1, "tools": {"syft": {"version": "1.2.3", "repository": "anchore/syft", "platforms": {key: copy.deepcopy(pin) for key in installer.PLATFORMS}}}}


class ToolInstallerTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()

    def fake_http(self, payload):
        opener = Mock()
        opener.open.return_value = io.BytesIO(payload)
        return patch.object(installer, "build_opener", return_value=opener)

    def test_committed_manifest_has_all_reviewed_pins(self):
        manifest = json.loads(installer.MANIFEST.read_text())
        installer.validate_manifest(manifest)
        self.assertEqual(set(manifest["tools"]), {"syft", "cosign", "trivy", "gitleaks", "kyverno", "gator", "kind", "helm", "kubectl"})

    def test_native_platform_and_unsupported_architecture(self):
        for system, machine, expected in [("Linux", "x86_64", "linux-amd64"), ("Darwin", "arm64", "darwin-arm64")]:
            with patch.object(installer.platform, "system", return_value=system), patch.object(installer.platform, "machine", return_value=machine):
                self.assertEqual(installer.native_platform(), expected)
        with patch.object(installer.platform, "system", return_value="Linux"), patch.object(installer.platform, "machine", return_value="arm64"):
            with self.assertRaisesRegex(ValueError, "unsupported"):
                installer.native_platform()

    def test_verified_raw_install_is_executable_and_scoped(self):
        payload = b"fixture bytes, never executed"
        with self.fake_http(payload):
            destination = installer.install("syft", manifest_for(payload), "darwin-arm64", self.root)
        self.assertEqual(destination, self.root / ".tools/bin/syft")
        self.assertEqual(destination.read_bytes(), payload)
        self.assertEqual(stat.S_IMODE(destination.stat().st_mode), 0o755)
        self.assertEqual(list(destination.parent.iterdir()), [destination])

    def test_checksum_failure_preserves_existing_binary(self):
        destination = self.root / ".tools/bin/syft"
        destination.parent.mkdir(parents=True)
        destination.write_bytes(b"previous verified binary")
        with self.fake_http(b"changed download"), self.assertRaisesRegex(ValueError, "SHA256 mismatch"):
            installer.install("syft", manifest_for(b"expected download"), "darwin-arm64", self.root)
        self.assertEqual(destination.read_bytes(), b"previous verified binary")

    def test_archive_extracts_only_exact_regular_binary(self):
        payload = archive_bytes([("LICENSE", b"license", tarfile.REGTYPE), ("syft", b"chosen binary", tarfile.REGTYPE)])
        with self.fake_http(payload):
            destination = installer.install("syft", manifest_for(payload, "syft"), "linux-amd64", self.root)
        self.assertEqual(destination.read_bytes(), b"chosen binary")
        self.assertEqual(list(destination.parent.iterdir()), [destination])

    def test_nested_archive_member_extracts_only_exact_file(self):
        payload = archive_bytes([
            ("../unrelated", b"ignored", tarfile.REGTYPE),
            ("linux-amd64/LICENSE", b"license", tarfile.REGTYPE),
            ("linux-amd64/syft", b"chosen binary", tarfile.REGTYPE),
        ])
        with self.fake_http(payload):
            destination = installer.install("syft", manifest_for(payload, "linux-amd64/syft"), "linux-amd64", self.root)
        self.assertEqual(destination.read_bytes(), b"chosen binary")
        self.assertEqual(list(self.root.iterdir()), [self.root / ".tools"])
        self.assertEqual(list(destination.parent.iterdir()), [destination])

    def test_official_helm_and_kubectl_urls_for_both_platforms(self):
        committed = json.loads(installer.MANIFEST.read_text())
        for name in ("helm", "kubectl"):
            for platform_name in installer.PLATFORMS:
                with self.subTest(name=name, platform_name=platform_name):
                    manifest = copy.deepcopy(committed)
                    pin = manifest["tools"][name]["platforms"][platform_name]
                    payload = archive_bytes([(pin["member"], b"chosen binary", tarfile.REGTYPE)]) if pin["member"] else b"chosen binary"
                    pin["sha256"] = hashlib.sha256(payload).hexdigest()
                    opener = Mock()
                    opener.open.return_value = io.BytesIO(payload)
                    with patch.object(installer, "build_opener", return_value=opener):
                        destination = installer.install(name, manifest, platform_name, self.root)
                    self.assertEqual(destination.read_bytes(), b"chosen binary")
                    request = opener.open.call_args.args[0]
                    self.assertEqual(request.full_url, pin["url"])

    def test_official_url_override_must_match_version_platform_and_members(self):
        committed = json.loads(installer.MANIFEST.read_text())
        bad_pins = [
            ("url", "https://example.com/helm-v3.22.0-darwin-arm64.tar.gz"),
            ("url", "http://get.helm.sh/helm-v3.22.0-darwin-arm64.tar.gz"),
            ("url", "https://get.helm.sh/helm-v3.21.4-darwin-arm64.tar.gz"),
            ("url", "https://get.helm.sh/helm-v3.22.0-linux-amd64.tar.gz"),
            ("url", "https://get.helm.sh/helm-v3.22.0-darwin-arm64.tar.gz?source=other"),
            ("url", None),
            ("asset", "other.tar.gz"),
            ("member", "linux-amd64/helm"),
        ]
        for key, value in bad_pins:
            manifest = copy.deepcopy(committed)
            manifest["tools"]["helm"]["platforms"]["darwin-arm64"][key] = value
            with self.subTest(key=key, value=value), patch.object(installer, "download_asset") as download:
                with self.assertRaises(ValueError):
                    installer.install("helm", manifest, "darwin-arm64", self.root)
                download.assert_not_called()

    def test_missing_or_unrelated_url_overrides_fail_before_download(self):
        manifest = json.loads(installer.MANIFEST.read_text())
        del manifest["tools"]["helm"]["platforms"]["darwin-arm64"]["url"]
        with patch.object(installer, "download_asset") as download, self.assertRaisesRegex(ValueError, "explicit"):
            installer.install("helm", manifest, "darwin-arm64", self.root)
        download.assert_not_called()
        manifest = manifest_for(b"data")
        manifest["tools"]["syft"]["platforms"]["linux-amd64"]["url"] = "https://github.com/anchore/syft/releases/download/v1.2.3/sample-bin"
        with patch.object(installer, "download_asset") as download, self.assertRaisesRegex(ValueError, "limited"):
            installer.install("syft", manifest, "linux-amd64", self.root)
        download.assert_not_called()

    def test_missing_duplicate_and_link_members_are_rejected(self):
        cases = [
            [("other", b"data", tarfile.REGTYPE)],
            [("syft", b"one", tarfile.REGTYPE), ("syft", b"two", tarfile.REGTYPE)],
            [("syft", b"", tarfile.SYMTYPE)],
            [("syft", b"", tarfile.LNKTYPE)],
        ]
        for entries in cases:
            with self.subTest(entries=entries):
                payload = archive_bytes(entries)
                with self.fake_http(payload), self.assertRaises(ValueError):
                    installer.install("syft", manifest_for(payload, "syft"), "linux-amd64", self.root)
                self.assertFalse((self.root / ".tools").exists())

    def test_invalid_manifest_paths_and_hashes_fail_before_download(self):
        for key, value in [("asset", "../asset"), ("sha256", "invalid"), ("member", "../binary")]:
            manifest = manifest_for(b"data")
            manifest["tools"]["syft"]["platforms"]["linux-amd64"][key] = value
            with self.subTest(key=key), patch.object(installer, "download_asset") as download:
                with self.assertRaises(ValueError):
                    installer.install("syft", manifest, "linux-amd64", self.root)
                download.assert_not_called()

    def test_archive_member_path_boundaries(self):
        invalid = ["/syft", "./syft", "../syft", "nested/../syft", "nested//syft", "nested/./syft", "nested/syft/", "nested\\syft", "a/b/c/d/syft", "a" * 257]
        for member in invalid:
            with self.subTest(member=member), patch.object(installer, "download_asset") as download:
                with self.assertRaises(ValueError):
                    installer.install("syft", manifest_for(b"data", member), "linux-amd64", self.root)
                download.assert_not_called()
        self.assertEqual(installer.validate_archive_member("a/b/c/syft"), "a/b/c/syft")
        self.assertEqual(installer.validate_archive_member("a" * 256), "a" * 256)

    def test_unknown_tool_does_not_contact_network(self):
        with patch.object(installer, "download_asset") as download, self.assertRaises(ValueError):
            installer.install("unknown", manifest_for(b"data"), "linux-amd64", self.root)
        download.assert_not_called()

    def test_download_size_limit_and_empty_response(self):
        with self.fake_http(b"123456789"), patch.object(installer, "MAX_DOWNLOAD", 8), self.assertRaisesRegex(ValueError, "size limit"):
            installer.install("syft", manifest_for(b"123456789"), "linux-amd64", self.root)
        with self.fake_http(b""), self.assertRaisesRegex(ValueError, "empty"):
            installer.install("syft", manifest_for(b""), "linux-amd64", self.root)
        self.assertFalse((self.root / ".tools").exists())

    def test_unapproved_redirect_rejected_without_network(self):
        redirect = installer.ReleaseRedirects()
        for url in ["http://github.com/release", "https://example.com/file", "https://github.com:444/file", "https://user@github.com/file", "https://dl.k8s.io.example.com/file", "https://get.helm.sh@evil.example/file", "\nhttps://github.com/file", "https://github.com/file\t", None]:
            with self.subTest(url=url), self.assertRaises(ValueError):
                redirect.redirect_request(None, None, 302, "Found", {}, url)
        self.assertEqual(installer.validate_url("https://release-assets.githubusercontent.com/file?signature=demo"), "https://release-assets.githubusercontent.com/file?signature=demo")
        for host in ("get.helm.sh", "dl.k8s.io", "cdn.dl.k8s.io"):
            self.assertEqual(installer.validate_url(f"https://{host}/file"), f"https://{host}/file")

    def test_symlink_destination_is_rejected(self):
        outside = self.root / "outside"
        outside.mkdir()
        (self.root / ".tools").symlink_to(outside, target_is_directory=True)
        with self.assertRaisesRegex(ValueError, "symlink"):
            installer.write_executable(self.root, "syft", b"data")
        self.assertEqual(list(outside.iterdir()), [])

    def test_atomic_failure_preserves_existing_binary_and_cleans_temp(self):
        destination = installer.write_executable(self.root, "syft", b"old")
        with patch.object(installer.os, "replace", side_effect=OSError("simulated failure")), self.assertRaises(OSError):
            installer.write_executable(self.root, "syft", b"new")
        self.assertEqual(destination.read_bytes(), b"old")
        self.assertEqual(list(destination.parent.iterdir()), [destination])


if __name__ == "__main__":
    unittest.main()
