from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import psycopg2.extras
import json


class StageTripPointsOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 api_endpoint,
                 internal_data_query,
                 extractors,
                 loaders, *args, **kwargs):

        super(StageTripPointsOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.api_endpoint = api_endpoint
        self.internal_data_query = internal_data_query
        self.extractors = extractors
        self.loaders = loaders

        if len(extractors) != len(loaders):
            raise ValueError("expected loaders and extractors"
                             + "to be the same length")

    def execute(self, context):

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        current_date = context.get('data_interval_start').to_date_string()
        pg_cur.execute(self.internal_data_query, current_date)
        records = pg_cur.fetchall()

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)

        for record in records:

            user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

            self.log.info("getting mapshare feed data for user: "
                          + user_id)

            endpoint = self.api_endpoint.format(user=mapshare_id,
                                                imei=garmin_imei)
            auth = {"auth": (mapshare_pw)}

            # need auth (?)
            api_response = http_hook.run(endpoint=endpoint,
                                         headers=auth)

            # note, the kml response gives the last point ONLY!
            response = json.loads(api_response.text)

            if response:

                # not currently loading properly
                trip_point_values = self.extractors[0](response)
                psycopg2.extras.execute_values(pg_cur,
                                               self.loaders[0],
                                               aqi_values)

                pg_conn.commit()

            else:

                self.log.info("No response from AirNow API endpoint")

        pg_conn.close()
