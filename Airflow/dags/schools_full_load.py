from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from airflow.operators.empty import EmptyOperator
from airflow.operators.bash import BashOperator
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

    os.makedirs(os.path.join(BASE_PATH, 'dags', 'tempFiles'), exist_ok=True)
    df.to_csv(os.path.join(BASE_PATH, 'dags', 'tempFiles', 'SourceSchool.csv'), index=False)


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


remove_school_csv = BashOperator(
    bash_command='rm -f $AIRFLOW_HOME/dags/tempFiles/SourceSchool.csv',
    task_id='remove_school_csv',
    dag=dag
)


truncate_seneca_programs_report = SQLExecuteQueryOperator(
    conn_id='supabase_report',
    sql='sqlScripts/truncateSenecaProgramsDest.sql',
    task_id='truncate_seneca_programs',
    dag=dag
)


fetch_seneca_programs = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='sqlScripts/getSenecaProgramsSource.sql',
    task_id='fetch_seneca_programs',
    do_xcom_push=True
)


def _transform_seneca_programs(**kwargs):
    ti = kwargs['ti']
    fetched_data = ti.xcom_pull('fetch_seneca_programs')
    columns = ['program_id', 'program_name']
    df = pd.DataFrame(fetched_data, columns=columns)
    os.makedirs(os.path.join(BASE_PATH, 'dags', 'tempFiles'), exist_ok=True)
    df.to_csv(os.path.join(BASE_PATH, 'dags', 'tempFiles', 'SourceSenecaPrograms.csv'), index=False)



transform_programs_data = PythonOperator(
    python_callable=_transform_seneca_programs,
    task_id='transform_seneca_progams',
    dag=dag,
    provide_context=True
)


def _insert_sencea_programs(**kwargs):
    report_conn = BaseHook.get_connection('supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        database=report_conn.schema,
        user=report_conn.login,
        password=report_conn.password
    )

    cursor = conn.cursor()
    with open(os.path.join(BASE_PATH, 'dags', 'tempFiles', 'SourceSenecaPrograms.csv'), 'r') as f:
        cursor.copy_expert("""
                COPY seneca_programs FROM STDIN WITH CSV HEADER DELIMITER ',';
                    """, f)
    cursor.close()
    conn.close()




load_seneca_programs = PythonOperator(
    python_callable=_insert_sencea_programs,
    task_id='load_seneca_programs',
    dag=dag
)


remove_seneca_programs_csv = BashOperator(
    bash_command='rm -f $AIRFLOW_HOME/dags/tempFiles/SourceSenecaPrograms.csv',
    task_id='remove_seneca_programs_csv',
    dag=dag
)


participants_placeholder = EmptyOperator(
    task_id='participants_placeholder',
    dag=dag
)



end_task = EmptyOperator(
    task_id='ending_task',
    dag=dag
)



start_dag >> [truncate_school_report, truncate_seneca_programs_report]

truncate_school_report >> fetch_school_data >> transform_school_data >> load_school >> remove_school_csv
truncate_seneca_programs_report >> fetch_seneca_programs >> transform_programs_data >> load_seneca_programs >> remove_seneca_programs_csv

[remove_school_csv, remove_seneca_programs_csv] >> participants_placeholder >> end_task

