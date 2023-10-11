# from airflow.models import Variable
from helpers.sql_queries import SqlQueries as sql
from helpers.header_funs import get_auth_basic
from helpers.extract_funs import extract_incident_attr, \
    extract_perimeter_attr, \
    extract_aqi_attr, \
    extract_feed_attr
import psycopg2.extras
import json
import pendulum


def elt_wildfire_locations(endpoint, pg_conn, pg_cur, context, log):

    start_date = context.get('ds')

    end_date = pendulum.from_format(start_date, "YYYY-MM-DD").add(days=1)

    # state settings
    pg_cur.execute(sql.select_all_user_state_settings)
    states = pg_cur.fetchall()
    states_formatted = "'%2C'".join(state[0] for state in states)

    endpoint.set_route(data_interval_start=start_date,
                       data_interval_end=end_date.to_date_string(),
                       states_str=states_formatted)

    endpt_resp = json.loads(endpoint.get().text)

    if endpt_resp:

        # loop through features and
        # load each incident and its perimeter into postgres
        for feature in endpt_resp['features']:

            incident_attr = extract_incident_attr(feature)
            pg_cur.execute(sql.insert_staging_incident, incident_attr)
            pg_conn.commit()

    else:

        log.info(endpoint.warn())


# TODO: this is broken for current perimeters fires
def elt_wildfire_perimeters(endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_current_incident_ids)
    records = pg_cur.fetchall()

    # I would much prefer to batch request these, but as
    # some fires don't have perimeter data, it looks like
    # the entire request will fail if I do.
    for record in records:

        endpoint.set_route(record[0])
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

    current_date = context.get('ds')

    pg_cur.execute(sql.select_active_users,
                   {'current_date': current_date})

    records = pg_cur.fetchall()

    for record in records:

        user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

        headers = get_auth_basic(mapshare_id, mapshare_pw)
        endpoint.set_route(user=mapshare_id, imei=garmin_imei)
        endpt_resp = endpoint.get(headers=headers)
        if endpt_resp:

            trip_attr = [trip_id] \
                + extract_feed_attr(endpt_resp)

            pg_cur.execute(sql.insert_staging_trip_points,
                           trip_attr)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())


def elt_aqi(endpoint, pg_conn, pg_cur, log, records, sql_query):

    pg_cur.execute(sql.select_airnow_api_key)
    airnow_key = pg_cur.fetchone()[0]

    for record in records:

        spatial_object_id, lon, lat, rad = record

        endpoint.set_route(lat=lat, lon=lon,
                           radius_miles=rad,
                           key=airnow_key)
        endpt_resp = json.loads(endpoint.get().text)

        if endpt_resp:

            aqi_values = extract_aqi_attr(spatial_object_id,
                                          endpt_resp)
            # print(aqi_values)
            psycopg2.extras.execute_values(pg_cur,
                                           sql_query,
                                           aqi_values)

            pg_conn.commit()

        else:

            log.info(endpoint.warn())


def elt_fire_locs_aqi(endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_fire_centroids)
    records = pg_cur.fetchall()

    elt_aqi(endpoint, pg_conn, pg_cur,
            log, records, sql.insert_staging_aqi)


def elt_trip_points_aqi(endpoint, pg_conn, pg_cur, context, log):

    pg_cur.execute(sql.select_latest_points,
                   {'current_date': context.get('ds')})
    records = pg_cur.fetchall()

    elt_aqi(endpoint, pg_conn, pg_cur,
            log, records, sql.insert_staging_trip_points_aqi)
