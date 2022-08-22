import requests
import configparser
import os
import json

# three functions:
# get last location
# send message
# get last message


def get_user_feed(user, pw):
    #
    # - queries feed url
    # - returns json response
    #
    url = f"https://share.garmin.com/Feed/Share/{user}"
    response = requests.get(url, auth=('', pw))
    return(json.loads(response.text))


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


def get_last_message(user, pw):
    pass

def main():

    os.chdir('/Users/Yoni/Documents/FiresideSat/project')

    config = configparser.ConfigParser()
    config.read_file(open('inReach.cfg'))

    device = int(config.get('GARMIN', 'DEVICE_ID'))
    user = config.get('GARMIN', 'USER_CODE')
    pw = config.get('GARMIN', 'PASSWORD')

    print(get_user_feed(user, pw))
    print(send_user_message(user, pw, device, "Hello World!"))

    pass


if __name__ == '__main__':
    main()
