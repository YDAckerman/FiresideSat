from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator
from operators.send_reports_operator import SendReportsOperator

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

dag = DAG('test_user_aqi_report_dag',
          start_date=datetime(2023, 7, 5),
          default_args=default_args,
          description='Send user aqi messages',
          schedule=timedelta(hours=4),
          catchup=False
          )

start_operator = DummyOperator(task_id='Begin_Prod_User_AQI_'
                               + 'Report_Dag_Execution',
                               dag=dag)

send_reports_operator = SendReportsOperator(
    task_id="send_user_aqi_reports",
    postgres_conn_id='fireside_prod',
    http_conn_id='garmin_share',
    message_type='user_aqi_report'
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> send_reports_operator

send_reports_operator >> end_operator
