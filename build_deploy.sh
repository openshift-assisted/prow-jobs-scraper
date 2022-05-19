#!/usr/bin/env bash

set -xeuo pipefail

if command -v podman
then
    CONTAINER_CMD="podman"
else
    CONTAINER_CMD="docker"
fi
export CONTAINER_CMD
echo "Using ${CONTAINER_CMD} as container engine..."

export CONTAINER_BUILD_EXTRA_PARAMS=${CONTAINER_BUILD_EXTRA_PARAMS:-"--no-cache"}
export PROW_JOBS_SCRAPER_IMAGE=${PROW_JOBS_SCRAPER_IMAGE:-"quay.io/app-sre/prow-jobs-scraper"}

# Tag with the current commit sha
PROW_JOBS_SCRAPER_TAG="$(git rev-parse --short=7 HEAD)"
export PROW_JOBS_SCRAPER_TAG

# Setup credentials to image registry
${CONTAINER_CMD} login -u="${QUAY_USER}" -p="${QUAY_TOKEN}" quay.io

# Build and push latest image
make build-image

PROW_JOBS_SCRAPER_IMAGE_COMMIT_SHA="${PROW_JOBS_SCRAPER_IMAGE}:${PROW_JOBS_SCRAPER_TAG}"
${CONTAINER_CMD} push "${PROW_JOBS_SCRAPER_IMAGE_COMMIT_SHA}"

# Tag the image as latest
PROW_JOBS_SCRAPER_IMAGE_LATEST="${PROW_JOBS_SCRAPER_IMAGE}:latest"
${CONTAINER_CMD} tag "${PROW_JOBS_SCRAPER_IMAGE_COMMIT_SHA}" "${PROW_JOBS_SCRAPER_IMAGE_LATEST}"
${CONTAINER_CMD} push "${PROW_JOBS_SCRAPER_IMAGE_COMMIT_SHA}"
