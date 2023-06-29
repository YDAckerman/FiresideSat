from pykml import parser
from datetime import datetime


def extract_incident_values(attributes):

    # Need to add 'geometry:{x:, y:}'
    attribute_keys = [
        'poly_SourceGlobalID', # SourceGlobalId
        'poly_IncidentName',   # IncidentName
        'attr_FireBehaviorGeneral', # FireBehaviorGeneral
        'attr_CalculatedAcres', # IncidentSize
        'attr_PercentContained', # PercentContained
        'poly_DateCurrent', # ModifiedOnDateTime_dt
        'poly_CreateDate'# CreatedOnDateTime_dt
    ]

    # None holds the lat/lon centroid values that
    # will come as part of the transform step
    return ([attributes[x] for x in attribute_keys] + [None])


def extract_perimeter_values(incident_id, rings):

    return ([(incident_id, i, x[0], x[1])
             for i in range(len(rings))
             for x in rings[i]
             ])


def extract_aqi_values(incident_id, api_response):
    """
    - loop through api_result
    - for each record, get date and location/aqi recorded
    - return list of tuples
    """
    tuples_list = [(incident_id,
                    x['DateObserved'],
                    x['HourObserved'],
                    x['Latitude'],
                    x['Longitude'],
                    x['AQI']) for x in api_response]
    return tuples_list


def extract_feed_values(api_response):

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