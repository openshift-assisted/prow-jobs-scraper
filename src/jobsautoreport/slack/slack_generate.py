from jobsautoreport.consts import FAILURE_EMOJI, SECTION_DIVIDER, SUCCESS_EMOJI
from jobsautoreport.models import (
    EquinixCostReport,
    EquinixUsageReport,
    FeatureFlags,
    PeriodicJobsReport,
    PostSubmitJobsReport,
    PresubmitJobsReport,
    Report,
    SlackMessage,
)


class SlackGenerator:
    @staticmethod
    def create_periodic_comment(periodics_report: PeriodicJobsReport) -> SlackMessage:
        text = (
            f"•\t _{periodics_report.total}_ in total\n"
            f" \t\t *-* {SUCCESS_EMOJI} {periodics_report.successes} succeeded\n"
            f" \t\t *-* {FAILURE_EMOJI} {periodics_report.failures} failed\n"
        )

        if periodics_report.success_rate is not None:
            text += f" \t  _{periodics_report.success_rate:.2f}%_ *success rate*\n"

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
                "text": {"type": "mrkdwn", "text": text},
            },
        ]

    @staticmethod
    def create_presubmit_comment(
        presubmits_report: PresubmitJobsReport,
    ) -> SlackMessage:
        text = (
            f"•\t _{presubmits_report.total}_ in total\n"
            f" \t\t *-* {SUCCESS_EMOJI} {presubmits_report.successes} succeeded\n"
            f" \t\t *-* {FAILURE_EMOJI} {presubmits_report.failures} failed\n"
        )

        if presubmits_report.success_rate is not None:
            text += f" \t  _{presubmits_report.success_rate:.2f}%_ *success rate*\n"

        return [
            SECTION_DIVIDER,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Presubmit e2e/subsystem jobs*\n",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"•\t _{presubmits_report.rehearsals}_ rehearsal jobs triggered",
                },
            },
        ]

    @staticmethod
    def create_postsubmit_comment(
        postsubmits_report: PostSubmitJobsReport,
    ) -> SlackMessage:
        text = (
            f"•\t _{postsubmits_report.total}_ in total\n"
            f" \t\t *-* {SUCCESS_EMOJI} {postsubmits_report.successes} succeeded\n"
            f" \t\t *-* {FAILURE_EMOJI} {postsubmits_report.failures} failed\n"
        )

        if postsubmits_report.success_rate is not None:
            text += f" \t  _{postsubmits_report.success_rate:.2f}%_ *success rate*\n"

        return [
            SECTION_DIVIDER,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Postsubmit jobs*\n",
                },
            },
            {
                "type": "section",
                "text": {"type": "mrkdwn", "text": text},
            },
        ]

    @staticmethod
    def create_equinix_message(
        equinix_usage_report: EquinixUsageReport,
        equinix_cost_report: EquinixCostReport,
        feature_flags: FeatureFlags,
    ) -> SlackMessage:
        message: SlackMessage = [
            SECTION_DIVIDER,
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "*Equinix*",
                },
            },
        ]
        if feature_flags.equinix_usage:
            message += [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": (
                            f"•\t _{equinix_usage_report.total_machines_leased}_ machine lease attempts\n"
                            f" \t\t *-* {SUCCESS_EMOJI} {equinix_usage_report.successful_machine_leases} succeeded\n"
                            f" \t\t *-* {FAILURE_EMOJI} {equinix_usage_report.unsuccessful_machine_leases} failed\n"
                        ),
                    },
                },
            ]
        if feature_flags.equinix_cost:
            message += [
                {
                    "type": "section",
                    "text": {
                        "type": "mrkdwn",
                        "text": f"•\t Total cost: *_{int(equinix_cost_report.total_equinix_machines_cost)}_ $*",
                    },
                },
            ]

        return message

    @staticmethod
    def create_header_message(
        report: Report,
    ) -> SlackMessage:
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
                    "text": f"*{report.from_date.strftime('%Y-%m-%d %H:%M:%S')} UTC\t:arrow_right:\t{report.to_date.strftime('%Y-%m-%d %H:%M:%S')} UTC*\n",
                },
            },
        ]
