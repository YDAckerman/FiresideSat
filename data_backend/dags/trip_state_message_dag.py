from datetime import datetime, timedelta
from airflow import DAG
from airflow.operators.dummy_operator import DummyOperator

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

dag = DAG('trip_state_message_dag',
          start_date=datetime(2021, 4, 1),
          end_date=datetime(2021, 4, 2),
          default_args=default_args,
          description='Send trip start/stop messages',
          schedule="@daily",
          max_active_runs=1,
          catchup=True
          )

start_operator = DummyOperator(task_id='Begin_Trip_State_'
                               + 'Message_Dag_Execution',
                               dag=dag)

end_operator = DummyOperator(task_id='Stop_execution', dag=dag)

# ##############################################
#  dag structure
# ##############################################

start_operator >> end_operator
