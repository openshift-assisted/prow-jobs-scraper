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
    presubmit: float = 0.0
    periodic: float = 0.0
    postsubmit: float = 0.0
    batch: float = 0.0


class JobMetrics(Metric):
    successes: int
    failures: int
    cost: float

    @property
    def total(self) -> int:
        return self.successes + self.failures

    @property
    def failure_rate(self) -> Optional[float]:
        return None if self.total == 0 else (self.failures / self.total) * 100

    @property
    def success_rate(self) -> Optional[float]:
        return None if self.failure_rate is None else 100 - self.failure_rate
