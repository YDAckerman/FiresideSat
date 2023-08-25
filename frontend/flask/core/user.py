from hashlib import sha3_256
from .device import Device
from .result import Result, RESULT_DB_ERR
from .sql_queries import SqlQueries

qrys = SqlQueries()

RESULT_MAPSHARE_ID_ERR = Result(False, 'Mapshare ID already in use.')
RESULT_REG_SUCCESS = Result(True, 'Check your satphone for confirmation.')


class User():

    user_id = None

    def __init__(self,
                 mapshare_id=None,
                 mapshare_password=None):

        self.credentials = {
            "email":  "NA",
            "pw": "NA",
            "mapshare_id": mapshare_id,
            "mapshare_pw": mapshare_password
        }

    def _set_user_id(self, new_id):
        self.user_id = new_id

    def _set_otp(self, otp):
        self.credentials['otp'] = sha3_256(bytes(otp, encoding='utf-8')) \
            .hexdigest()

    def _update_mapshare_pw(self, new_pw):
        pass

    def exists(self, conn):

        with conn:
            with conn.cursor() as cur:
                cur.execute(qrys.usr_exists,
                            self.credentials)
                user_exists = cur.fetchall()

        if user_exists:
            return True
        return False

    def register(self, conn, debug=False):

        if self.exists(conn):
            return RESULT_MAPSHARE_ID_ERR

        device = Device()

        if debug:
            device.set_garmin_id("000000")
            res = RESULT_REG_SUCCESS
        else:
            res = device.send_confirmation(self)

        if res.status:

            with conn:
                with conn.cursor() as cur:

                    try:

                        cur.execute(qrys.new_usr,
                                    self.credentials)
                        self._set_user_id(cur.fetchall()[0][0])

                    except Exception as e:
                        print("Insert User Error: " + e)
                        return RESULT_DB_ERR

            conn.commit()
            device_reg_result = device.register(self, conn)
            if not device_reg_result.status:
                return device_reg_result

        return res.append(device_reg_result)
