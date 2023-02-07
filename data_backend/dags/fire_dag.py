from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.operators.python_operator import PythonOperator

from airflow.operators import (LoadWildfireData)

from helpers import SqlQueries
from helpers import DataExtractors
from helpers import ApiCalls

default_args = {
    'owner': 'Yoni Ackerman',
    'start_date': datetime(2018, 11, 1),
    'end_date': datetime(2018, 11, 3),
    'retries': 0,
    'retry_delay': timedelta(seconds=5),
}

dag = DAG('fire_dag',
          default_args=default_args,
          description='ELT for Wildfire Conditions',
          schedule_interval=timedelta(hours=5),
          max_active_runs=1,
          catchup=True
          )

start_operator = DummyOperator(task_id='Being_Fire_Dag_Execution')

staging_tables_operator = PostgresOperator(
    task_id="create_staging_tables",
    postgress_conn_id="airflow",
    sql=SqlQueries.create_staging_tables
)

load_data_operator = LoadWildfireData(
    task_id="load_wildfire_data",
    postgress_conn_id="airflow",
    api_url=ApiCalls.wildfire_incidents_test_url,
    extractors=[DataExtractors.extract_wildfire_incident_values,
                DataExtractors.extract_wildfire_perimeter_values]
    loaders=[SqlQueries.insert_staging_incident,
             SqlQueries.insert_staging_perimeter]
)
