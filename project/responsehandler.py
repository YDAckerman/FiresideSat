# DEPRECATED

import requests
import json
import pandas as pd
from perimeter import Perimeter
from userlocation import UserLocation

# interested in:
# 'properties.CalculatedAcres'
# 'properties.InitialLatitude'
# 'properties.InitialLongitude'
# 'properties.IncidentName'
# 'properties.FireDiscoveryDateTime'
class Handler:

    def __init__(self):
        self.user_location = UserLocation()

    def response(self, opts):

        # if lat lon are given:
        for opt, arg in opts:

            if opt == '-h':
                return('test.py -d <max_dist> -x <longitude> -y <latitude>')
            # implement lat/lon checks (i.e. needs to be in CA)
            elif opt in ("-d", "--dist"):
                self.max_dist = arg
            elif opt in ("-x", "--lon"):
                self.user_location.setLon(arg)
            elif opt in ("-y", "--lat"):
                self.user_location.setLat(arg)

        self.setIncidentNames(self.max_dist)
        self.setIncidentPerimeters(self.incident_names)
        return(self.make_response())

    def setIncidentNames(self, max_dist):

        fire_url = "https://services3.arcgis.com/" + \
            "T4QMspbfLg3qTGWY/arcgis/rest/services/" + \
            "Current_WildlandFire_Locations/FeatureServer" + \
            "/0/query?outFields=*&where=1%3D1&f=geojson"
        fire_json = json.loads(requests.get(fire_url).text)['features']
        fire_dt = pd.DataFrame.from_dict(pd.json_normalize(fire_json))
        dists = self.user_location.getAllDistances(fire_dt['geometry.coordinates'])
        dists = pd.Series(dists)
        incident_names = fire_dt[dists < max_dist]['properties.IncidentName']
        self.incident_names = list(incident_names)

    def setIncidentPerimeters(self, incident_names):

        def getPerimeter(incident_name):
            # incident_name = "TYLER RD  MERCED"
            perimeter_url = 'https://services3.arcgis.com/' + \
                'T4QMspbfLg3qTGWY/arcgis/rest/services/' + \
                'CY_WildlandFire_Perimeters_ToDate/FeatureServer/' + \
                '0/query?f=json&where=(poly_IncidentName' + \
                f'%20IN%20(%27{incident_name}%27))&outFields=*'
            perimeter_json = json.loads(requests.get(perimeter_url).text)

            # sometimes an incident won't have perimeter data
            # if so, return an empty perimeter
            if len(perimeter_json['features']) == 0:
                return(Perimeter())

            perimeter_rings = perimeter_json['features'][0]['geometry']['rings']
            return(Perimeter(perimeter_rings))

        self.incident_perimeters = [getPerimeter(name) for name in incident_names]

    def make_response(self):

        # this is inelegant
        point = [self.user_location.lon, self.user_location.lat]
        response = ''

        # if there are no incidents nearby, return that information
        if len(self.incident_names) == 0:
            return(f'No Incidents within {self.max_dist} km')

        # otherwise, create a response with distance and bearing to each
        # incident
        for i in range(len(self.incident_names)):
            if self.incident_perimeters[i].isEmpty():
                response = response + \
                    f'The {self.incident_names[i]} perimeter is undefined \n'
            else:
                dist, bear = self.incident_perimeters[i].getDistBearing(point)
                response = response + \
                    f'Distance and bearing from {self.incident_names[i]}: ' + \
                    f'{dist:.2f}, {bear:.2f} \n'
        return response

def main():

    handler = Handler()
    opts = [['-d', 80], ['-x', -119.602469], ['-y', 37.491798]]
    print(handler.response(opts))

    opts = [['-d', 80], ['-x', -122.276023], ['-y', 37.856861]]
    print(handler.response(opts))

    opts = [['-d', 15], ['-x', -122.276023], ['-y', 37.856861]]
    print(handler.response(opts))

if __name__ == "__main__":
    main()
