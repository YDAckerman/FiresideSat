import requests
import configparser
import json
import re

from pykml import parser
from pykml import util

import base64

def get_user_info(user, pw):
    #
    # - queries feed url
    # - returns json response

    user ="WURUE"
    pw ="hV3DSaqfa0qR7X09V0iX"
    imei ="300434030014150"


    # usr_pw = f'{user}:{pw}'
    # b64_val = base64.b64encode(usr_pw.encode()).decode()
    # headers = {"Authorization": "Basic %s" % b64_val}
    
    # url = f"https://explore.garmin.com/feed/share/{user}" + \
    #     "?d1=2022-08-01T06:00z&d2=2022-10-01T15:00z"

    url = f"https://explore.garmin.com/feed/share/{user}" + \
        f"?imei={imei}"
    response = requests.get(url, auth=(user, pw))

    # won't always work.
    # see use of pykml below.
    coords = re.findall(r'<coordinates>(\S+),(\S+),(\S+)</coordinates>',
                        response.text)[-1]

    # timestamp = re.findall(r'<TimeStamp>\s+<when>(\S+)</when>\s+</TimeStamp>',
    #                        response.text)[-1]

    root = parser.fromstring(bytes(response.text, encoding='utf8'))
    root.Document.Folder.Placemark.TimeStamp.when
    root.Document.Folder.Placemark.Point.coordinates
    root.Document.Folder.Placemark.ExtendedData.Data[17].value
    root.Document.Folder.Placemark.ExtendedData.Data[12].value


    datetime.strptime(str(root.Document.Folder.Placemark.TimeStamp.when), '%Y-%m-%dT%H:%M:%SZ')
    # resp = requests.get("https://developers.google.com/static/kml/documentation/KML_Samples.kml")
    # root = parser.fromstring(bytes(resp.text, encoding='utf8'))
    # root.Document.Folder[0].Placemark[1].Point.coordinates
    
    event = 'OTHER'
    if 'Tracking turned off' in response.text:
        event = 'OFF'
    elif 'Tracking turned on' in response.text:
        event = 'ON'

    return({'lon': float(coords[0]),
            'lat': float(coords[1]),
            'elv': float(coords[2]),
            'event': event
            })


def send_user_message(user, pw, device, msg):
    #
    # - posts message to user MapShare
    # - returns True if sucessful, False otherwise.
    # - Note: this might be broken. access to the SendMessageToDevices
    # -       function might require the user name(?)
    #


    msg = "is this still working?"

    device = "448739"
    
    url = f"https://share.garmin.com/{user}/Map/SendMessageToDevices"
    myobj = {'deviceIds': device,
             'fromAddr': 'no_reply@firesidesat.com',
             'messageText': msg}

    myobj = {
        'deviceIds': "000000",
        'fromAddr': 'no_reply@firesidesat.com',
        'messageText': msg}
    

    response = requests.post(url, auth=('', pw), json=myobj)
    return(json.loads(response.text)["success"])


def main():

    config = configparser.ConfigParser()
    config.read_file(open('/usr/Yoni/Projects/'
                          + 'FiresideSat/project/inReach.cfg'))

    device = int(config.get('GARMIN', 'DEVICE_ID'))
    user = config.get('GARMIN', 'USER_CODE')
    pw = config.get('GARMIN', 'PASSWORD')

    print(get_user_info(user, pw))
    print(send_user_message(user, pw, device, "Hello World!"))

if __name__ == '__main__':
    main()
