from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.operators.python import PythonOperator
from oauth2client.service_account import ServiceAccountCredentials
import pandas as pd
import gspread
from dotenv import load_dotenv
import os
import datetime as dt



ETL_DAG = DAG(
    dag_id='load_from_supa',
    schedule_interval='@daily',
    start_date=dt.datetime(2025, 2, 21)
)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

load_dotenv()

cred_json_path = os.getenv('GOOGLE_CRED_JSON')

def gauthenticate(path=cred_json_path):
    cred = ServiceAccountCredentials.from_json_keyfile_name(path, scopes=SCOPES)
    client = gspread.authorize(cred)
    file =  client.open_by_key('1PZMEIFuMlWwcozguuXRnEtDLHJiLAhl-FqwxkMDAfN0')
    return file


def _print_data(**kwargs):
    ti = kwargs['ti']
    print(ti)
    fetched_data = ti.xcom_pull(task_ids='fetch_from_supa')
    print(fetched_data)




fetch_data_from_supa = SQLExecuteQueryOperator(
    dag=ETL_DAG,
    task_id='fetch_from_supa',
    sql='SELECT * FROM participant_informations;',
    conn_id='supabase_prod',
    do_xcom_push=True
)

print_data = PythonOperator(
    dag=ETL_DAG,
    task_id='print_data',
    python_callable=_print_data,
    provide_context=True
)


fetch_data_from_supa >> print_data





