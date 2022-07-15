import time
import pickle
from geofuns import getDistance

class UserLocation:

    # phone number or user_id?
    # right now this doesnt link to where a user /was/
    # that would require saving/loading and maybe be
    # an unnecessiarily complex use-case (and more work)
    
    def __init__(self):
        self.timestamp = time.time()
    
    def setLon(self, lon):
        self.lon = lon

    def setLat(self, lat):
        self.lat = lat

    def getAllDistances(self, coords):
        point1 = [self.lon, self.lat]
        return([getDistance(point1, point2) for point2 in coords])

    # def save(self): 

def main():
    test_point = (-119.602469, 37.491798)
    user_location = UserLocation()
    user_location.setLon(test_point[0])
    user_location.setLat(test_point[1])
    with open('./test_data/fire_coords.pickle', 'rb') as f:
        test_coords = pickle.load(f)
    test_dists = user_location.getAllDistances(test_coords)
    print("min test distance: " + str(min(test_dists)))
    print("max test distance: " + str(max(test_dists)))

if __name__ == "__main__":
    main()
