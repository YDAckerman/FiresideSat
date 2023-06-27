from airflow.hooks.postgres_hook import PostgresHook
from airflow.hooks.http_hook import HttpHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers.comms import Comms


class SendReportsOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 http_conn_id,
                 message_type,
                 *args, **kwargs):

        super(SendReportsOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.http_conn_id = http_conn_id
        self.message_type = message_type

    def execute(self, context):

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        http_hook = HttpHook(method='POST',
                             http_conn_id=self.http_conn_id)

        Comms(http_hook, pg_hook) \
            .send_messages(self.message_type, context, self.log)
