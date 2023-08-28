from .db import db_submit
from .result import Result, RESULT_DB_ERR
from .sql_queries import SqlQueries


qrys = SqlQueries()


class Device():

    def __init__(self, garmin_id=None, imei=None):
        self.garmin_id = garmin_id
        self.imei = imei

    def delete(self):
        return db_submit(qrys.delete_device,
                         {'garmin_device_id': self.garmin_id},
                         Result(True, 'Device Successfully Deleted'))

    def register_to_user(self, user_id):
        return db_submit(qrys.delete_device,
                         {'user_id': user_id,
                          'garmin_imei': self.imei,
                          'garmin_device_id': self.garmin_id},
                         Result(True, 'Device Successfully Registered'))
