
class SqlQueries():

    def __init__(self):
        pass

    usr_exists = """
    SELECT 1
    FROM users
    WHERE  mapshare_id = %(mapshare_id)s;
    """

    new_usr = """
    INSERT INTO users (user_email, user_pw,
                       mapshare_id, mapshare_pw)
    VALUES (%(email)s, %(pw)s,
            %(mapshare_id)s, %(mapshare_pw)s)
    RETURNING user_id;
    """

    new_device = """
    INSERT INTO devices (user_id, garmin_imei, garmin_device_id)
    VALUES (%(user_id)s, %(garmin_imei)s, %(garmin_device_id)s)
    RETURNING device_id;
    """
