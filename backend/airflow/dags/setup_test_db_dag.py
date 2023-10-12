from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.postgres_operator import PostgresOperator
# from airflow.operators.python_operator import PythonOperator
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

dag = DAG('setup_test_db_dag',
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

start_operator = DummyOperator(task_id='Begin_Setup_Test_DB_Execution',
                               dag=dag)

drop_current_tables = PostgresOperator(
    task_id="drop_current_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.drop_current_tables
)

create_current_tables = PostgresOperator(
    task_id="create_current_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_current_tables
)

drop_user_table = PostgresOperator(
    task_id="drop_user_table",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.drop_user_table
)

create_user_table = PostgresOperator(
    task_id="create_user_table",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_user_table
)

drop_trip_tables = PostgresOperator(
    task_id="drop_trip_table",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.drop_trip_tables
)

create_trip_tables = PostgresOperator(
    task_id="create_trip_table",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_trip_tables
)

drop_report_tables = PostgresOperator(
    task_id="drop_report_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.drop_report_tables
)

create_report_tables = PostgresOperator(
    task_id="create_report_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_report_tables
)

drop_variables_table = PostgresOperator(
    task_id="drop_variables_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.drop_variables_table
)

create_variables_table = PostgresOperator(
    task_id="create_variables_tables",
    dag=dag,
    postgres_conn_id="fireside",
    sql=sql.create_variables_table
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

# clearly could use some abstraction here

start_operator >> drop_current_tables

drop_current_tables >> create_current_tables

create_current_tables >> end_operator

# users table
start_operator >> drop_user_table

drop_user_table >> create_user_table

create_user_table >> end_operator

# trips table
start_operator >> drop_trip_tables

drop_trip_tables >> create_trip_tables

create_trip_tables >> end_operator

# report tables
start_operator >> drop_report_tables

drop_report_tables >> create_report_tables

create_report_tables >> end_operator

# variables table
start_operator >> drop_variables_table

drop_variables_table >> create_variables_table

create_variables_table >> end_operator
