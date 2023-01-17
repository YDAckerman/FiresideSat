import requests
import json
import datetime
import psycopg2
import psycopg2.extras
import configparser

from sql_queries import drop_staging_tables_query
from sql_queries import create_staging_tables_query
from sql_queries import delete_staging_perimeter_query
from sql_queries import insert_staging_incident_query
from sql_queries import insert_staging_perimeter_query

from api_calls import historic_wildfire_incidents_url

# import pdb


def make_incident_values(attributes):
    """
    """
    attribute_keys = [
        'poly_GlobalID',
        'poly_IncidentName',
        'irwin_FireBehaviorGeneral',
        'irwin_CalculatedAcres',
        'irwin_PercentContained'
    ]

    date_attributes = [
        'poly_DateCurrent',
        'poly_CreateDate'
    ]

    fts = datetime.datetime.fromtimestamp
    feature_datetimes = [fts(attributes[x] * .001) for x in
                         date_attributes]

    return([attributes[x] for x in attribute_keys] +
           [*feature_datetimes] +
           [None]*2)


def make_perimeter_values(incident_id, rings):
    """
    """
    return([(incident_id, i, x[0], x[1])
            for i in range(len(rings))
            for x in rings[i]
            ])


def run(cur, url):
    """
    """
    api_response = json.loads(requests.get(url).text)

    for feature in api_response['features']:

        attributes = feature['attributes']
        incident_id = attributes['poly_GlobalID']
        rings = feature['geometry']['rings']

        incident_values = make_incident_values(attributes)
        perimeter_values = make_perimeter_values(incident_id, rings)

        # execute sql queries
        cur.execute(insert_staging_incident_query, incident_values)
        cur.execute(delete_staging_perimeter_query, (incident_id, ))
        psycopg2.extras.execute_values(cur, insert_staging_perimeter_query,
                                       perimeter_values)


def main():

    config = configparser.ConfigParser()
    config.read('./fireside.cfg')

    conn = psycopg2.connect(
        database=config['DATABASE']['DB_NAME'],
        user=config['DATABASE']['DB_USER'],
        password=config['DATABASE']['DB_PASSWORD'],
        host=config['DATABASE']['DB_HOST'],
    )

    cur = conn.cursor()

    # create tables
    cur.execute(drop_staging_tables_query)
    conn.commit()
    cur.execute(create_staging_tables_query)
    conn.commit()

    # insert data
    run(cur, historic_wildfire_incidents_url)
    conn.commit()

    # test
    for table in ["incidents", "perimeters"]:

        cur.execute(f"SELECT * FROM staging.{table} LIMIT 5;")
        records = cur.fetchall()
        for record in records:
            print(record)

    conn.close()


if __name__ == '__main__':
    main()
