from datetime import datetime
from unittest.mock import MagicMock

import pytest

from jobsautoreport.models import JobTypeMetrics, MachineMetrics
from jobsautoreport.report import Report
from jobsautoreport.trends import TrendDetector, Trends

mock_list = MagicMock(return_value=[1, 2, 3])


@pytest.fixture
def mock_current_report():
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        number_of_e2e_or_subsystem_periodic_jobs=0,
        number_of_successful_e2e_or_subsystem_periodic_jobs=0,
        number_of_failing_e2e_or_subsystem_periodic_jobs=0,
        success_rate_for_e2e_or_subsystem_periodic_jobs=None,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[],
        number_of_e2e_or_subsystem_presubmit_jobs=10,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=2,
        number_of_rehearsal_jobs=4,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=0.8,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[],
        top_5_most_triggered_e2e_or_subsystem_jobs=[],
        number_of_postsubmit_jobs=16,
        number_of_successful_postsubmit_jobs=8,
        number_of_failing_postsubmit_jobs=8,
        success_rate_for_postsubmit_jobs=0.5,
        top_10_failing_postsubmit_jobs=[],
        number_of_successful_machine_leases=16,
        number_of_unsuccessful_machine_leases=0,
        total_number_of_machine_leased=16,
    )


@pytest.fixture
def mock_last_report():
    return Report(
        from_date=datetime.now(),
        to_date=datetime.now(),
        number_of_e2e_or_subsystem_periodic_jobs=20,
        number_of_successful_e2e_or_subsystem_periodic_jobs=15,
        number_of_failing_e2e_or_subsystem_periodic_jobs=5,
        success_rate_for_e2e_or_subsystem_periodic_jobs=0.75,
        top_10_failing_e2e_or_subsystem_periodic_jobs=[],
        number_of_e2e_or_subsystem_presubmit_jobs=10,
        number_of_successful_e2e_or_subsystem_presubmit_jobs=8,
        number_of_failing_e2e_or_subsystem_presubmit_jobs=2,
        number_of_rehearsal_jobs=4,
        success_rate_for_e2e_or_subsystem_presubmit_jobs=0.8,
        top_10_failing_e2e_or_subsystem_presubmit_jobs=[],
        top_5_most_triggered_e2e_or_subsystem_jobs=[],
        number_of_postsubmit_jobs=0,
        number_of_successful_postsubmit_jobs=0,
        number_of_failing_postsubmit_jobs=0,
        success_rate_for_postsubmit_jobs=None,
        top_10_failing_postsubmit_jobs=[],
        number_of_successful_machine_leases=16,
        number_of_unsuccessful_machine_leases=0,
        total_number_of_machine_leased=16,
    )


@pytest.fixture
def mock_trend_detecter(mock_current_report: Report, mock_last_report: Report):
    return TrendDetector(
        current_report=mock_current_report,
        last_report=mock_last_report,
    )


def test_detect_trends(
    mock_trend_detecter: TrendDetector,
    mock_current_report: Report,
    mock_last_report: Report,
):
    trends = mock_trend_detecter.detect_trends()

    assert (
        trends.number_of_e2e_or_subsystem_periodic_jobs
        == mock_current_report.number_of_e2e_or_subsystem_periodic_jobs
        - mock_last_report.number_of_e2e_or_subsystem_periodic_jobs
    )
    assert trends.success_rate_for_e2e_or_subsystem_periodic_jobs is None
    assert (
        trends.number_of_e2e_or_subsystem_presubmit_jobs
        == mock_current_report.number_of_e2e_or_subsystem_presubmit_jobs
        - mock_last_report.number_of_e2e_or_subsystem_presubmit_jobs
    )
    assert (
        trends.success_rate_for_e2e_or_subsystem_presubmit_jobs
        == mock_current_report.success_rate_for_e2e_or_subsystem_presubmit_jobs
        - mock_last_report.success_rate_for_e2e_or_subsystem_presubmit_jobs
    )
    assert (
        trends.number_of_rehearsal_jobs
        == mock_current_report.number_of_rehearsal_jobs
        - mock_last_report.number_of_rehearsal_jobs
    )
    assert (
        trends.number_of_postsubmit_jobs
        == mock_current_report.number_of_postsubmit_jobs
        - mock_last_report.number_of_postsubmit_jobs
    )
    assert trends.success_rate_for_postsubmit_jobs is None
    assert (
        trends.total_number_of_machine_leased
        == mock_current_report.total_number_of_machine_leased
        - mock_last_report.total_number_of_machine_leased
    )
    assert (
        trends.number_of_unsuccessful_machine_leases
        == mock_current_report.number_of_unsuccessful_machine_leases
        - mock_last_report.number_of_unsuccessful_machine_leases
    )
