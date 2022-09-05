import inReach as mini
from fire_api import FireAPI
import configparser
from log import log

def main():

    config = configparser.ConfigParser()
    config.read_file(open('inReach.cfg'))

    device = int(config.get('GARMIN', 'DEVICE_ID'))
    user = config.get('GARMIN', 'USER_CODE')
    pw = config.get('GARMIN', 'PASSWORD')

    status = mini.get_user_info(user, pw)
    if status['event'] in ['ON', 'OTHER']:
        api = FireAPI()
        api_hash = hash(api)
        # get hash of previous message
        with open('last_hash.txt', 'wr') as f:
            last_hash = f.readlines()[-1]
            if last_hash != api_hash:
                msg = api.build_message(loc=[status['lon'], status['lat']])
                if len(msg) > 0: # and hash is different from previous
                    mini.send_user_message(user, pw, device, msg)
                    # log the response
                    # https://docs.python.org/3/howto/logging.html
                else:
                    # log that there were no new incidents to report
    else:
        # log that the device was in the OFF state

if __name__ == '__main__':
    main()
