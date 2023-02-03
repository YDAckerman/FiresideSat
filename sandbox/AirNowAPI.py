import requests
import json
import datetime
import psycopg2
import psycopg2.extras

import sql_queries as qry
import api_calls as api
import helpers as hlp
import WildFireAPI as fire_api

import pdb


def record_to_datetime(result):
    """
    - extract the date from an airnow api result record
    """

    date_part = [int(x) for x in result['DateObserved'].strip().split("-")]
    hour_part = result['HourObserved']
    return(datetime.datetime(*[*date_part, hour_part]))


def make_aqi_values(incident_id, api_response):
    """
    - loop through api_result
    - for each record, get date and location/aqi recorded
    - return list of tuples
    """
    tuples_list = [(incident_id,
                    record_to_datetime(x),
                    x['Latitude'],
                    x['Longitude'],
                    x['AQI']) for x in api_response]
    return(tuples_list)


def run(cur, api_key):

    params = {
        "lat": None,
        "lon": None,
        "key": api_key
    }

    cur.execute(qry.create_staging_aqi)
    cur.execute(qry.select_centroids)
    records = cur.fetchall()

    for record in records:
        incident_id, params['lat'], params['lon'] = record
        pdb.set_trace()
        next
        # api_response = json.loads(requests.get(api.airnow_radius_url,
        #                                        params=params).text)
        # aqi_values = make_aqi_values(incident_id, api_response)
        # psycopg2.extras.execute_values(cur, qry.insert_staging_aqi,
        #                                aqi_values)


def test():

    conn, cur = hlp.db_connect()

    hlp.test_db_up(cur)

    test_url = api.wildfire_incidents_test_urls[11]

    # populate test schema with data
    fire_api.run(cur, test_url)

    # get api data and insert into 'current_aqi' table
    run(cur, hlp.get_api_key('AirNow'))

    cur.execute("SELECT * FROM staging_aqi LIMIT 5;")
    records = cur.fetchall()
    print(records)
    conn.close()


def main():
    """
    """
    test()


if __name__ == '__main__':
    main()
