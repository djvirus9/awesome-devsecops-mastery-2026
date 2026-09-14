"""Offline contracts: no Docker daemon, network requests or renderer required."""

import importlib.util
from pathlib import Path
import struct
import subprocess
import tempfile
import unittest
from unittest.mock import patch
import zlib

SPEC = importlib.util.spec_from_file_location(
    "dashboard_validation", Path(__file__).resolve().parents[1] / "scripts/validate_dashboard.py")
dashboard = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(dashboard)


def prometheus_sample(value):
    return {"status": "success", "data": {"resultType": "vector",
            "result": [{"metric": {}, "value": [1, str(value)]}]}}


def grafana_samples():
    return {"results": {str(key): {"status": 200, "frames": [{
        "schema": {"fields": [{"type": "time"}, {"type": "number"}]},
        "data": {"values": [[1000], [value]]}}]}
        for key, value in dashboard.EXPECTED.items()}}


def chunk(kind, data):
    return struct.pack(">I", len(data)) + kind + data + struct.pack(">I", zlib.crc32(kind + data))


def png():
    return (b"\x89PNG\r\n\x1a\n" +
            chunk(b"IHDR", struct.pack(">IIBBBBB", 150, 150, 8, 0, 0, 0, 0)) +
            chunk(b"IDAT", zlib.compress((b"\x00" + b"\x00" * 150) * 150)) +
            chunk(b"IEND", b""))


class DashboardValidationTests(unittest.TestCase):
    def test_prometheus_requires_one_finite_expected_sample(self):
        self.assertEqual(dashboard.prometheus_value(prometheus_sample(64800), 64800), 64800)
        for value in [0, float("nan"), float("inf")]:
            with self.subTest(value=value), self.assertRaises(ValueError):
                dashboard.prometheus_value(prometheus_sample(value), 64800)
        response = prometheus_sample(64800)
        response["data"]["result"] *= 2
        with self.assertRaises(ValueError):
            dashboard.prometheus_value(response, 64800)

    def test_grafana_requires_all_three_expected_frames(self):
        self.assertEqual(dashboard.grafana_values(grafana_samples()),
                         {"1": 64800, "2": 1200, "3": 2})
        for replacement in [None, 0, True, float("nan")]:
            response = grafana_samples()
            response["results"]["1"]["frames"][0]["data"]["values"][1] = [replacement]
            with self.subTest(value=replacement), self.assertRaises((TypeError, ValueError)):
                dashboard.grafana_values(response)
        with self.assertRaises(ValueError):
            dashboard.grafana_values({"results": {}})

    def test_grafana_error_and_multiple_samples_fail(self):
        response = grafana_samples()
        response["results"]["1"]["error"] = "query failed"
        with self.assertRaises(ValueError):
            dashboard.grafana_values(response)
        response = grafana_samples()
        response["results"]["1"]["frames"] *= 2
        with self.assertRaises(ValueError):
            dashboard.grafana_values(response)

    def test_png_structure_checksum_and_end_marker(self):
        self.assertEqual(dashboard.png_dimensions(png()), (150, 150))
        for payload in [b"not an image", png()[:-1], png() + b"unexpected",
                        png()[:40] + b"bad" + png()[43:]]:
            with self.subTest(payload=payload[:12]), self.assertRaises(ValueError):
                dashboard.png_dimensions(payload)

    def test_fetch_refuses_remote_hosts_without_network(self):
        with patch.object(dashboard.urllib.request, "build_opener") as opener:
            for url in ["http://example.com:3000", "https://127.0.0.1:3000",
                        "http://127.0.0.1:3000@elsewhere"]:
                with self.subTest(url=url), self.assertRaises(ValueError):
                    dashboard.fetch(url, "/api/health", "unused")
            opener.assert_not_called()

    def test_redirect_is_rejected(self):
        with self.assertRaisesRegex(RuntimeError, "redirect"):
            dashboard.NoRedirect().redirect_request(None, None, 302, "", {}, "https://example.com")

    def test_fixture_contains_only_explicit_synthetic_inputs(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            result = dashboard.prepare_fixture(directory)
            self.assertEqual(len(result["panels"]), 3)
            files = sorted(str(path.relative_to(directory)) for path in directory.rglob("*") if path.is_file())
            self.assertEqual(len(files), 7)
            self.assertNotIn("samples/sample-api/app.py", files)
            self.assertEqual((directory.stat().st_mode & 0o777), 0o755)
            self.assertIn("http://127.0.0.1:9090", (directory / "provisioning/datasources/demo.yaml").read_text())

    def test_exact_ids_tracked_before_start_failure(self):
        container = "a" * 64
        with tempfile.TemporaryDirectory() as temporary:
            services = dashboard.Services(Path(temporary), Path(temporary))
            with patch.object(dashboard, "docker", side_effect=[container, RuntimeError("start failed")]):
                with self.assertRaisesRegex(RuntimeError, "start failed"):
                    services.create("exporter")
            self.assertEqual(services.containers, [("exporter", container)])

    def test_cleanup_only_removes_created_ids_and_redacts_logs(self):
        container, network = "a" * 64, "b" * 64
        with tempfile.TemporaryDirectory() as temporary:
            services = dashboard.Services(Path(temporary), Path(temporary))
            services.containers = [("exporter", container)]
            services.network = network
            services.redactions = ["synthetic-private-value"]
            fake = subprocess.CompletedProcess([], 0, "synthetic-private-value", "stderr evidence")
            with patch.object(dashboard, "docker", return_value="") as docker_mock, \
                    patch.object(dashboard.subprocess, "run", return_value=fake):
                self.assertEqual(services.cleanup(), [])
            self.assertEqual(docker_mock.call_args_list[0].args, ("rm", "--force", container))
            self.assertEqual(docker_mock.call_args_list[1].args, ("network", "rm", network))
            self.assertNotIn("synthetic-private-value", (Path(temporary) / "exporter.log").read_text())

    def test_all_test_images_are_digest_pinned(self):
        self.assertEqual(set(dashboard.IMAGES), {"exporter", "grafana", "prometheus", "renderer"})
        for image in dashboard.IMAGES.values():
            self.assertRegex(image, r"@sha256:[a-f0-9]{64}$")

    def test_docker_helper_uses_fixed_environment_without_remote_overrides(self):
        fake = subprocess.CompletedProcess([], 0, "ok", "")
        with patch.object(dashboard.subprocess, "run", return_value=fake) as runner:
            self.assertEqual(dashboard.docker("info"), "ok")
        environment = runner.call_args.kwargs["env"]
        for name in ("DOCKER_HOST", "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
            self.assertNotIn(name, environment)


if __name__ == "__main__":
    unittest.main()
