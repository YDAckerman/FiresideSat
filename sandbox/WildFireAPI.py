import requests
import json
import datetime
import psycopg2
import psycopg2.extras

import sql_queries as qry
import api_calls as api
import helpers as hlp

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

    # create staging tables
    cur.execute(qry.create_staging_tables)

    # todo: error handling
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

    # create updated/outdated
    cur.execute(qry.insert_updated_outdated)

    # delete outdated
    cur.execute(qry.delete_all_outdated)

    # upsert incidents
    # upsert perimeters
    # upsert rings
    cur.execute(qry.upsert_current_incident)
    cur.execute(qry.upsert_current_perimeter)
    cur.execute(qry.upsert_current_bounding_box)


def test():
    """
    """
    def get_table_size(cur, tbl):
        cur.execute(f"SELECT COUNT(*) FROM {tbl};")
        records = cur.fetchall()
        return(records[0][0])

    conn, cur = hlp.db_connect()

    hlp.test_db_up(cur)

    current = []
    outdated = []
    updated = []

    for test_url in api.wildfire_incidents_test_urls:

        # load data
        run(cur, test_url)

        updated.append(get_table_size(cur, "staging_incidents_updated"))
        outdated.append(get_table_size(cur, "staging_incidents_outdated"))
        current.append(get_table_size(cur, "current_incidents"))

    conn.close()

    return(updated, outdated, current)


def main():

    updated, outdated, current = test()
    print(updated)
    print(outdated)
    print(current)


if __name__ == '__main__':
    main()
