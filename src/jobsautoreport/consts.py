from typing import Final

SECTION_DIVIDER: Final[dict[str, str]] = {"type": "divider"}
SUCCESS_EMOJI: Final[str] = ":done-circle-check:"
FAILURE_EMOJI: Final[str] = ":x:"
TOP_10_FAILED_PERIODIC_JOBS_TITLE: Final[str] = "Top 10 Failed Periodic Jobs"
TOP_10_FAILED_PRESUBMIT_JOBS_TITLE: Final[str] = "Top 10 Failed Presubmit Jobs"
TOP_5_TRIGGERED_PRESUBMIT_JOBS_TITLE: Final[str] = "Top 5 Triggered Presubmit Jobs"
TOP_10_FAILED_POSTSUBMIT_JOBS_TITLE: Final[str] = "Top 10 Failed Postsubmit Jobs"
PERIODIC_FLAKY_JOBS_TITLE: Final[str] = "Periodic Flaky Jobs"
REHEARSE: Final[str] = "rehearse"
RELEASE: Final[str] = "release"
OPENSHIFT: Final[str] = "openshift"
SUBSYSTEM: Final[str] = "subsystem"
E2E: Final[str] = "e2e"
ASSISTED_REPOSITORIES: Final[list[str]] = [
    "assisted-service",
    "assisted-installer",
    "assisted-installer-agent",
    "assisted-image-service",
    "assisted-test-infra",
    "cluster-api-provider-agent",
]
