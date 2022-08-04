
import selenium
import requests
import configparser

# three functions:
# get last location
# send message
# get last message

# get configuration information
# (this will go elsewhere)
config = configparser.ConfigParser()
config.read_file(open('inReach.cfg'))

# get feed for most recently recorded location
url = "https://share.garmin.com/Feed/Share/WURUE"
response = requests.get(url, auth=('', config.get('GARMIN', 'PASSWORD')))
print(response.text)

# access the main website interface
url = "https://share.garmin.com/WURUE"
response = requests.get(url, auth=('', config.get('GARMIN', 'PASSWORD')))
response.status_code
response.text
