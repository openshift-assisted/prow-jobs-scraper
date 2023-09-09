from jobsautoreport.models import Report
from jobsautoreport.trends import TrendDetector, TrendSlackIntegrator


def test_detect_trends(
    mock_report_1: Report,
    mock_report_2: Report,
):
    trends = TrendDetector().detect_trends(
        last_report=mock_report_2, current_report=mock_report_1
    )

    assert (
        trends.number_of_e2e_or_subsystem_periodic_jobs
        == mock_report_1.periodics_report.total - mock_report_2.periodics_report.total
    )
    assert (
        trends.success_rate_for_e2e_or_subsystem_periodic_jobs
        == mock_report_1.periodics_report.success_rate
        - mock_report_2.periodics_report.success_rate
    )
    assert (
        trends.number_of_e2e_or_subsystem_presubmit_jobs
        == mock_report_1.presubmits_report.total - mock_report_2.presubmits_report.total
    )
    assert (
        trends.success_rate_for_e2e_or_subsystem_presubmit_jobs
        == mock_report_1.presubmits_report.success_rate
        - mock_report_2.presubmits_report.success_rate
    )
    assert (
        trends.number_of_rehearsal_jobs
        == mock_report_1.presubmits_report.rehearsals
        - mock_report_2.presubmits_report.rehearsals
    )
    assert (
        trends.number_of_postsubmit_jobs
        == mock_report_1.postsubmits_report.total
        - mock_report_2.postsubmits_report.total
    )
    assert trends.success_rate_for_postsubmit_jobs is None
    assert (
        trends.total_number_of_machine_leased
        == mock_report_1.equinix_usage_report.total_machines_leased
        - mock_report_2.equinix_usage_report.total_machines_leased
    )
    assert (
        trends.number_of_unsuccessful_machine_leases
        == mock_report_1.equinix_usage_report.unsuccessful_machine_leases
        - mock_report_2.equinix_usage_report.unsuccessful_machine_leases
    )


def test_get_sign_for_trend():
    assert TrendSlackIntegrator()._get_sign_for_trend(trend=1) == "+"
    assert TrendSlackIntegrator()._get_sign_for_trend(trend=0) == ""
    assert TrendSlackIntegrator()._get_sign_for_trend(trend=-1) == ""
