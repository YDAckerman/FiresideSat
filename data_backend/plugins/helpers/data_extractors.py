from pykml import parser
from pykml import util



class DataExtractors():

    def extract_wildfire_incident_values(attributes):
        """
        """
        attribute_keys = [
            'poly_SourceGlobalID',
            'poly_IncidentName',
            'attr_FireBehaviorGeneral',
            'attr_CalculatedAcres',
            'attr_PercentContained',
            'poly_DateCurrent',
            'poly_CreateDate'
        ]

        # None holds the lat/lon centroid values that
        # will come as part of the transform step
        return ([attributes[x] for x in attribute_keys] + [None])

    def extract_wildfire_perimeter_values(incident_id, rings):
        """
        """
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

    def extract_kml_feed_points(api_response):

        # see for details on kml feed:
        # https://support.garmin.com/en-US/?faq=tdlDCyo1fJ5UxjUbA9rMY8

        root = parser.fromstring(bytes(api_response.text, encoding='utf8'))
        timestamp = str(root.Document.Folder.Placemark.TimeStamp.when)
        coords = str(root.Document.Folder.Placemark.Point.coordinates)
        device_id = str(root.Document.Folder.Placemark.ExtendedData.Data[7].value)

        return [timestamp, coords.split(",")[0:2], device_id]
