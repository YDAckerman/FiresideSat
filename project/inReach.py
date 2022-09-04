import requests
import configparser
import json
import re


def get_user_info(user, pw):
    #
    # - queries feed url
    # - returns json response

    url = f"https://explore.garmin.com/feed/share/{user}"

    # url = f"https://explore.garmin.com/feed/share/{user}" + \
    #     "?d1=2022-08-01T06:00z&d2=2022-10-01T15:00z"
    response = requests.get(url, auth=(user, pw))

    coords = re.findall(r'<coordinates>(\S+),(\S+),(\S+)</coordinates>',
                        response.text)[0]

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
    #
    url = f"https://share.garmin.com/{user}/Map/SendMessageToDevices"
    myobj = {'deviceIds': device,
             'fromAddr': 'assistant@firesidesat.com',
             'messageText': msg}
    response = requests.post(url, auth=('', pw), json=myobj)
    return(json.loads(response.text)["success"])


def main():

    config = configparser.ConfigParser()
    config.read_file(open('/Users/Yoni/Documents/FiresideSat/project/inReach.cfg'))

    device = int(config.get('GARMIN', 'DEVICE_ID'))
    user = config.get('GARMIN', 'USER_CODE')
    pw = config.get('GARMIN', 'PASSWORD')

    print(get_user_info(user, pw))
    print(send_user_message(user, pw, device, "Hello World!"))

if __name__ == '__main__':
    main()
