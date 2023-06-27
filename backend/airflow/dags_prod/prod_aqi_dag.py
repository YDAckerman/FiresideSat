from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from operators.stage_data_operator import StageDataOperator
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

dag = DAG('prod_aqi_dag',
          start_date=datetime(2023, 6, 20),
          default_args=default_args,
          description='ELT for AQI Conditions',
          schedule_interval='@hourly'
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_AQI_Dag_Execution',
                               dag=dag)


create_staging_aqi = PostgresOperator(
    task_id="create_staging_aqi",
    dag=dag,
    postgres_conn_id="fireside_prod",
    sql=SqlQueries.create_staging_aqi
)

stage_aqi_data_operator = StageDataOperator(
    task_id="stage_aqi_data",
    dag=dag,
    postgres_conn_id="fireside_prod",
    http_conn_id="airnow",
    api_endpoint="airnow_endpoint"
)

upsert_current_operator = PostgresOperator(
    task_id="upsert_current",
    dag=dag,
    postgres_conn_id="fireside_prod",
    sql=SqlQueries.upsert_current_aqi
)

delete_outdated_operator = PostgresOperator(
    task_id="delete_outdated",
    dag=dag,
    postgres_conn_id="fireside_prod",
    sql=SqlQueries.delete_aqi_outdated
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_aqi

create_staging_aqi >> stage_aqi_data_operator

stage_aqi_data_operator >> upsert_current_operator

upsert_current_operator >> delete_outdated_operator

delete_outdated_operator >> end_operator
