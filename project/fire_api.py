
# __________________NOTES__________________
# state park boundaries:
# https://www.parks.ca.gov/?page_id=29682
# national park boundaries:
# https://irma.nps.gov/DataStore/Reference/Profile/2224545?lnv=True
# national park air quality monitors:
# https://www.nps.gov/subjects/air/current-data.htm
# _________________________________________

import requests
import json
from perimeter import Perimeter
from log import log


class FireAPI:

    api_call = "https://services3.arcgis.com/T4QMspbfLg3qTGWY/" + \
        "arcgis/rest/services/Current_WildlandFire_Perimeters/" + \
        "FeatureServer/0/query?f=json&where=" + \
        "(irwin_POOState%20IN%20(%27US-CA%27))&outFields=*"

    def __init__(self):

        perimeter_json = json.loads(requests.get(self.api_call).text)

        self.perimeters = {
            feature['attributes']['poly_IncidentName']:
            {'behavior': feature['attributes']['irwin_FireBehaviorGeneral'],
             'perimeter': Perimeter(feature['geometry']['rings'])}
            for feature in perimeter_json['features']
        }

        log.info("HASH:" + hash(str(self.perimeters)))

    def build_message(self, loc):

        message = ''
        for fire in self.perimeters.keys():
            dist = self.perimeters[fire]['perimeter'].getDist(loc)
            edge = self.perimeters[fire]['perimeter'].nearest_node
            status = self.perimeters[fire]['behavior']
            if dist < 161:
                message += f'{fire}, {status}, {edge}, {dist} \n'

        return(message)


def main():
    api = FireAPI()
    msg = api.build_message(loc=[-119.602469, 37.491798])
    if msg == '':
        msg = 'No incidents to report'
    print(msg)


if __name__ == '__main__':
    main()
