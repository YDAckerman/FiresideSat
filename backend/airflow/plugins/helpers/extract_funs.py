from pykml import parser
from datetime import datetime

FIRE_INCIDENT_ATTR_KEYS = [
        'UniqueFireIdentifier',
        'IncidentName',
        'FireBehaviorGeneral',
        'IncidentSize',
        'PercentContained',
        'CreatedOnDateTime_dt',
        'ModifiedOnDateTime_dt'
    ]


def extract_incident_attr(feature):

    attributes = feature['attributes']
    lon_lat = list(feature['geometry'].values())
    incident_attr = [attributes[x] for x in FIRE_INCIDENT_ATTR_KEYS]

    return (incident_attr + lon_lat)


def extract_perimeter_attr(feature):

    attributes = feature['attributes']
    incident_id = attributes['attr_UniqueFireIdentifier']
    rings = feature['geometry']['rings']
    return ([(incident_id, i, x[0], x[1])
             for i in range(len(rings))
             for x in rings[i]
             ])


def extract_aqi_attr(spatial_object_id, api_response):
    """
    - loop through api_result
    - for each record, get date and location/aqi recorded
    - return list of tuples
    """
    tuples_list = [(spatial_object_id,
                    x['DateObserved'],
                    x['HourObserved'],
                    x['Latitude'],
                    x['Longitude'],
                    x['AQI']) for x in api_response]
    return tuples_list


def extract_feed_attr(api_response):

    # see for details on kml feed:
    # https://support.garmin.com/en-US/?faq=tdlDCyo1fJ5UxjUbA9rMY8

    root = parser.fromstring(bytes(api_response.text, encoding='utf8'))

    # need to convert to datetime
    time_point_added_str = str(root.Document
                               .Folder
                               .Placemark.TimeStamp
                               .when)
    time_point_added = datetime.strptime(time_point_added_str,
                                         '%Y-%m-%dT%H:%M:%SZ')

    coords = str(root.Document.Folder.Placemark.Point.coordinates)
    course = str(root.Document
                 .Folder
                 .Placemark.ExtendedData
                 .Data[12].value)

    return [time_point_added, *coords.split(",")[0:2], course]
