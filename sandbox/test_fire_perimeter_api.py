
import os
import requests
import json
import psycopg2
import datetime

conn = psycopg2.connect(
    database="conditions", user='root',
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

for feature in perimeter_json['features']:
    # datetime.datetime.fromtimestamp(epoch_time)
    # centroid = 
    incident_query = "INSERT INTO incidents (" + \
        "incident_id, incident_name, centroid_lat, centroid_lon" + \
        "start_time, last_update, behavior, total_acres, " + \
        "percent_contained) VALUES (" + \
        ','.join(['%s'] * 9) + ") " + \
        "ON CONFLICT (incident_id, date_current) DO" + \
        "UPDATE SET " + \ 
    ', '.join([f'{x} =  EXCLUDED.{x}' for x in ['date_current',
                                                'centroid_lat',
                                                'centroid_lon',
                                                'behavoir',
                                                'total_acres',
                                                'percent_contained']])
    
items = {
    feature['attributes']['poly_GlobalID']:
    {'name': feature['attributes']['poly_IncidentName'],
     'behavior': feature['attributes']['irwin_FireBehaviorGeneral'],
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
#        WHERE table_schema = 'public'""")
# for table in cur.fetchall():
#     print(table)
