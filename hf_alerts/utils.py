from dataclasses import dataclass, field
from datetime import datetime


def get_availabilities(bookings, open, close):
    last_end_date = open
    availabilities = []
    for booking in bookings:
        if booking["band"] is None:
            continue
        availabilities.append(Availability(datetime.fromisoformat(last_end_date), datetime.fromisoformat(booking["start"])))
        last_end_date = booking["end"]
    availabilities.append(Availability(datetime.fromisoformat(last_end_date), datetime.fromisoformat(close)))
    return list(filter(lambda avail: avail.span > 0, availabilities))


def filter_availabilities(avail, length=2, min_size=0, name=None, start_time=None, end_time=None):
    avail = avail[avail["span"] >= length]
    avail = avail[avail["size"] >= min_size]
    if name: avail = avail[avail["name"] == name]
    if start_time: avail = avail[avail["start_time"] >= start_time]
    if end_time: avail = avail[avail["end_time"] <= end_time]
    return avail


@dataclass
class Availability:
    start: datetime
    end: datetime
    span: float = field(init=False)

    def __post_init__(self):
        self.span = round(((self.end - self.start).total_seconds())/3600, 1)

