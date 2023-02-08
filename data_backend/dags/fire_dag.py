from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
# from airflow.operators.python_operator import PythonOperator

from operators.load_wildfire_data_operator import LoadWildfireDataOperator
from helpers.sql_queries import SqlQueries
from helpers.data_extractors import DataExtractors
from helpers.api_calls import ApiCalls

# ##############################################
#  default arguments
# ##############################################

default_args = {
    'owner': 'Yoni Ackerman',
    'start_date': datetime(2018, 11, 1),
    'end_date': datetime(2018, 11, 3),
    'retries': 0,
    'retry_delay': timedelta(seconds=5),
}

# ##############################################
#  dag instantiation
# ##############################################

dag = DAG('fire_dag',
          default_args=default_args,
          description='ELT for Wildfire Conditions',
          schedule_interval=timedelta(hours=5),
          max_active_runs=1,
          catchup=True
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_Fire_Dag_Execution',
                               dag=dag)

create_staging_tables = PostgresOperator(
    task_id="create_staging_tables",
    dag=dag,
    postgres_conn_id="postgres_default",
    sql=SqlQueries.create_staging_tables
)

load_wildfire_data = LoadWildfireDataOperator(
    task_id="load_wildfire_data",
    dag=dag,
    postgres_conn_id="postgres_default",
    api_url=ApiCalls.wildfire_incidents_test_url,
    extractors=[DataExtractors.extract_wildfire_incident_values,
                DataExtractors.extract_wildfire_perimeter_values],
    loaders=[SqlQueries.insert_staging_incident,
             SqlQueries.insert_staging_perimeter]
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_tables

create_staging_tables >> load_wildfire_data

load_wildfire_data >> end_operator
