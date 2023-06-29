from airflow.models import Variable
from helpers.sql_queries import SqlQueries as sql
from helpers.endpoint import make_headers
from helpers.etl_extract_funs import extract_incident_values, \
    extract_perimeter_values, \
    extract_aqi_values, \
    extract_feed_values
import psycopg2.extras
import json


def load_wildfire_perimeters(self, http_hook, endpoint, pg_conn,
                             pg_cur, context, log):

    response = http_hook.run(endpoint=endpoint.format(**context))
    response = json.loads(response.text)

    if response:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in response['features']:

            attributes = feature['attributes']
            incident_id = attributes['poly_SourceGlobalID']

            rings = feature['geometry']['rings']

            incident_values = extract_incident_values(attributes)

            log.info("Incident data:" + str(incident_values))

            perimeter_values = extract_perimeter_values(incident_id, rings)

            log.info("Inserting wildfire staging data for incident: "
                     + incident_id)
            pg_cur.execute(sql.insert_staging_incident,
                           incident_values)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_perimeter,
                                           perimeter_values)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def load_wildfire_locations(self, http_hook, endpoint, pg_conn,
                            pg_cur, context, log):

    response = http_hook.run(endpoint=endpoint.format(**context))
    response = json.loads(response.text)

    if response:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in response['features']:

            attributes = feature['attributes']

            incident_values = extract_incident_values(attributes)

            pg_cur.execute(sql.insert_staging_incident,
                           incident_values)

            pg_conn.commit()

    else:

        log.info(endpoint.warn())


def load_from_mapshare_endpoint(self, http_hook, endpoint, pg_conn,
                                pg_cur, context, log):

    current_date = context.get('data_interval_start')

    pg_cur.execute(sql.select_active_users,
                   {'current_date': current_date})

    records = pg_cur.fetchall()

    for record in records:

        user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

        log.info("getting mapshare feed data for user: "
                 + str(user_id))

        endpoint = self.api \
                       .format_endpoint("mapshare_feed_endpoint",
                                        {"mapshare_id": mapshare_id,
                                         "garmin_imei": garmin_imei}) \

        headers = make_headers(mapshare_id, mapshare_pw)

        api_response = http_hook.run(endpoint=endpoint,
                                     headers=headers)

        if api_response:

            trip_values = [trip_id] \
                + extract_feed_values(api_response)
            pg_cur.execute(sql.insert_staging_trip_points,
                           trip_values)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())


def load_from_airnow_endpoint(self, http_hook, endpoint, pg_conn, pg_cur,
                              context, log):

    pg_cur.execute(sql.select_fire_centroids)
    records = pg_cur.fetchall()

    for record in records:

        # TODO: DIST _should_ change depending on the fire (record)
        AQI_RADIUS_MILES = 35
        incident_id, lon, lat = record

        log.info("Inserting aqi staging data for incident: "
                 + incident_id)

        endpoint = self.api \
                       .format_endpoint("airnow_endpoint",
                                        {'lat': lat,
                                         'lon': lon,
                                         'radius_miles': AQI_RADIUS_MILES})

        api_response = http_hook.run(endpoint=endpoint)
        response = json.loads(api_response.text)

        if response:

            aqi_values = extract_aqi_values(incident_id, response)
            psycopg2.extras.execute_values(pg_cur,
                                           sql.insert_staging_aqi,
                                           aqi_values)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())
