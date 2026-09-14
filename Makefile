PYTHON ?= python3
VENV_PYTHON := .venv/bin/python
IMAGE ?= devsecops-reference:local
export PATH := $(CURDIR)/.tools/bin:$(PATH)

.PHONY: setup test validate run container container-test sbom sast policy-test runtime-test metrics metrics-serve

setup:
	$(PYTHON) -m venv .venv
	$(VENV_PYTHON) -m pip install --require-hashes -r requirements-dev.txt

test:
	$(VENV_PYTHON) -m unittest discover -s tests -p 'test_*.py' -v
	$(VENV_PYTHON) -m unittest discover -s repo-templates -p 'test_*.py' -v
	$(MAKE) runtime-test

validate:
	$(VENV_PYTHON) scripts/validate_repository.py

run:
	$(VENV_PYTHON) samples/sample-api/app.py

container:
	docker build --pull -t $(IMAGE) samples/sample-api

container-test:
	$(VENV_PYTHON) scripts/container_smoke.py --image $(IMAGE)

sbom:
	mkdir -p reports
	syft --config configs/syft.yaml docker:$(IMAGE) -o cyclonedx-json=reports/sbom.cdx.json

sast:
	mkdir -p reports
	semgrep scan --config configs/semgrep.yml --error --metrics off --json-output reports/semgrep.json samples

policy-test:
	bash policies/verify.sh

runtime-test:
	$(VENV_PYTHON) -m unittest discover -s labs/lab-05-runtime-detection -p 'test_*.py' -v

metrics:
	$(VENV_PYTHON) scripts/metrics.py

metrics-serve:
	$(VENV_PYTHON) scripts/metrics.py --serve --port 9108
