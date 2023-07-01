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

# ##############################################
#  dag instantiation
# ##############################################

dag = DAG('test_update_usr_loc',
          start_date=datetime(2021, 5, 2),
          end_date=datetime(2021, 5, 3),
          default_args=default_args,
          description='Update User Locations',
          schedule_interval=timedelta(days=1),
          max_active_runs=1,
          catchup=True
          )

start_operator = DummyOperator(task_id='Begin_Test_Update_Usr_Loc_Dag_Execution',
                               dag=dag)

create_staging_trip_points = PostgresOperator(
    task_id="create_staging_trip_points",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_staging_trip_points
)

stage_trip_points = StageDataOperator(
    task_id="stage_kml_feed_data",
    dag=dag,
    postgres_conn_id="fireside",
    http_conn_id="mapshare_feed",
    endpoint_name="mapshare_feed_endpoint"
)

upsert_trip_points = PostgresOperator(
    task_id="upsert_trip_points",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.upsert_trip_points
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> create_staging_trip_points

create_staging_trip_points >> stage_trip_points

stage_trip_points >> upsert_trip_points

upsert_trip_points >> end_operator
