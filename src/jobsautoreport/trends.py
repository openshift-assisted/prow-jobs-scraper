from typing import Final, Optional

from pydantic import BaseModel

from jobsautoreport.report import Report

COMPARED_FIELDS: Final[list[str]] = [
    "number_of_e2e_or_subsystem_periodic_jobs",
    "success_rate_for_e2e_or_subsystem_periodic_jobs",
    "number_of_e2e_or_subsystem_presubmit_jobs",
    "success_rate_for_e2e_or_subsystem_presubmit_jobs",
    "number_of_rehearsal_jobs",
    "number_of_postsubmit_jobs",
    "success_rate_for_postsubmit_jobs",
    "total_number_of_machine_leased",
    "number_of_unsuccessful_machine_leases",
]


class Trends(BaseModel):
    number_of_e2e_or_subsystem_periodic_jobs: int
    success_rate_for_e2e_or_subsystem_periodic_jobs: Optional[float]
    number_of_e2e_or_subsystem_presubmit_jobs: int
    success_rate_for_e2e_or_subsystem_presubmit_jobs: Optional[float]
    number_of_rehearsal_jobs: int
    number_of_postsubmit_jobs: int
    success_rate_for_postsubmit_jobs: Optional[float]
    total_number_of_machine_leased: int
    number_of_unsuccessful_machine_leases: int


class TrendDetector(BaseModel):
    current_report: Report
    last_report: Report

    def detect_trends(self) -> Trends:
        trends = {}

        for field in COMPARED_FIELDS:
            if (
                current_report_field_value := getattr(self.current_report, field)
            ) is not None and (
                last_report_field_value := getattr(self.last_report, field)
            ) is not None:
                trends[field] = current_report_field_value - last_report_field_value

        return Trends.parse_obj(trends)
