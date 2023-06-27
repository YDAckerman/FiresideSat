from helpers.sql_queries import SqlQueries
from helpers.api_endpoint import ApiEndpoint, make_headers
from pykml import parser
from datetime import datetime
import psycopg2.extras
import json


class EtlFunctions():

    def __init__(self):
        print("using etl functions")
        self.sql = SqlQueries()
        self.api = ApiEndpoint()

    def load_from_endpoint(self,
                           endpoint, http_hook, pg_hook, context, log):

        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        if endpoint == "wildfire_current_endpoint":

            endpoint = self.api \
                           .format_endpoint("wildfire_current_endpoint",
                                            context)

            self._load_from_wildfire_endpoint(http_hook, endpoint,
                                              pg_conn, pg_cur,
                                              context, log)

        elif endpoint == "wildfire_test_endpoint":

            endpoint = self.api \
                           .format_endpoint("wildfire_test_endpoint",
                                            context)

            self._load_from_wildfire_endpoint(http_hook, endpoint,
                                              pg_conn, pg_cur,
                                              context, log)

        elif endpoint == "airnow_endpoint":

            self._load_from_airnow_endpoint(http_hook, pg_conn,
                                            pg_cur, context, log)

        elif endpoint == "mapshare_feed_endpoint":

            self._load_from_mapshare_endpoint(http_hook,
                                              pg_conn, pg_cur,
                                              context, log)
        else:

            raise ValueError("Unrecognized enpoint")

        pg_conn.close()

    def _load_from_wildfire_endpoint(self, http_hook, endpoint,
                                     pg_conn, pg_cur, context, log):

        response = http_hook.run(endpoint=endpoint)
        response = json.loads(response.text)

        if response:

            # loop through features and
            # load each incident and its perimeter into postgres
            for feature in response['features']:

                attributes = feature['attributes']
                incident_id = attributes['poly_SourceGlobalID']

                rings = feature['geometry']['rings']

                incident_values = self \
                    ._extract_incident_values(attributes)

                log.info("Incident data:" + str(incident_values))

                perimeter_values = self \
                    ._extract_perimeter_values(incident_id, rings)

                log.info("Inserting wildfire staging data for incident: "
                         + incident_id)
                pg_cur.execute(self.sql.insert_staging_incident,
                               incident_values)
                psycopg2.extras.execute_values(pg_cur,
                                               self.sql
                                               .insert_staging_perimeter,
                                               perimeter_values)
                pg_conn.commit()

        else:

            log.info("No response from Wildfire API endpoint")

    def _load_from_mapshare_endpoint(self,
                                     http_hook, pg_conn, pg_cur, context, log):

        current_date = context.get('data_interval_start')

        pg_cur.execute(self.sql.select_active_users,
                       {'current_date': current_date})

        records = pg_cur.fetchall()

        for record in records:

            user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

            log.info("getting mapshare feed data for user: "
                     + str(user_id))

            endpoint = self.api \
                .format_endpoint("mapshare_feed_endpoint",
                                 {"mapshare_id": mapshare_id,
                                  "garmin_imei": garmin_imei}) \

            headers = make_headers(mapshare_id, mapshare_pw)

            api_response = http_hook.run(endpoint=endpoint,
                                         headers=headers)

            if api_response:

                trip_values = [trip_id] \
                    + self._extract_feed_values(api_response)
                pg_cur.execute(self.sql.insert_staging_trip_points,
                               trip_values)

                pg_conn.commit()

            else:

                log.info("No response from MapShare KML Feed endpoint")

    def _load_from_airnow_endpoint(self,
                                   http_hook, pg_conn, pg_cur, context, log):

        pg_cur.execute(self.sql.select_fire_centroids)
        records = pg_cur.fetchall()

        for record in records:

            # TODO: DIST _should_ change depending on the fire (record)
            AQI_RADIUS_MILES = 35
            incident_id, lon, lat = record

            log.info("Inserting aqi staging data for incident: "
                     + incident_id)

            endpoint = self.api \
                .format_endpoint("airnow_endpoint",
                                 {'lat': lat,
                                  'lon': lon,
                                  'radius_miles': AQI_RADIUS_MILES})

            api_response = http_hook.run(endpoint=endpoint)
            response = json.loads(api_response.text)

            if response:

                aqi_values = self._extract_aqi_values(incident_id,
                                                      response)
                psycopg2.extras.execute_values(pg_cur,
                                               self.sql.insert_staging_aqi,
                                               aqi_values)

                pg_conn.commit()

            else:

                log.info("No response from AirNow API endpoint")

    @staticmethod
    def _extract_incident_values(attributes):
        """
        """
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

    @staticmethod
    def _extract_perimeter_values(incident_id, rings):
        """
        """
        return ([(incident_id, i, x[0], x[1])
                 for i in range(len(rings))
                 for x in rings[i]
                 ])

    @staticmethod
    def _extract_aqi_values(incident_id, api_response):
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

    @staticmethod
    def _extract_feed_values(api_response):

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
