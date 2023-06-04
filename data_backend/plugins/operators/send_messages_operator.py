from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.utils.decorators import apply_defaults
from helpers.comms import Comms


class SendMessagesOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 service_name,
                 message_type,
                 *args, **kwargs):

        super(SendMessagesOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id
        self.service_name = service_name
        self.message_type = message_type

    def execute(self, context):

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)

        Comms().send_messages(self.service_name,
                              self.message_type,
                              pg_hook,
                              context,
                              self.log)
