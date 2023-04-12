from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
# from airflow.operators.python_operator import PythonOperator

from operators.stage_trip_points_operator import StageTripPointsOperator
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

dag = DAG('test_kml_feed_dag',
          start_date=datetime(2021, 4, 1),
          end_date=datetime(2021, 4, 2),
          default_args=default_args,
          description='ELT for kml feed',
          schedule_interval=timedelta(days=5),
          max_active_runs=1,
          catchup=True
          )

start_operator = DummyOperator(task_id='Begin_kml_feed_Dag_Execution',
                               dag=dag)

create_staging_trip_points = PostgresOperator(
    task_id="create_staging_trip_points",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.create_staging_trip_points
)

stage_trip_points = StageTripPointsOperator(
    task_id="stage_kml_feed_data",
    dag=dag,
    postgres_conn_id="fireside",
    http_conn_id="mapshare_feed",
    api_endpoint=ApiCalls.mapshare_feed_endpoint,
    internal_data_query=SqlQueries.select_active_users,
    extractors=[DataExtractors.extract_feed_values],
    loaders=[SqlQueries.insert_staging_trip_points]
)

upsert_trip_points = PostgresOperator(
    task_id="upsert_trip_points",
    dag=dag,
    postgres_conn_id="fireside",
    sql=SqlQueries.upsert_trip_points
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_trip_points

create_staging_trip_points >> stage_trip_points

stage_trip_points >> upsert_trip_points

upsert_trip_points >> end_operator
