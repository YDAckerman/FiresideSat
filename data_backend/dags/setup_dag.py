from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
# from airflow.operators.python_operator import PythonOperator
from helpers.sql_queries import SqlQueries

# ##############################################
#  default arguments
# ##############################################

default_args = {
    'owner': 'Yoni Ackerman',
    'retries': 0,
    'retry_delay': timedelta(minutes=3)
}

# ##############################################
#  dag instantiation
# ##############################################

dag = DAG('setup_dag',
          start_date=datetime(2021, 4, 1),
          end_date=datetime(2021, 4, 1),
          default_args=default_args,
          description='Setup for Wildfire Conditions',
          schedule_interval=timedelta(days=1),
          max_active_runs=1,
          catchup=True
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_Setup_Execution',
                               dag=dag)

drop_current_tables = PostgresOperator(
    task_id="drop_current_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.drop_current_tables
)

create_current_tables = PostgresOperator(
    task_id="create_current_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.create_current_tables
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> drop_current_tables

drop_current_tables >> create_current_tables

create_current_tables >> end_operator
