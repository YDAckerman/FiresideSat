import inReach as mini
import perimeter
import configparser
from responsehandler import Handler

def main():

    config = configparser.ConfigParser()
    config.read_file(open('inReach.cfg'))

    device = int(config.get('GARMIN', 'DEVICE_ID'))
    user = config.get('GARMIN', 'USER_CODE')
    pw = config.get('GARMIN', 'PASSWORD')

    status = mini.get_user_info(user, pw)
    if status['event'] in ['ON', 'OTHER']:
        
