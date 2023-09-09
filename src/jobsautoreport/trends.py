from typing import Optional, Union

from pydantic import BaseModel

from jobsautoreport.models import Report, SlackMessage, Trends


class TrendDetector(BaseModel):
    """Responsible for detecting differences in trends between two reports: `current_report` and `last_report`."""

    @staticmethod
    def subtract_optional_values(
        first_value: Optional[float], second_value: Optional[float]
    ) -> Optional[float]:
        return (
            first_value - second_value
            if first_value is not None and second_value is not None
            else None
        )

    def detect_trends(self, last_report: Report, current_report: Report) -> Trends:
        return Trends(
            number_of_e2e_or_subsystem_periodic_jobs=current_report.periodics_report.total
            - last_report.periodics_report.total,
            success_rate_for_e2e_or_subsystem_periodic_jobs=self.subtract_optional_values(
                current_report.periodics_report.success_rate,
                last_report.periodics_report.success_rate,
            ),
            number_of_e2e_or_subsystem_presubmit_jobs=current_report.presubmits_report.total
            - last_report.presubmits_report.total,
            success_rate_for_e2e_or_subsystem_presubmit_jobs=self.subtract_optional_values(
                current_report.presubmits_report.success_rate,
                last_report.presubmits_report.success_rate,
            ),
            number_of_rehearsal_jobs=current_report.presubmits_report.rehearsals
            - last_report.presubmits_report.rehearsals,
            number_of_postsubmit_jobs=current_report.postsubmits_report.total
            - last_report.postsubmits_report.total,
            success_rate_for_postsubmit_jobs=self.subtract_optional_values(
                current_report.postsubmits_report.success_rate,
                last_report.postsubmits_report.success_rate,
            ),
            total_number_of_machine_leased=current_report.equinix_usage_report.total_machines_leased
            - last_report.equinix_usage_report.total_machines_leased,
            number_of_unsuccessful_machine_leases=current_report.equinix_usage_report.unsuccessful_machine_leases
            - last_report.equinix_usage_report.unsuccessful_machine_leases,
            total_equinix_machines_cost=current_report.equinix_cost_report.total_equinix_machines_cost
            - last_report.equinix_cost_report.total_equinix_machines_cost,
        )


class TrendSlackIntegrator:
    """Integrates detected trends into Slack messages."""

    @classmethod
    def add_periodic_trends(cls, slack_message: SlackMessage, trends: Trends):
        text: str = slack_message[1]["text"]["text"]
        text = text.replace(
            "in total\n",
            f"in total  ({cls._get_sign_for_trend(trends.number_of_e2e_or_subsystem_periodic_jobs)}{trends.number_of_e2e_or_subsystem_periodic_jobs})\n",
        )
        if (
            "*success rate*" in text
            and trends.success_rate_for_e2e_or_subsystem_periodic_jobs is not None
        ):
            text = text.replace(
                "*success rate*\n",
                f"*success rate*  ({cls._get_sign_for_trend(trends.success_rate_for_e2e_or_subsystem_periodic_jobs)}{trends.success_rate_for_e2e_or_subsystem_periodic_jobs:.2f}%)\n",
            )
        slack_message[1]["text"]["text"] = text

    @classmethod
    def add_presubmit_trends(cls, slack_message: SlackMessage, trends: Trends):
        text: str = slack_message[2]["text"]["text"]
        text = text.replace(
            "in total\n",
            f"in total  ({cls._get_sign_for_trend(trends.number_of_e2e_or_subsystem_presubmit_jobs)}{trends.number_of_e2e_or_subsystem_presubmit_jobs})\n",
        )
        if (
            "*success rate*" in text
            and trends.success_rate_for_e2e_or_subsystem_presubmit_jobs is not None
        ):
            text = text.replace(
                "*success rate*\n",
                f"*success rate*  ({cls._get_sign_for_trend(trends.success_rate_for_e2e_or_subsystem_presubmit_jobs)}{trends.success_rate_for_e2e_or_subsystem_presubmit_jobs:.2f}%)\n",
            )
        slack_message[2]["text"]["text"] = text

        text = slack_message[3]["text"]["text"]
        text = text.replace(
            "rehearsal jobs triggered",
            f"rehearsal jobs triggered  ({cls._get_sign_for_trend(trends.number_of_rehearsal_jobs)}{trends.number_of_rehearsal_jobs})",
        )
        slack_message[3]["text"]["text"] = text

    @classmethod
    def add_postsubmit_trends(cls, slack_message: SlackMessage, trends: Trends):
        text: str = slack_message[2]["text"]["text"]
        text = text.replace(
            "in total\n",
            f"in total  ({cls._get_sign_for_trend(trends.number_of_postsubmit_jobs)}{trends.number_of_postsubmit_jobs})\n",
        )
        if (
            "*success rate*" in text
            and trends.success_rate_for_postsubmit_jobs is not None
        ):
            text = text.replace(
                "*success rate*\n",
                f"*success rate*  ({cls._get_sign_for_trend(trends.success_rate_for_postsubmit_jobs)}{trends.success_rate_for_postsubmit_jobs:.2f}%)\n",
            )
        slack_message[2]["text"]["text"] = text

    @classmethod
    def add_equinix_trends(cls, slack_message: SlackMessage, trends: Trends):
        text: str = slack_message[2]["text"]["text"]
        text = text.replace(
            "machine lease attempts\n",
            f"machine lease attempts  ({cls._get_sign_for_trend(trends.total_number_of_machine_leased)}{trends.total_number_of_machine_leased})\n",
        )
        text = text.replace(
            "failed\n",
            f"failed  ({cls._get_sign_for_trend(trends.number_of_unsuccessful_machine_leases)}{trends.number_of_unsuccessful_machine_leases})\n",
        )
        slack_message[2]["text"]["text"] = text

        text = slack_message[3]["text"]["text"]
        text = text.replace(
            "$*",
            f"$*  ({cls._get_sign_for_trend(trends.total_equinix_machines_cost)}{int(trends.total_equinix_machines_cost)} $)",
        )
        slack_message[3]["text"]["text"] = text

    @staticmethod
    def _get_sign_for_trend(trend: Union[float, int]) -> str:
        if trend > 0:
            return "+"
        return ""
