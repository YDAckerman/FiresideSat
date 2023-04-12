from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
import base64


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

        current_date = context.get('data_interval_start')

        pg_cur.execute(self.internal_data_query,
                       [current_date]*2)

        records = pg_cur.fetchall()

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)

        for record in records:

            user_id, trip_id, garmin_imei, mapshare_id, mapshare_pw = record

            self.log.info("getting mapshare feed data for user: "
                          + str(user_id))

            endpoint = self.api_endpoint.format(user=mapshare_id,
                                                imei=garmin_imei)

            usr_pw = f'{mapshare_id}:{mapshare_pw}'
            b64_val = base64.b64encode(usr_pw.encode()).decode()
            headers = {"Authorization": "Basic %s" % b64_val}

            # need auth (?)
            api_response = http_hook.run(endpoint=endpoint,
                                         headers=headers)

            if api_response:

                trip_values = [trip_id] + self.extractors[0](api_response)

                pg_cur.execute(self.loaders[0], trip_values)

                pg_conn.commit()

            else:

                self.log.info("No response from MapShare KML Feed endpoint")

        pg_conn.close()
