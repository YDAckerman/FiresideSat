from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers.etl_functions import EtlFunctions


class StageDataOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 api_endpoint,
                 *args, **kwargs):

        super(StageDataOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.api_endpoint = api_endpoint

    def execute(self, context):

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)
        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)

        EtlFunctions() \
            .load_from_endpoint(self.api_endpoint,
                                http_hook,
                                pg_hook,
                                context,
                                self.log)
