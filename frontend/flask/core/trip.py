from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trip():

    trip_id: int
    start_date: datetime
    end_date: datetime
