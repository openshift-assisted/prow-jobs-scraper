from datetime import datetime

from jobsautoreport.query import Querier


class Reporter:
    def __init__(self, querier: Querier):
        self._querier = querier

    def get_success_rate(self, from_date: datetime, to_date: datetime) -> str:
        successfull_jobs_list = self._querier.query_successfull_jobs(from_date, to_date)
        unsuccessfull_jobs_list = self._querier.query_successfull_jobs(
            from_date, to_date
        )
        if len(successfull_jobs_list) == 0:
            return "0"
        return f"{(len(successfull_jobs_list) / (len(unsuccessfull_jobs_list) + len(successfull_jobs_list))) * 100}%"

    def get_number_of_jobs_triggered(
        self, from_date: datetime, to_date: datetime
    ) -> int:
        jobs_list = self._querier.query_number_of_jobs_triggered(from_date, to_date)
        return len(jobs_list)

    def get_average_duration_of_jobs(
        self, from_date: datetime, to_date: datetime
    ) -> float:
        jobs_list = self._querier.query_number_of_jobs_triggered(from_date, to_date)
        if len(jobs_list) == 0:
            return 0
        avg = sum([job.duration for job in jobs_list]) / len(jobs_list)
        return avg
