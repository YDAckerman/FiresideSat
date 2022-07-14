import numpy as np
from geofuns import getDistance, getBearing

class Perimeter:

    def __init__(self, rings):
        self.nodes = np.asarray([j for i in rings for j in i])
        self.nearest_node = None

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
            self.closest(point)
        else:
            point2 = self.nearest_node.tolist()[0]
            return getDistance(point, point2), getBearing(point, point2)


def main():
    
