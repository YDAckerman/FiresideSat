from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
# from airflow.operators.python_operator import PythonOperator

from operators.stage_wildfire_data_operator import StageWildfireDataOperator
from helpers.sql_queries import SqlQueries
from helpers.data_extractors import DataExtractors
from helpers.api_calls import ApiCalls

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

dag = DAG('fire_dag',
          start_date=datetime(2021, 4, 1),
          end_date=datetime(2021, 4, 2),
          default_args=default_args,
          description='ELT for Wildfire Conditions',
          schedule_interval=timedelta(days=5),
          max_active_runs=1,
          catchup=True
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_Fire_Dag_Execution',
                               dag=dag)

create_current_tables = PostgresOperator(
    task_id="create_current_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.create_current_tables
)

create_staging_tables = PostgresOperator(
    task_id="create_staging_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.create_staging_tables
)

stage_wildfire_data = StageWildfireDataOperator(
    task_id="load_wildfire_data",
    dag=dag,
    postgres_conn_id="fireside",
    http_conn_id="wildfire_api",
    api_endpoint=ApiCalls.wildfire_incidents_test_endpoint,
    extractors=[DataExtractors.extract_wildfire_incident_values,
                DataExtractors.extract_wildfire_perimeter_values],
    loaders=[SqlQueries.insert_staging_incident,
             SqlQueries.insert_staging_perimeter]
)

insert_updated_outdated = PostgresOperator(
    task_id="insert_updated_outdated",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.insert_updated_outdated
)

delete_all_outdated = PostgresOperator(
    task_id="delete_all_outdated",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.delete_all_outdated
)

upsert_current_incident = PostgresOperator(
    task_id="upsert_current_incident",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.upsert_current_incident
)

upsert_current_perimeter = PostgresOperator(
    task_id="upsert_current_perimeter",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.upsert_current_perimeter
)

upsert_current_bounding_box = PostgresOperator(
    task_id="upsert_current_bounding_box",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.upsert_current_bounding_box
)

upsert_current_centroids = PostgresOperator(
    task_id="upsert_current_centroids",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.upsert_incident_centroids
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_tables

create_staging_tables >> stage_wildfire_data

stage_wildfire_data >> insert_updated_outdated

insert_updated_outdated >> delete_all_outdated

delete_all_outdated >> upsert_current_incident

upsert_current_incident >> upsert_current_perimeter

upsert_current_perimeter >> upsert_current_bounding_box

upsert_current_bounding_box >> upsert_current_centroids

upsert_current_centroids >> end_operator
