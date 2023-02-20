from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
from airflow.models import Variable
# from airflow.operators.python_operator import PythonOperator

from operators.stage_aqi_data_operator import StageAqiDataOperator
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

dag = DAG('aqi_dag',
          start_date=datetime(2021, 4, 1),
          end_date=datetime(2021, 4, 2),
          default_args=default_args,
          description='ELT for AQI Conditions',
          schedule_interval=timedelta(days=5),
          max_active_runs=1,
          catchup=True
          )

# ##############################################
#  operator instantiations
# ##############################################

start_operator = DummyOperator(task_id='Begin_AQI_Dag_Execution',
                               dag=dag)


create_staging_aqi = PostgresOperator(
    task_id="create_staging_aqi",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.create_staging_aqi
)

stage_aqi_data_operator = StageAqiDataOperator(
    task_id="stage_aqi_data",
    dag=dag,
    postgres_conn_id="fireside",
    http_conn_id="airnow",
    api_endpoint=ApiCalls.airnow_radius_url,
    api_key=Variable.get("airnow_api_key"),
    internal_data_query=SqlQueries.select_centroids,
    extractors=[DataExtractors.extract_aqi_values],
    loaders=[SqlQueries.insert_staging_aqi]
)

delete_outdated_operator = PostgresOperator(
    task_id="delete_outdated",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.delete_aqi_outdated
)

upsert_current_aqi

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_aqi

create_staging_aqi >> stage_aqi_data_operator

stage_aqi_data_operator >> end_operator
