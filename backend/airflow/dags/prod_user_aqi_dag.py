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

dag = DAG('prod_user_aqi_dag',
          start_date=datetime(2023, 7, 4),
          default_args=default_args,
          description='ELT for User AQI Conditions',
          schedule_interval='@hourly',
          catchup=False
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_AQI_Dag_Execution',
                               dag=dag)


create_staging_aqi = PostgresOperator(
    task_id="create_staging_user_aqi",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.create_staging_aqi
)

stage_aqi_data_operator = StageDataOperator(
    task_id="stage_aqi_data",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    http_conn_id="airnow",
    endpoint_name="airnow_trip_points"
)

upsert_current_operator = PostgresOperator(
    task_id="upsert_current",
    dag=dag,
    postgres_conn_id=POSTGRES_DB,
    sql=sql.upsert_trip_points_aqi
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_aqi

create_staging_aqi >> stage_aqi_data_operator

stage_aqi_data_operator >> upsert_current_operator

upsert_current_operator >> end_operator
