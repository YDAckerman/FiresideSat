import requests
import json
import datetime
import psycopg2
import psycopg2.extras
import configparser

import sql_queries as qry
import api_calls as api

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
        cur.execute(qry.insert_staging_incident, incident_values)
        psycopg2.extras.execute_values(cur, qry.insert_staging_perimeter,
                                       perimeter_values)


def main():
    """
    """
    def print_table_size(cur, tbl):
        print(f"{tbl} number of rows: ")
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        records = cur.fetchall()
        for record in records:
            print(record)

    config = configparser.ConfigParser()
    config.read('./fireside.cfg')

    conn = psycopg2.connect(
        database=config['DB']['DB_NAME'],
        user=config['DB']['DB_USER'],
        password=config['DB']['DB_PASSWORD'],
        host=config['DB']['DB_HOST'],
    )

    conn.autocommit = True

    cur = conn.cursor()

    # create the schemas
    cur.execute(qry.create_schemas)

    # drop/create current tables
    cur.execute(qry.drop_current_tables)
    cur.execute(qry.create_current_tables)

    for test_url in api.wildfire_incidents_test_urls:

        # create staging tables
        cur.execute(qry.create_staging_tables)

        # load staging data
        run(cur, test_url)

        # test:
        print("staging rows: ")
        print_table_size(cur, "staging.incidents")
        print_table_size(cur, "staging.perimeters")

        # create updated/outdated
        cur.execute(qry.insert_updated_outdated)

        # test:
        print("update/outdate table sizes: ")
        print_table_size(cur, "staging.incidents_updated")
        print_table_size(cur, "staging.incidents_outdated")

        # delete outdated
        print("post-delete rows: ")
        cur.execute(qry.delete_all_outdated)
        print_table_size(cur, "current.incidents")
        print_table_size(cur, "current.perimeters")
        print_table_size(cur, "current.rings")

        # upsert incidents
        # upsert perimeters
        # upsert rings
        cur.execute(qry.upsert_current_incident)
        cur.execute(qry.upsert_current_perimeter)
        cur.execute(qry.upsert_current_ring)

        print("post-upsert rows: ")
        print_table_size(cur, "current.incidents")
        print_table_size(cur, "current.perimeters")
        print_table_size(cur, "current.rings")

    conn.close()


if __name__ == '__main__':
    main()
