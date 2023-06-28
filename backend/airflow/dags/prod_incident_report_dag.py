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

dag = DAG('prod_incident_report_dag',
          start_date=datetime(2023, 6, 20),
          default_args=default_args,
          description='Send Incident Reports',
          schedule=timedelta(hours=12))

start_operator = DummyOperator(task_id='Begin_Incident_'
                               + 'Report_Dag_Execution',
                               dag=dag)

send_reports_operator = SendReportsOperator(
    task_id="send_incident_reports",
    postgres_conn_id='fireside_prod',
    http_conn_id='garmin_share',
    message_type='incident_report'
)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> send_reports_operator

send_reports_operator >> end_operator
