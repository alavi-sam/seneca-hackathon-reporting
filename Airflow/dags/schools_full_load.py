from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
import datetime as dt
import pandas as pd
import io


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': dt.datetime(2025, 2, 25),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1
}


dag = DAG(
    dag_id='full_load',
    default_args=default_args,
    schedule_interval='@daily'
)

start_dag = EmptyOperator(
    task_id='start_process',
    dag=dag
)

fetch_school_data = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='./sqlScripts/getSchool.sql',
    do_xcom_push=True,
    dag=dag,
    task_id='fetch_school_from_prod'
)


def _transform_school(**kwargs):
    ti = kwargs['ti']
    fetched_data = ti.xcom_pull('fetch_school_from_prod')
    if not fetched_data:
        raise ValueError("No school was recieved from Source SQL")
    column_names = ['school_id', 'school_name', 'province', 'city']
    df = pd.DataFrame(fetched_data, columns=column_names)



