from enum import Enum
from typing import NewType

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


class MachineMetrics(BaseModel):
    metrics: dict[str, float]

    def is_zero(self) -> bool:
        return sum(self.metrics.values()) == 0
