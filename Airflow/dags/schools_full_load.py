from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.hooks.base import BaseHook
import psycopg2
import datetime as dt
import pandas as pd
import os
import io


BASE_PATH = os.path.join(os.getenv('AIRFLOW_HOME'), 'dags')


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


truncate_school_report = SQLExecuteQueryOperator(
    conn_id='supabase_report',
    sql='sqlScripts/truncateSchoolDest.sql',
    task_id='truncate_report_school',
    dag=dag
)


fetch_school_data = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='sqlScripts/getSchoolSource.sql',
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

    os.makedirs(os.path.join(os.getenv('AIRFLOW_HOME'), 'dags', 'tempFiles'), exist_ok=True)
    df.to_csv(os.path.join(os.getenv('AIRFLOW_HOME'), 'dags', 'tempFiles', 'SourceSchool.csv'), index=False)


def _insert_school_table(**kwargs):
    report_conn = BaseHook.get_connection('supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        database=report_conn.schema,
        user=report_conn.login,
        password=report_conn.password
    )

    cursor = conn.cursor()

    with open(os.path.join(BASE_PATH, 'tempFiles', 'SourceSchool.csv'), 'r') as f:
        cursor.copy_expert("""
        COPY school FROM STDIN WITH CSV HEADER DELIMITER ',';
                            """, file=f)
        
    conn.commit()
    cursor.close()

transform_school_data = PythonOperator(
    python_callable=_transform_school,
    dag=dag,
    task_id='transform_school_data'
)


load_school = PythonOperator(
    python_callable=_insert_school_table,
    task_id='load_school_report',
    dag=dag
)




end_task = EmptyOperator(
    task_id='ending_task',
    dag=dag
)



start_dag >> fetch_school_data >> transform_school_data >> load_school >> end_task

