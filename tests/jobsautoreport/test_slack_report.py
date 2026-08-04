from unittest.mock import MagicMock, patch

import pytest

from jobsautoreport.models import FeatureFlags, Report, Trends
from jobsautoreport.slack.slack_report import SlackReporter


@pytest.fixture
def mock_thread_time_stamp() -> dict[str, str]:
    return {"ts": "test-thread-time-stamp"}


@pytest.fixture
def slack_reporter(mock_thread_time_stamp) -> SlackReporter:
    test_channel = "test-channel"
    web_client_mock = MagicMock()
    response_mock = MagicMock()
    response_mock.validate.return_value = True
    response_mock.__getitem__.side_effect = mock_thread_time_stamp.__getitem__
    web_client_mock.chat_postMessage.return_value = response_mock
    web_client_mock.files_upload_v2.return_value = response_mock

    return SlackReporter(web_client=web_client_mock, channel_id=test_channel)


@pytest.fixture
def mock_trends() -> Trends:
    return Trends(
        number_of_e2e_or_subsystem_periodic_jobs=10,
        success_rate_for_e2e_or_subsystem_periodic_jobs=0.03,
        number_of_e2e_or_subsystem_presubmit_jobs=5,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=None,
        number_of_rehearsal_jobs=0,
        number_of_postsubmit_jobs=5,
        success_rate_for_postsubmit_jobs=-0.02,
    )


@pytest.fixture(autouse=True)
def mock_plotter() -> MagicMock:
    with patch("jobsautoreport.plot.Plotter") as plotter:
        plotter_graph_creation_returned_value = ("test-filename", "test-file-path")
        plotter.create_most_failing_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_most_triggered_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        plotter.create_flaky_jobs_graph.return_value = (
            plotter_graph_creation_returned_value
        )
        yield plotter


@pytest.fixture(autouse=True)
def mock_slack_generator() -> MagicMock:
    with patch("jobsautoreport.slack.slack_report.SlackGenerator") as slack_generator:
        yield slack_generator


@pytest.fixture(autouse=True)
def mock_trend_slack_integrator() -> MagicMock:
    with patch(
        "jobsautoreport.slack.slack_report.TrendSlackIntegrator"
    ) as trend_slack_integrator:
        yield trend_slack_integrator


def test__send_success_rates_with_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_success_rates(
        report=mock_report_1,
        trends=mock_trends,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )
    # periodics
    mock_slack_generator.create_periodic_comment.assert_called_once()
    mock_trend_slack_integrator.add_periodic_trends.assert_called_once()

    # presubmits
    mock_slack_generator.create_presubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_presubmit_trends.assert_called_once()

    # postsubmits
    mock_slack_generator.create_postsubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_postsubmit_trends.assert_called_once()

    # graphs
    assert mock_plotter.create_most_failing_jobs_graph.call_count == 3
    assert mock_plotter.create_most_triggered_jobs_graph.call_count == 1
    assert slack_reporter._client.files_upload_v2.call_count == 4

    # messages
    assert slack_reporter._client.chat_postMessage.call_count == 3


def test__send_success_rates_without_trends(
    mock_report_1: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    mock_slack_generator: MagicMock,
    slack_reporter: SlackReporter,
    mock_trend_slack_integrator: MagicMock,
):
    slack_reporter._send_success_rates(
        report=mock_report_1,
        trends=None,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )
    # periodics
    mock_slack_generator.create_periodic_comment.assert_called_once()
    mock_trend_slack_integrator.add_periodic_trends.assert_not_called()

    # presubmits
    mock_slack_generator.create_presubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_presubmit_trends.assert_not_called()

    # postsubmits
    mock_slack_generator.create_postsubmit_comment.assert_called_once()
    mock_trend_slack_integrator.add_postsubmit_trends.assert_not_called()

    # graphs
    assert mock_plotter.create_most_failing_jobs_graph.call_count == 3
    assert mock_plotter.create_most_triggered_jobs_graph.call_count == 1
    assert slack_reporter._client.files_upload_v2.call_count == 4

    # messages
    assert slack_reporter._client.chat_postMessage.call_count == 3


def test__send_flakiness_rates_with_flaky_jobs(
    mock_report_1: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    slack_reporter: SlackReporter,
):
    slack_reporter._send_flakiness_rates(
        report=mock_report_1,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_plotter.create_flaky_jobs_graph.assert_called_once()
    slack_reporter._client.files_upload_v2.assert_called_once()


def test__send_flakiness_rates_without_flaky_jobs(
    mock_report_2: Report,
    mock_plotter: MagicMock,
    mock_thread_time_stamp: dict[str, str],
    slack_reporter: SlackReporter,
):
    slack_reporter._send_flakiness_rates(
        report=mock_report_2,
        plotter=mock_plotter,
        thread_time_stamp=mock_thread_time_stamp["ts"],
    )

    mock_plotter.create_flaky_jobs_graph.assert_not_called()
    slack_reporter._client.files_upload_v2.assert_not_called()


def test_send_report_with_all_features(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits
    assert slack_reporter._client.chat_postMessage.call_count == 4

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph
    assert slack_reporter._client.files_upload_v2.call_count == 5


def test_send_report_with_all_features_but_success_rate(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=False,
        trends=True,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header
    assert slack_reporter._client.chat_postMessage.call_count == 1

    # (flaky jobs) graph
    assert slack_reporter._client.files_upload_v2.call_count == 1


def test_send_report_with_all_features_but_trends(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        trends=False,
        flakiness_rates=True,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits
    assert slack_reporter._client.chat_postMessage.call_count == 4

    # 3 (top 10 failing) graphs, (top 5 triggered) graph, (flaky jobs) graph
    assert slack_reporter._client.files_upload_v2.call_count == 5


def test_send_report_with_all_features_but_flakiness_rates(
    mock_report_1: Report,
    mock_trends: Trends,
    slack_reporter: SlackReporter,
):
    feature_flags = FeatureFlags(
        success_rates=True,
        trends=True,
        flakiness_rates=False,
    )

    slack_reporter.send_report(
        report=mock_report_1, trends=mock_trends, feature_flags=feature_flags
    )

    # header, periodics, presubmits, postsubmits
    assert slack_reporter._client.chat_postMessage.call_count == 4

    # 3 (top 10 failing) graphs, (top 5 triggered) graph
    assert slack_reporter._client.files_upload_v2.call_count == 4
