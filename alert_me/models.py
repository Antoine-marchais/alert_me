from dataclasses import dataclass, field
from datetime import datetime


@dataclass
class User:
    name: str
    id: int


@dataclass
class Alert:
    start_time: datetime
    end_time: datetime
    min_span: float
    min_size: float


@dataclass
class Availability:
    start: datetime
    end: datetime
    span: float = field(init=False)

    def __post_init__(self):
        self.span = round(((self.end - self.start).total_seconds())/3600, 1)
