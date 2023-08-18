
class SqlQueries():

    def __init__(self):
        pass

    usr_exists = """
    SELECT 1
    FROM users
    WHERE  user_email = %(email)s;
    """

    new_usr = """
    INSERT INTO users (user_email, user_pw,
                       mapshare_id, mapshare_pw)
    VALUES (%(email)s, %(otp)s,
            %(mapshare_id)s, %(mapshare_pw)s)
    RETURNING user_id;
    """

    new_device_for_usr = """
    INSERT INTO devices (user_id)
    VALUES (%(user_id)s)
    RETURNING device_id;
    """

    update_device_garmin_id = """
    UPDATE devices
    SET garmin_device_id = %(garmin_device_id)s
    WHERE device_id = %(device_id)s;
    """
