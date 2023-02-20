from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import psycopg2.extras
import json


class StageWildfireDataOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 api_endpoint,
                 extractors,
                 loaders, *args, **kwargs):

        super(StageWildfireDataOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.api_endpoint = api_endpoint
        self.extractors = extractors
        self.loaders = loaders

        if len(extractors) != len(loaders):
            raise ValueError("expected loaders and extractors"
                             + "to be the same length")

    def execute(self, context):

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)

        current_date = context.get('data_interval_start')
        start_date = current_date.to_date_string()
        end_date = current_date \
            .add(days=1) \
            .to_date_string()

        endpoint = self.api_endpoint.format(start_date, end_date)
        api_response = http_hook.run(endpoint=endpoint)
        response = json.loads(api_response.text)

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        if response:

            # loop through features and
            # load each incident and its perimeter into postgres
            for feature in response['features']:

                attributes = feature['attributes']
                incident_id = attributes['poly_GlobalID']
                rings = feature['geometry']['rings']

                incident_values = self.extractors[0](attributes)
                perimeter_values = self.extractors[1](incident_id,
                                                      rings)

                self.log.info("Inserting wildfire staging data for incident: "
                              + incident_id)
                pg_cur.execute(self.loaders[0], incident_values)
                psycopg2.extras.execute_values(pg_cur,
                                               self.loaders[1],
                                               perimeter_values)
                pg_conn.commit()

        else:

            self.log.info("No response from Wildfire API endpoint")

        pg_conn.close()
