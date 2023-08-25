

class Trip():

    def __init__(self, mapshare_id, start_date, end_date):

        self.mapshare_id = mapshare_id
        self.start_date = start_date
        self.end_date = end_date
        self.trip_id = None

    def update_start_date(self, new_start):
        self.start_date = new_start

    def update_end_date(self, new_end):
        self.end_date = new_end

    def set_trip_id(self, trip_id):
        self.trip_id = trip_id

    def submit(self):
        # if trip_id exists
        # use an update
        # if not, submit trip and record new trip_id
        pass

    def delete(self):
         # if trip_id exists, call delete
        pass
