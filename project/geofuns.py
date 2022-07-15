
# sourced from
# https://www.movable-type.co.uk/scripts/latlong.html

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

def main():
    point1 = (-17.03663, 8.46696)
    point2 = (-17.03663, 65.35996)
    distance = getDistance(point1, point2)
    bearing = getBearing(point1, point2)
    print(f"Calcuated distance: {distance}")
    print("True distance: 6328 km")
    print(f"Calculated bearing: {bearing}")
    print("True bearing: 0 degrees")

if __name__ == "__main__":
    main()
