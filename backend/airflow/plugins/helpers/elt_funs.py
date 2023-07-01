from airflow.models import Variable
from helpers.sql_queries import SqlQueries as sql
from helpers.header_funs import get_auth_basic
from helpers.extract_funs import extract_incident_attr, \
    extract_perimeter_attr, \
    extract_aqi_attr, \
    extract_feed_attr
import psycopg2.extras
import json


def elt_wildfire_locations(endpoint, pg_conn, pg_cur, context, log):

    start_date = context.get('data_interval_start') \
                       .to_date_string()
    end_date = context.get('data_interval_end') \
                      .to_date_string()

    endpoint.set_route(data_interval_start=start_date,
                       data_interval_end=end_date)

    endpt_resp = json.loads(endpoint.get().text)

    if endpt_resp:

        print(endpt_resp)

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in endpt_resp['features']:

            incident_attr = extract_incident_attr(feature)
            pg_cur.execute(sql.insert_staging_incident, incident_attr)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def elt_wildfire_perimeters(endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_current_incident_ids)
    records = pg_cur.fetchall()
    endpoint.set_route("%27%2C%20%27".join(list(zip(*records))[0]))
    endpt_resp = json.loads(endpoint.get().text)

    if endpt_resp:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in endpt_resp['features']:

            perimeter_attr = extract_perimeter_attr(feature)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_perimeter,
                                           perimeter_attr)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def elt_mapshare_locs(endpoint, pg_conn, pg_cur, context, log):

    current_date = context.get('data_interval_start')

    pg_cur.execute(sql.select_active_users,
                   {'current_date': current_date})

    records = pg_cur.fetchall()

    for record in records:

        user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

        headers = get_auth_basic(mapshare_id, mapshare_pw)
        endpoint.set_route(mapshare_id=mapshare_id,
                           garmin_imei=garmin_imei)
        endpt_resp = endpoint.get(headers=headers)
        if endpt_resp:

            trip_attr = [trip_id] \
                + extract_feed_attr(endpt_resp)

            pg_cur.execute(sql.insert_staging_trip_points,
                           trip_attr)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())


def elt_fire_locs_aqi(endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_fire_centroids)
    records = pg_cur.fetchall()

    for record in records:

        # TODO: DIST _should_ change depending on the fire (record)
        AQI_RADIUS_MILES = 35
        incident_id, lon, lat = record

        endpoint.set_route(lat=lat, lon=lon,
                           radius_miles=AQI_RADIUS_MILES,
                           key=Variable.get('airnow_api_key'))
        endpt_resp = json.loads(endpoint.get().text)

        if endpt_resp:

            aqi_values = extract_aqi_attr(incident_id,
                                          endpt_resp)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_aqi,
                                           aqi_values)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())
