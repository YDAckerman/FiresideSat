
import sys
import numpy as np
import pickle
from geofuns import getDistance, getBearing


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


def main():
    # lon / lat
    test_point = (-119.602469, 37.491798)
    with open('./test_data/washburn_rings.pickle', 'rb') as f:
        washburn_rings = pickle.load(f)
    print("Testing Perimeter")
    try:
        washburn_perimeter = Perimeter(washburn_rings)
    except:
        print("Perimeter failed")
    print("Succeeded")
    print("Testing setNearestPoint")
    try:
        washburn_perimeter.setNearestPoint(test_point)
    except:
        print("setNearestPoint failed")
        sys.exit()
    print("Succeeded")
    print("Testing getDistBearing")
    try:
        distance, bearing = washburn_perimeter.getDistBearing(test_point)
    except:
        print("getDistBearing failed")
        sys.exit()
    print("Succeeded")
    print(f'Calculated Distance is: {distance}')
    print("True distance: 1.1 km")
    print(f'Calculated Bearing is: {bearing}')
    print("True bearing: 318.84 degrees")


if __name__ == "__main__":
    main()

