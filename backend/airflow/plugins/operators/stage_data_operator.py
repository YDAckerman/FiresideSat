from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers.etl import ELTProcess


class StageDataOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 endpoint_name,
                 *args, **kwargs):

        super(StageDataOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.endpoint_name = endpoint_name

    def execute(self, context):

        http_hook = HttpHook(method='GET',
                             http_conn_id=self.http_conn_id)

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)

        elt = ELTProcess(self.endpoint_name, http_hook,
                         pg_hook, context, self.log)

        elt.run()
