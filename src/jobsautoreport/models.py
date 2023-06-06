from enum import Enum
from typing import NewType, Optional

from pydantic import BaseModel


class JobType(Enum):
    PRESUBMIT = "presubmit"
    POSTSUBMIT = "postsubmit"
    PERIODIC = "periodic"
    BATCH = "batch"


class JobState(Enum):
    SUCCESS = "success"
    FAILURE = "failure"


StepState = NewType("StepState", JobState)(JobState)


class ReportInterval(Enum):
    WEEK = "week"
    MONTH = "month"


class Metric(BaseModel):
    def is_zero(self) -> bool:
        for cost in self.dict().values():
            if cost > 0:
                return False
        return True


class MachineMetrics(Metric):
    metrics: dict[str, float]

    def is_zero(self) -> bool:
        return sum(self.metrics.values()) == 0


class JobTypeMetrics(Metric):
    metrics: dict[str, float]

    def is_zero(self) -> bool:
        return sum(self.metrics.values()) == 0


class JobMetrics(Metric):
    successes: int
    failures: int
    cost: float
    flakiness: Optional[float]
    flakiness_threshold: float = 0.5

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def failure_rate(self) -> Optional[float]:
        return None if self.total == 0 else (self.failures / self.total) * 100

    @property
    def success_rate(self) -> Optional[float]:
        return None if self.failure_rate is None else 100 - self.failure_rate

    def is_flaky(self) -> Optional[bool]:
        return (
            self.flakiness > self.flakiness_threshold and self.total >= 5
            if self.flakiness is not None
            else None
        )
