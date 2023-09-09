import pytest

from jobsautoreport.models import FeatureFlags, Report, SlackMessage
from jobsautoreport.slack.slack_generate import SlackGenerator


@pytest.fixture
def expected_header_comment(mock_report_1: Report) -> SlackMessage:
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "CI Report",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*{mock_report_1.from_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\t:arrow_right:\t{mock_report_1.to_date.strftime('%Y-%m-%d %H:%M:%S')} UTC*\n",
            },
        },
    ]


@pytest.fixture
def expected_periodic_comment(mock_report_1: Report) -> SlackMessage:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Periodic e2e/subsystem jobs*\n",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"•\t _{mock_report_1.periodics_report.total}_ in total\n"
                    f" \t\t *-* :done-circle-check: {mock_report_1.periodics_report.successes} succeeded\n"
                    f" \t\t *-* :x: {mock_report_1.periodics_report.failures} failed\n"
                    f" \t  _{mock_report_1.periodics_report.success_rate:.2f}%_ *success rate*\n"
                ),
            },
        },
    ]


@pytest.fixture
def expected_presubmit_comment(mock_report_1: Report) -> SlackMessage:
    return [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Presubmit e2e/subsystem jobs*\n",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"•\t _{mock_report_1.presubmits_report.total}_ in total\n"
                    f" \t\t *-* :done-circle-check: {mock_report_1.presubmits_report.successes} succeeded\n"
                    f" \t\t *-* :x: {mock_report_1.presubmits_report.failures} failed\n"
                    f" \t  _{mock_report_1.presubmits_report.success_rate:.2f}%_ *success rate*\n"
                ),
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"•\t _{mock_report_1.presubmits_report.rehearsals}_ rehearsal jobs triggered",
            },
        },
    ]


@pytest.fixture
def expected_postsubmit_comment(mock_report_1: Report) -> SlackMessage:
    return [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Postsubmit jobs*\n",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"•\t _{mock_report_1.postsubmits_report.total}_ in total\n"
                    f" \t\t *-* :done-circle-check: {mock_report_1.postsubmits_report.successes} succeeded\n"
                    f" \t\t *-* :x: {mock_report_1.postsubmits_report.failures} failed\n"
                    f" \t  _{mock_report_1.postsubmits_report.success_rate:.2f}%_ *success rate*\n"
                ),
            },
        },
    ]


@pytest.fixture
def expected_equinix_comment(mock_report_1: Report) -> SlackMessage:
    return [
        {"type": "divider"},
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": "*Equinix*",
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": (
                    f"•\t _{mock_report_1.equinix_usage_report.total_machines_leased}_ machine lease attempts\n"
                    f" \t\t *-* :done-circle-check: {mock_report_1.equinix_usage_report.successful_machine_leases} succeeded\n"
                    f" \t\t *-* :x: {mock_report_1.equinix_usage_report.unsuccessful_machine_leases} failed\n"
                ),
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"•\t Total cost: *_{int(mock_report_1.equinix_cost_report.total_equinix_machines_cost)}_ $*",
            },
        },
    ]


def test_create_periodic_comment(
    expected_periodic_comment: SlackMessage, mock_report_1: Report
):
    assert (
        SlackGenerator().create_periodic_comment(
            periodics_report=mock_report_1.periodics_report
        )
        == expected_periodic_comment
    )


def test_create_presubmit_comment(
    expected_presubmit_comment: SlackMessage, mock_report_1: Report
):
    assert (
        SlackGenerator().create_presubmit_comment(
            presubmits_report=mock_report_1.presubmits_report
        )
        == expected_presubmit_comment
    )


def test_create_postubmit_comment(
    expected_postsubmit_comment: SlackMessage, mock_report_1: Report
):
    assert (
        SlackGenerator().create_postsubmit_comment(
            postsubmits_report=mock_report_1.postsubmits_report
        )
        == expected_postsubmit_comment
    )


def test_create_equinix_comment(
    expected_equinix_comment: SlackMessage, mock_report_1: Report
):
    assert (
        SlackGenerator().create_equinix_message(
            equinix_usage_report=mock_report_1.equinix_usage_report,
            equinix_cost_report=mock_report_1.equinix_cost_report,
            feature_flags=FeatureFlags(
                success_rates=True,
                equinix_usage=True,
                equinix_cost=True,
                trends=True,
                flakiness_rates=True,
            ),
        )
        == expected_equinix_comment
    )


def test_header_comment(expected_header_comment: SlackMessage, mock_report_1: Report):
    assert (
        SlackGenerator().create_header_message(report=mock_report_1)
        == expected_header_comment
    )
