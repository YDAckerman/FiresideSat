from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from operators.stage_data_operator import StageDataOperator
from helpers.sql_queries import SqlQueries as sql

# ##############################################
#  default arguments
# ##############################################

default_args = {
    'owner': 'Yoni Ackerman',
    'retries': 0,
    'retry_delay': timedelta(minutes=3)
}

POSTGRES_DB = "fireside_prod"

# ##############################################
#  dag instantiation
# ##############################################

dag = DAG('prod_update_incidents_dag',
          start_date=datetime(2023, 7, 4),
          default_args=default_args,
          description='ELT for Wildfire Conditions',
          schedule_interval='@hourly',
          catchup=False
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_Update_Incidents_Dag_Execution',
                               dag=dag)

create_staging_tables = PostgresOperator(
    task_id="create_staging_tables",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.create_staging_tables
)

stage_wildfire_data = StageDataOperator(
    task_id="stage_wildfire_data",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    http_conn_id="wildfire_api",
    endpoint_name="current_locations"
)

# TODO
# upsert_staging_centroids = PostgresOperator(
#     task_id="upsert_staging_centroids",
#     dag=dag,
#     postgres_conn_id=POSTGRES_DB,
#     sql=sql.upsert_staging_centroids
# )

insert_updated_outdated = PostgresOperator(
    task_id="insert_updated_outdated",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.insert_updated_outdated
)

delete_all_outdated = PostgresOperator(
    task_id="delete_all_outdated",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.delete_all_outdated
)

upsert_current_incident = PostgresOperator(
    task_id="upsert_current_incident",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.upsert_current_incident
)

# stage_perimeter_data = StageDataOperator(
#     task_id="stage_perimeter_data",
#     dag=dag,
#     postgres_conn_id=POSTGRES_DB,
#     http_conn_id="wildfire_api",
#     endpoint_name="current_perimeters"
# )

# upsert_current_perimeter = PostgresOperator(
#     task_id="upsert_current_perimeter",
#     dag=dag,
#     postgres_conn_id=POSTGRES_DB,
#     sql=sql.upsert_current_perimeter
# )

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_tables

create_staging_tables >> stage_wildfire_data

stage_wildfire_data >> insert_updated_outdated

insert_updated_outdated >> delete_all_outdated

delete_all_outdated >> upsert_current_incident

upsert_current_incident >> end_operator


# >> stage_perimeter_data

# stage_perimeter_data >> upsert_current_perimeter

# upsert_current_perimeter
