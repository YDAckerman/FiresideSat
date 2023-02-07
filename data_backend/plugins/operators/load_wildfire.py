from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults

import psycopg2.extras

class LoadWildfireData(BaseOperator):

    @apply_defaults
    def __init__(self, postgres_conn_id, api_url,
                 staging_sql, extractors,
                 loaders, *args, **kwargs):

        super(LoadWildfireData, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.url = api_url
        self.extractors = extractors
        self.loaders = loaders

        if len(extractors) != len(loaders):
            raise ValueError("expected loaders and extractors"
                             + "to be the same length")

        def execute(self, context):

            current_date = context.get('data_interval_start')
            start_date = current_date.to_date_string()
            end_date = current_date \
                .add(days=1) \
                .to_date_string()

            http_hook = HttpHook(method='GET',
                                 http_conn_id=self.url.format(start_date,
                                                              end_date))
            response = http_hook.run_and_check()
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

                    incident_values = extractors[0](attributes)
                    perimeter_values = extractors[1](incident_id, rings)

                    pg_cur.execute(loaders[0], incident_values)
                    psycopg2.extras.execute_values(pg_cur,
                                                   loaders[1],
                                                   perimeter_values)

            else:

                self.log.info("No response from Wildfire API endpoint")
