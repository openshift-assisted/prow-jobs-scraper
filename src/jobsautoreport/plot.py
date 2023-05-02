import logging

import plotly.graph_objects as graph_objects  # type: ignore
from plotly import express

from jobsautoreport.report import IdentifiedJobMetrics, JobIdentifier

logger = logging.getLogger(__name__)


class Plotter:
    def create_most_failing_jobs_graph(
        self,
        jobs: list[IdentifiedJobMetrics],
        file_title: str,
    ) -> tuple[str, str]:
        is_variant_unique = JobIdentifier.is_variant_unique(
            [identified_job_metrics.job_identifier for identified_job_metrics in jobs]
        )
        names = [
            identified_job_metrics.job_identifier.get_slack_name(is_variant_unique)
            for identified_job_metrics in jobs
        ]
        successes = [
            identified_job_metrics.metrics.successes for identified_job_metrics in jobs
        ]
        failures = [
            identified_job_metrics.metrics.failures for identified_job_metrics in jobs
        ]

        filename, file_path = self._file_name_proccesor(file_title=file_title)
        fig = graph_objects.Figure()
        fig.add_trace(
            graph_objects.Bar(
                x=successes,
                y=names,
                name="succeeded",
                orientation="h",
                marker=dict(
                    color=list(reversed(express.colors.sequential.Greens)),
                ),
                text=successes,
                textposition="auto",
                textfont=dict(size=14, color="white"),
            )
        )

        fig.add_trace(
            graph_objects.Bar(
                x=failures,
                y=names,
                name="failed",
                orientation="h",
                marker=dict(
                    color=express.colors.sequential.Reds,
                ),
                text=failures,
                textposition="auto",
                textfont=dict(size=14, color="white"),
            )
        )

        fig.update_layout(
            barmode="stack",
            title_text=file_title,
            font_family="Arial",
            font_size=12,
            xaxis_title="Trigger Count",
            yaxis_title="Job",
            yaxis=dict(
                tickfont=dict(size=10),
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
            ),
        )

        fig.write_image(file_path, scale=3)
        logger.info("image created at %s successfully", file_path)

        return filename, file_path

    def create_most_triggered_jobs_graph(
        self, jobs: list[IdentifiedJobMetrics], file_title: str
    ) -> tuple[str, str]:
        is_variant_unique = JobIdentifier.is_variant_unique(
            [identified_job_metrics.job_identifier for identified_job_metrics in jobs]
        )
        names = [
            identified_job_metrics.job_identifier.get_slack_name(is_variant_unique)
            for identified_job_metrics in jobs
        ]
        quantities = [
            identified_job_metrics.metrics.total for identified_job_metrics in jobs
        ]

        filename, file_path = self._file_name_proccesor(file_title=file_title)
        fig = graph_objects.Figure()
        fig.add_trace(
            graph_objects.Bar(
                x=quantities,
                y=names,
                name="Quantity",
                orientation="h",
                marker=dict(
                    color=express.colors.sequential.Agsunset,
                    line=dict(color="rgba(0, 0, 0, 0.5)", width=1),
                ),
                text=quantities,
                textposition="auto",
                textfont=dict(size=14, color="white"),
            )
        )

        fig.update_layout(
            title_text=file_title,
            font_family="Arial",
            font_size=12,
            xaxis_title="Trigger Count",
            yaxis_title="Job",
            yaxis=dict(
                tickfont=dict(size=10),
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
            ),
        )

        fig.write_image(file_path, scale=3)
        logger.info("image created at %s successfully", file_path)

        return filename, file_path

    def create_most_expensive_jobs_graph(
        self,
        jobs: list[IdentifiedJobMetrics],
        file_title: str,
    ) -> tuple[str, str]:
        is_variant_unique = JobIdentifier.is_variant_unique(
            [identified_job_metrics.job_identifier for identified_job_metrics in jobs]
        )
        names = [
            identified_job_metrics.job_identifier.get_slack_name(is_variant_unique)
            for identified_job_metrics in jobs
        ]
        costs = [identified_job_metrics.metrics.cost for identified_job_metrics in jobs]
        filename, file_path = self._file_name_proccesor(file_title=file_title)
        fig = graph_objects.Figure()

        fig.add_trace(
            graph_objects.Bar(
                x=costs,
                y=names,
                name="Cost",
                orientation="h",
                marker=dict(
                    color=express.colors.sequential.Plasma,
                    line=dict(color="rgba(0, 0, 0, 0.5)", width=1),
                ),
                text=[int(cost) for cost in costs],
                textposition="inside",
                textfont=dict(color="white"),
            )
        )

        fig.update_layout(
            title_text=file_title,
            font_family="Arial",
            font_size=12,
            xaxis_title="Cost (USD)",
            yaxis_title="Job",
            yaxis=dict(
                tickfont=dict(size=10),
                showgrid=True,
                gridwidth=1,
                gridcolor="lightgray",
            ),
        )

        fig.write_image(file_path, scale=3)
        logger.info("image created at %s successfully", file_path)

        return filename, file_path

    @staticmethod
    def _file_name_proccesor(file_title: str) -> tuple[str, str]:
        filename = file_title.replace(" ", "_").lower()
        file_path = f"/tmp/{filename}.png"
        return filename, file_path
