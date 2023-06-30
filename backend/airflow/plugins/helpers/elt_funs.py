from airflow.models import Variable
from helpers.sql_queries import SqlQueries as sql
from helpers.extract_funs import extract_incident_attr, \
    extract_perimeter_attr, \
    extract_aqi_attr, \
    extract_feed_attr
import psycopg2.extras
import json


def elt_wildfire_locations(self, endpoint, pg_conn, pg_cur, context, log):

    endpoint_response = json.loads(endpoint.run(context).text)

    if endpoint_response:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in endpoint_response['features']:

            incident_attr = extract_incident_attr(feature)
            pg_cur.execute(sql.insert_staging_incident, incident_attr)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def elt_wildfire_perimeters(self, endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_current_incident_ids)
    records = pg_cur.fetchall()
    endpoint_response = json.loads(endpoint.run("'%2C%20'".join(records)).text)

    if endpoint_response:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in endpoint_response['features']:

            perimeter_attr = extract_perimeter_attr(feature)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_perimeter,
                                           perimeter_attr)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def elt_mapshare_locs(self, endpoint, pg_conn, pg_cur, context, log):

    current_date = context.get('data_interval_start')

    pg_cur.execute(sql.select_active_users,
                   {'current_date': current_date})

    records = pg_cur.fetchall()

    for record in records:

        user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

        headers = endpoint.make_headers(mapshare_id, mapshare_pw)
        cv = {"mapshare_id": mapshare_id,
              "garmin_imei": garmin_imei}
        endpoint_response = endpoint.run(context_vars=cv,
                                         headers=headers)
        if endpoint_response:

            trip_attr = [trip_id] \
                + extract_feed_attr(endpoint_response)

            pg_cur.execute(sql.insert_staging_trip_points,
                           trip_attr)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())


def elt_fire_locs_aqi(self, endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_fire_centroids)
    records = pg_cur.fetchall()

    for record in records:

        # TODO: DIST _should_ change depending on the fire (record)
        AQI_RADIUS_MILES = 35
        incident_id, lon, lat = record

        log.info("Inserting aqi staging data for incident: "
                 + incident_id)

        api_key = Variable.get('airnow_api_key')
        cv = {'lat': lat, 'lon': lon,
              'radius_miles': AQI_RADIUS_MILES,
              'key': api_key}
        endpoint_response = json.loads(endpoint.run(context_vars=cv).text)

        if endpoint_response:

            aqi_values = extract_aqi_attr(incident_id,
                                          endpoint_response)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_aqi,
                                           aqi_values)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())
