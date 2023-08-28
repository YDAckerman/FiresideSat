
class SqlQueries():

    def __init__(self):
        pass

    does_user_exist = """
    SELECT 1
    FROM users
    WHERE  mapshare_id = %(mapshare_id)s;
    """

    check_device_exists = """
    SELECT 1
    FROM devices
    WHERE device_id = %(device_id)s;
    """

    select_user_id = """
    SELECT user_id FROM users WHERE mapshare_id = %(mapshare_id)s;
    """

    insert_new_usr = """
    INSERT INTO users (user_email, user_pw,
                       mapshare_id, mapshare_pw)
    VALUES ('NA', 'NA', %(mapshare_id)s, %(mapshare_pw)s);
    """

    insert_new_device = """
    INSERT INTO devices (user_id, garmin_imei, garmin_device_id)
    VALUES (%(user_id)s, %(garmin_imei)s, %(garmin_device_id)s);
    """

    delete_device = """
    DELETE FROM devices WHERE garmin_device_id = %(garmin_device_id)s;
    """

    delete_user = """
    DELETE FROM users WHERE mapshare_id = %(mapshare_id)s;
    """

    insert_new_trip = """

    """
