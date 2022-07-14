#!/usr/bin/python3

import requests
import pandas as pd
from perimeter import Perimeter
import json
import sys
import getopt

def getPerimeter(incident_name):

    # incident_name = "Washburn"
    perimeter_url = 'https://services3.arcgis.com/' + \
        'T4QMspbfLg3qTGWY/arcgis/rest/services/' + \
        'CY_WildlandFire_Perimeters_ToDate/FeatureServer/' + \
        '0/query?f=json&where=(poly_IncidentName' + \
        f'%20IN%20(%27{incident_name}%27))&outFields=*'
    perimeter_json = json.loads(requests.get(perimeter_url).text)
    perimeter_rings = perimeter_json['features'][0]['geometry']['rings']
    return Perimeter(perimeter_rings)


def getCloseFires(lat, lon):
    # implement lat/lon checks
    fire_locs_url = "https://services3.arcgis.com/" + \
        "T4QMspbfLg3qTGWY/arcgis/rest/services/" + \
        "Current_WildlandFire_Locations/FeatureServer" + \
        "/0/query?outFields=*&where=1%3D1&f=geojson"
    locations_json = json.loads(requests.get(fire_locs_url).text)
    flat_locations = pd.json_normalize(locations_json['features'])
    locations_dt = pd.DataFrame.from_dict(flat_locations)
    return locations_dt

# interested in:
# 'properties.CalculatedAcres'
# 'properties.InitialLatitude'
# 'properties.InitialLongitude'
# 'properties.IncidentName'
# 'properties.FireDiscoveryDateTime'

def main(argv):
    lon = 0
    lat = 0
    try:
        opts, args = getopt.getopt(argv, "hx:y:", ["lon=", "lat="])
    except getopt.GetoptError:
        print('test.py -x <longitude> -y <latitude>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -x <longitude> -y <latitude>')
            sys.exit()
        elif opt in ("-x", "--lon"):
            lon = arg
        elif opt in ("-y", "--lat"):
            lat = arg
    print(f'latitude is {lat}')
    print(f'longitude is {lon}')

if __name__ == "__main__":
    main(sys.argv[1:])
