from .device import Device
from .result import Result
from .sql_queries import SqlQueries


qrys = SqlQueries()


class User():

    def __init__(self, email,
                 password=None,
                 mapshare_id=None,
                 mapshare_password=None):

        self.credentials = {"email": email,
                            "password": password,
                            "mapshare_id": mapshare_id,
                            "mapshare_pw": mapshare_password,
                            "otp": None}

    def set_otp(self, otp):
        self.credentials['otp'] = otp

    def exists(self, conn):

        with conn:
            with conn.cursor() as cur:

                # check if user exists
                # (if so, direct to reset password;
                # must provide new mapshare pw, too)
                cur.execute(qrys.usr_exists,
                            self.credentials)
                user_exists = cur.fetchall()

        if user_exists:
            return True
        return False

    def login(self, conn):

        if self.exists(conn):
            pass
        else:
            return Result(False, 'User does not exist.')

    def register(self, conn):

        if self.exists(conn):
            return Result(False, 'Email already in use.')

        device = Device()
        device.set_id("")
        self.set_otp("12345")
        # res = device.send_otp(user)
        res = Result(True, 'Check your satphone for a one-time passcode.')

        if res.status:

            with conn:
                with conn.cursor() as cur:
                    db_err_result = Result(False, 'A database error occurred')
                    try:
                        cur.execute(qrys.new_usr, self
                                    .credentials)

                    except Exception as e:
                        print("Insert User Error: " + e)
                        return db_err_result

                    try:
                        user_id = cur.fetchall()[0][0]
                        cur.execute(qrys.new_device_for_usr,
                                    {"user_id": user_id})
                        device_id = cur.fetchall()[0][0]
                        cur.execute(qrys.update_device_garmin_id,
                                    {'device_id': device_id,
                                     'garmin_device_id':
                                     device.garmin_id})
                    except Exception as e:
                        print("Insert/Update Device Error: " + e)
                        return db_err_result

                conn.commit()
        return res
