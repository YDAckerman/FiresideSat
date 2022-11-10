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
        with open('fireside_log.txt', 'r') as f:

            # TODO: This should be using sqlite or something
            # note the log file...
            
            # use previously recorded hashes to make
            # sure we don't send a message based on
            # the same information twice
            log_lines = f.readlines()
            last_hash = log_lines[-1].split(" ")[-1]
            old_hashes = [line.split(" ")[-1] for line in log_lines[0:-1]
                          if 'HASH' in line]

            if last_hash not in old_hashes:
                msg = api.build_message(loc=[status['lon'], status['lat']])
                if len(msg) > 0:
                    garmin_response = mini.send_user_message(user, pw,
                                                             device, msg)
                    # log the response
                    log.info(f'RESPONSE:{garmin_response}')
                else:
                    # log that there were no new incidents to report
                    log.info('NO NEW INCIDENTS')

    else:
        # log that the device was in the OFF state
        log.info('Tracking is turned OFF')

if __name__ == '__main__':
    main()
