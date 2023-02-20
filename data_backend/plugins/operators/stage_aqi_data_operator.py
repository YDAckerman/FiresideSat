from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import psycopg2.extras
import json


class StageAqiDataOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 api_endpoint,
                 api_key,
                 internal_data_query,
                 extractors,
                 loaders, *args, **kwargs):

        super(StageAqiDataOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.api_endpoint = api_endpoint
        self.api_key = api_key
        self.internal_data_query = internal_data_query
        self.extractors = extractors
        self.loaders = loaders

        if len(extractors) != len(loaders):
            raise ValueError("expected loaders and extractors"
                             + "to be the same length")

    def execute(self, context):

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        pg_cur.execute(self.internal_data_query)
        records = pg_cur.fetchall()

        for record in records:

            # TODO: Need to catch errors here
            incident_id, lon, lat = record

            self.log.info("Inserting aqi staging data for incident: "
                          + incident_id)

            endpoint = self.api_endpoint.format(lat=lat, lon=lon,
                                                key=self.api_key)
            api_response = http_hook.run(endpoint=endpoint)
            response = json.loads(api_response.text)

            if response:

                aqi_values = self.extractors[0](incident_id, response)
                psycopg2.extras.execute_values(pg_cur,
                                               self.loaders[0],
                                               aqi_values)

                pg_conn.commit()

            else:

                self.log.info("No response from AirNow API endpoint")

        pg_conn.close()
