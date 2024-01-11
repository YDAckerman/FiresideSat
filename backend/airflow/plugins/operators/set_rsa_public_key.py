from airflow.hooks.postgres_hook import PostgresHook
from airflow.models import BaseOperator
from airflow.models import Variable
from airflow.utils.decorators import apply_defaults
from helpers.sql_queries import SqlQueries as sql


class SetPublicKeyOperator(BaseOperator):

    @apply_defaults
    def __init__(self,
                 postgres_conn_id,
                 *args, **kwargs):

        super(SetPublicKeyOperator, self).__init__(*args, **kwargs)
        self.pg_conn_id = postgres_conn_id

    def execute(self, context):

        pem = Variable.get("rsa_public_key_pem")

        pg_hook = PostgresHook(postgres_conn_id=self.pg_conn_id)
        pg_conn = pg_hook.get_conn()
        pg_cur = pg_conn.cursor()

        pg_cur.execute(sql.reset_public_key, {'pem': pem})
        pg_conn.commit()
        pg_conn.close()
