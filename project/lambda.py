# import time
import selenium
import requests
import pandas as pd
import numpy as np
import json
from math import sin, cos, sqrt, atan2, radians, pi

def getDistance(point1, point2):
    # initial source: https://stackoverflow.com/questions/19412462
    # get the distance between two points in km
    # points are tuples or lists in the form (lat, lon)

        # approximate radius of earth in km
        R = 6373.0

        lon1 = radians(point1[0])
        lat1 = radians(point1[1])

        lon2 = radians(point2[0])
        lat2 = radians(point2[1])

        dlon = lon2 - lon1
        dlat = lat2 - lat1

        a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
        c = 2 * atan2(sqrt(a), sqrt(1 - a))

        # return in km
        return(R * c)

def getBearing(point1, point2):
        # provides initial bearing indegress from point1 to point2
        # sourced from
        # https://www.movable-type.co.uk/scripts/latlong.html

        lon1 = radians(point1[0])
        lat1 = radians(point1[1])

        lon2 = radians(point2[0])
        lat2 = radians(point2[1])

        dlon = lon2 - lon1
        y = sin(dlon) * cos(lat2)
        x = cos(lat1) * sin(lat2) - sin(lat1) * cos(lat2) * cos(dlon)
        theta = atan2(y, x)
        # return in degrees
        bearing = (theta*180/pi + 360) % 360

        return(bearing)


class UserLocation:

    def __init__(self):
        self.timestamp = None # time.time()

    def setLon(self, lon):
        self.lon = lon

    def setLat(self, lat):
        self.lat = lat

    def setPoint(self, lon, lat):
        self.point = [lon, lat]

    def getAllDistances(self, coords):
        point1 = self.point
        return([getDistance(point1, point2) for point2 in coords])


class Perimeter:

    def __init__(self, rings=None):
        if rings is None:
            self.nodes = None
        else:
            self.nodes = np.asarray([j for i in rings for j in i])
        self.nearest_node = None

    def isEmpty(self):
        if self.nodes is None:
            return(True)
        return(False)

    def setNearestPoint(self, point):
        # sourced from:
        # https://codereview.stackexchange.com/questions/28207
        node = np.asarray(point)
        dist_2 = np.sum((self.nodes - node)**2, axis=1)
        self.nearest_node = self.nodes[np.argmin(dist_2)]

    def getNearestPoint(self):
        return self.nearest_node

    def getDistBearing(self, point):
        # sourced from:
        # https://www.movable-type.co.uk/scripts/latlong.html
        if self.nearest_node is None:
            self.setNearestPoint(point)
            point2 = self.nearest_node.tolist()
            return getDistance(point, point2), getBearing(point, point2)
        else:
            point2 = self.nearest_node.tolist()
            return getDistance(point, point2), getBearing(point, point2)


class Handler:


    def __init__(self):
        self.user_location = UserLocation()
        self.max_dist = 80 # km for now


    def response(self, lon, lat):

        # if lat lon are given:
        self.user_location.setPoint(lon, lat)
        self.setIncidentNames(self.max_dist)
        self.setIncidentPerimeters(self.incident_names)
        return(self.make_response())


    def setIncidentNames(self, max_dist):

        fire_url = "https://services3.arcgis.com/" + \
            "T4QMspbfLg3qTGWY/arcgis/rest/services/" + \
            "Current_WildlandFire_Locations/FeatureServer" + \
            "/0/query?outFields=IncidentName" + \
            "&where=(POOState%20IN%20('US-CA'))&f=geojson"
        fire_json = json.loads(requests.get(fire_url).text)['features']
        fire_dt = pd.DataFrame.from_dict(pd.json_normalize(fire_json))
        dists = self.user_location.getAllDistances(fire_dt['geometry.coordinates'])
        dists = pd.Series(dists)
        incident_names = fire_dt[dists < max_dist]['properties.IncidentName']
        self.incident_names = list(incident_names)


    def setIncidentPerimeters(self, incident_names):

        def getPerimeter(incident_name):
            # incident_name = "Washburn"
            perimeter_url = 'https://services3.arcgis.com/' + \
                'T4QMspbfLg3qTGWY/arcgis/rest/services/' + \
                'Current_WildlandFire_Perimeters/FeatureServer/' + \
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
        point = self.user_location.point
        response = ''

        # if there are no incidents nearby, return that information
        if len(self.incident_names) == 0:
            return(f'No Incidents within {self.max_dist} km')

        # otherwise, create a response with distance and bearing to each
        # incident
        for i in range(len(self.incident_names)):
            if self.incident_perimeters[i].isEmpty():
                next
            else:
                dist, bear = self.incident_perimeters[i].getDistBearing(point)
                # print(self.incident_perimeters[i].getNearestPoint())
                response = response + \
                    f'Distance and bearing from {self.incident_names[i]}: ' + \
                    f'{dist:.2f}, {bear:.2f} \n'
        if response == '':
            response = 'No active fires nearby'
        return response


def lambda_handler(event, context):
    handler = Handler()
    content = event['Body'].split("+")
    response_string = handler.response(float(content[1]), float(content[0]))
    return("<?xml version=\"1.0\" encoding=\"UTF-8\"?>"
           + "<Response><Message><Body>"
           + response_string
           + "</Body></Message></Response>")


message = {
    "Body": "37.491798+-119.602469+-Jonathan"
}

message = {
    "Body": "37.5123+-122.1611+-Jonathan"
}
print(lambda_handler(message, 1))
