
import os
import requests
import json
import psycopg2
import datetime



conn = psycopg2.connect(
    database="fireside", user='root',
    password='unsafe', host='0.0.0.0', port=5432
)

cur = conn.cursor()

# currently, there is rain all overr california - no fires!
# will need a different api call that hits historic fires fttb
api_call = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/" + \
        "arcgis/rest/services/Current_WildlandFire_Perimeters/" + \
        "FeatureServer/0/query?f=json&where=" + \
        "(irwin_POOState%20IN%20(%27US-CA%27))&outFields=*"

historic_api_call = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/" + \
    "arcgis/rest/services/Fire_History_Perimeters_Public/" + \
    "FeatureServer/0/query?f=json&where=" + \
    "(poly_CreateDate%20%3E%3D%20DATE%20'2022-04-01'%20" + \
    "AND" + \
    "%20poly_CreateDate%20%3C%3D%20DATE%20'2022-09-28')%20" + \
    "AND" + \
    "%20(irwin_POOState%20IN%20('US-CA'))&outFields=*"


perimeter_json = json.loads(requests.get(historic_api_call).text)


def get_centroids(rings):
    """
    - disaggregated the rings into points
    - find the mean of the lat/lon point values
    """
    points = [point for ring in rings for point in ring]
    num_points = len(points)
    sum_lon = 0
    sum_lat = 0
    for point in points:
        sum_lon += point[0]
        sum_lat += point[1]
    return([sum_lon / num_points, sum_lat / num_points])

def make_sql_insert(feature):
    perimeter_rings = feature['geometry']['rings']
    centroids = get_centroids(perimeter_rings)

    fts = datetime.datetime.fromtimestamp
    [fts(feature['attributes'][x] * .001) for x in
                         ['poly_DateCurrent', 'poly_CreateDate']]
    feature_datetimes = [fts(feature['attributes'][x]) for x in
                         ['poly_DateCurrent', 'poly_CreateDate']]

    update_vars = ['date_last_update', 'centroid_lat', 'centroid_lon',
                   'behavoir', 'total_acres', 'percent_contained']
    update_vars_sql = ", ".join([f'{x} =  EXCLUDED.{x}' for x in update_vars])
    incident_query = "INSERT INTO incidents (" + \
        "incident_id, incident_name, " + \
        "behavior, total_acres, percent_contained, " + \
        "date_created, date_last_update, " + \
        "centroid_lat, centroid_lon,) VALUES (" + \
        ','.join(['%s'] * 9) + ") " + \
        "ON CONFLICT (incident_id) DO" + \
        "UPDATE SET " + update_vars_sql

    attributes = ['poly_GlobalID',
                  'poly_IncidentName',
                  'irwin_FireBehaviorGeneral',
                  'irwin_CalculatedAcres',
                  'irwin_PercentContained'
                  ]
    values = [feature['attributes'][x] for x in attributes] + \
        [*feature_datetimes] + \
        [centroids[1], centroids[0],]
    return [attributes, values]

# construct and execute the sql insert statement
# for 
for feature in perimeter_json['features']:
    
    cur.execute(*make_sql_insert(feature))
    

                        
items = {
    feature['attributes']['poly_GlobalID']:
    {'name': feature['attributes']['poly_IncidentName'],
     'behavior': feature['attributes'][],
     'feature_category': feature['attributes']['poly_FeatureCategory'],
     'percent_contained': feature['attributes']['irwin_PercentContained'],
     'total_acres': feature['attributes']['poly_GISAcres'],
     'date_current': feature['attributes']['poly_DateCurrent'],
     'date_created': feature['attributes']['poly_CreateDate'],
     'perimeter': union(feature['geometry']['rings'])}
    
}


# coords are in lon lat 

# postgres://postgres:postgrespw@localhost:55000

# cur.execute("""SELECT table_name FROM information_schema.tables
#        WHERE table_schema = 'conditions'""")
# for table in cur.fetchall():
#     print(table)


