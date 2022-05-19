CONTAINER_CMD := $(or $(CONTAINER_CMD), $(shell command -v podman 2> /dev/null))
ifndef CONTAINER_CMD
CONTAINER_CMD := docker
endif

PROW_JOBS_SCRAPER_IMAGE := $(or $(PROW_JOBS_SCRAPER_IMAGE),quay.io/edge-infrastructure/prow-jobs-scraper)
PROW_JOBS_SCRAPER_TAG := $(or $(PROW_JOBS_SCRAPER_TAG),latest)

install:
	pip install .

install-lint:
	pip install .[lint]

install-unit-tests:
	pip install .[test-runner]

full-install: install install-lint install-unit-tests

unit-tests:
	tox

format:
	black src/ tests/
	isort src tests/

mypy:
	mypy --non-interactive --install-types src/

lint-manifest:
	oc process --local=true -f openshift/template.yaml --param IMAGE_TAG=foobar | oc apply --dry-run=client --validate -f -

lint: mypy format
	git diff --exit-code

build-image:
	$(CONTAINER_CMD) build $(CONTAINER_BUILD_EXTRA_PARAMS) -t $(PROW_JOBS_SCRAPER_IMAGE):$(PROW_JOBS_SCRAPER_TAG) .

.PHONY: install install-lint install-unit-tests full-install unit-tests format mypy lint lint-manifest build-image
