from dataclasses import dataclass
from datetime import datetime


@dataclass
class Trip():

    trip_id: int
    start_date: datetime
    end_date: datetime

    def intersects(self, trip):
        return self.contains(trip.start_date) or self.contains(trip.end_date)

    def contains_any(self, dates):
        return sum([self.contains(d) for d in dates])

    def contains(self, date):
        return self.start_date <= date and self.end_date >= date

    def consistent(self):
        return self.start_date < self.end_date

    @classmethod
    def from_strs(cls, trip_id: str, state: str,
                  start_date: str, end_date: str):

        try:
            trip_id = int(trip_id)
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        except Exception as e:
            print("Trip creation error: " + str(e))
            trip_id = None
            start_date = None
            end_date = None

        return cls(trip_id, start_date, end_date)
