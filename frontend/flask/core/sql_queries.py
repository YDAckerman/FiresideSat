
class SqlQueries():

    def __init__(self):
        pass

    check_device_exists = """
    SELECT 1
    FROM devices
    WHERE device_id = %(device_id)s;
    """

    select_user_id = """
    SELECT COALESCE(MAX(user_id), 0)
    FROM users WHERE mapshare_id = %(mapshare_id)s;
    """

    select_device_id = """
    SELECT COALESCE(MAX(device_id), 0)
    FROM devices WHERE user_id = %(user_id)s;
    """

    insert_new_trip = """
    INSERT INTO trips (user_id, device_id, start_date, end_date)
    VALUES (%(user_id)s, %(device_id)s, %(start_date)s, %(end_date)s);
    """

    delete_trip = """
    DELETE FROM trips WHERE trip_id = %(trip_id)s;
    DELETE FROM trip_points WHERE trip_id = %(trip_id)s;
    """

    update_trip = """
    UPDATE trips
    SET start_date = %(start_date)s,
          end_date = %(end_date)s
    WHERE trip_id = %(trip_id)s;
    """

    upsert_airnow_key = """
    INSERT INTO variables (name, value)
    VALUES ('airnow_api_key', %(airnow_key)s)
    ON CONFLICT (name) DO
    UPDATE SET
    value = EXCLUDED.value;
    """

    select_user_trips = """
    SELECT trip_id, start_date, end_date
    FROM trips WHERE user_id = %(user_id)s
    ORDER BY start_date;
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
    DELETE FROM users WHERE user_id = %(user_id)s;
    DELETE FROM trips WHERE user_id = %(user_id)s;
    """
