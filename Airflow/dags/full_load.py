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
import requests
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

    os.makedirs(os.path.join(BASE_PATH, 'tempFiles'), exist_ok=True)
    df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'SourceSchool.csv'), index=False)


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
    conn.close()

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
    os.makedirs(os.path.join(BASE_PATH, 'tempFiles'), exist_ok=True)
    df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'SourceSenecaPrograms.csv'), index=False)



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
    with open(os.path.join(BASE_PATH, 'tempFiles', 'SourceSenecaPrograms.csv'), 'r') as f:
        cursor.copy_expert("""
                COPY seneca_programs FROM STDIN WITH CSV HEADER DELIMITER ',';
                    """, f)
    conn.commit()
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


dummy_task = EmptyOperator(
    task_id='bridge_between_tasks',
    dag=dag
)



truncate_participants_report = SQLExecuteQueryOperator(
    conn_id='supabase_report',
    sql='sqlScripts/truncateParticipantsDest.sql',
    task_id='truncate_participants_table',
    dag=dag
)


fetch_participants_data = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='sqlScripts/getParticipantsSource.sql',
    task_id='fetch_participants_data',
    do_xcom_push=True
)



def _transform_participants(**kwargs):
    ti = kwargs['ti']
    participants_data = ti.xcom_pull('fetch_participants_data')
    columns = ['participant_id', 'firstname', 'lastname', 'email', 'phone_number', 'is_alumni', 'graduation_year',
               'graduation_month', 'from_seneca', 'school_id', 'semester_number', 'shirt_size', 'seneca_program_id',
               'is_solo', 'having_team', 'degree_type', 'study_field_name', 'registered_at']
    df = pd.DataFrame(participants_data, columns=columns)
    mask = df['seneca_program_id'].notnull()
    df.loc[mask, 'seneca_program_id'] = df.loc[mask, 'seneca_program_id'].astype(int)
    df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'SourceParticipants.csv'), index=False, float_format="%.0f")


transform_participants_data = PythonOperator(
    python_callable=_transform_participants,
    task_id='transform_participants',
    dag=dag,
    provide_context=True
)


def _insert_participants(**kwargs):
    report_conn = BaseHook.get_connection(conn_id='supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        user=report_conn.login,
        password=report_conn.password,
        database=report_conn.schema
    )

    cursor = conn.cursor()
    with open(os.path.join(BASE_PATH, 'tempFiles', 'SourceParticipants.csv'), 'r') as f:
        cursor.copy_expert("""
            COPY participants FROM STDIN WITH CSV HEADER DELIMITER ',';
    """, f)
    
    conn.commit()
    cursor.close()
    conn.close()



load_participants = PythonOperator(
    python_callable=_insert_participants,
    task_id='load_participants',
    dag=dag
)


remove_participants_csv = BashOperator(
    bash_command='rm -f $AIRFLOW_HOME/dags/tempFiles/SourceParticipants.csv',
    task_id='remove_participants_csv',
    dag=dag
)


truncate_teams_report = SQLExecuteQueryOperator(
    conn_id='supabase_report',
    sql='sqlScripts/truncateTeamsDest.sql',
    task_id='truncate_teams_table',
    dag=dag
)


fetch_teams_data = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='sqlScripts/getTeamsSource.sql',
    task_id='fetch_teams_data',
    dag=dag,
    do_xcom_push=True
)


def _transform_teams(**kwargs):
    ti = kwargs['ti']
    teams_data = ti.xcom_pull('fetch_teams_data')
    columns = ['team_id', 'team_name', 'team_passcode', 'is_private', 'created_at']
    df = pd.DataFrame(teams_data, columns=columns)
    df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'SourceTeams.csv'), index=False)


transform_teams_data = PythonOperator(
    python_callable=_transform_teams,
    task_id='transform_teams',
    dag=dag,
    provide_context=True
)


def _insert_teams(**kwargs):
    report_conn = BaseHook.get_connection(conn_id='supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        database=report_conn.schema,
        user=report_conn.login,
        password=report_conn.password
    )

    cursor = conn.cursor()
    with open(os.path.join(BASE_PATH, 'tempFiles', 'SourceTeams.csv'), 'r') as f:
        cursor.copy_expert("""
            COPY teams FROM STDIN WITH CSV HEADER DELIMITER ',';
            """, f)
    conn.commit()
    cursor.close()
    conn.close()


load_teams_data = PythonOperator(
    python_callable=_insert_teams,
    task_id='load_teams_data',
    dag=dag
)


remove_teams_csv = BashOperator(
    bash_command='rm -f $AIRFLOW_HOME/dags/tempFiles/SourceTeams.csv',
    task_id='remove_teams_csv',
    dag=dag
)


truncate_team_members_report = SQLExecuteQueryOperator(
    conn_id='supabase_report',
    sql='sqlScripts/truncateTeamMembersDest.sql',
    task_id='truncate_team_members_table',
    dag=dag
)


fetch_team_members_data = SQLExecuteQueryOperator(
    conn_id='supabase_prod',
    sql='sqlScripts/getTeamMembersSource.sql',
    task_id='fetch_team_members',
    dag=dag,
    do_xcom_push=True
)


def _transform_team_members(**kwargs):
    ti = kwargs['ti']
    team_members_data = ti.xcom_pull('fetch_team_members')
    columns = ['team_id', 'participant_id', 'is_leader', 'joined_at']
    df = pd.DataFrame(team_members_data, columns=columns)
    df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'SourceTeamMembers.csv'), index=False)


transform_team_members_data = PythonOperator(
    python_callable=_transform_team_members,
    task_id='transform_team_members',
    dag=dag,
    provide_context=True
)


def _insert_team_members(**kwargs):
    report_conn = BaseHook.get_connection(conn_id='supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        database=report_conn.schema,
        user=report_conn.login,
        password=report_conn.password
        )
    
    cursor = conn.cursor()
    with open(os.path.join(BASE_PATH, 'tempFiles', 'SourceTeamMembers.csv'), 'r') as f:
        cursor.copy_expert("""
            COPY team_members FROM STDIN WITH CSV HEADER DELIMITER ',';
    """, file=f)
    conn.commit()
    cursor.close()
    conn.close()


load_team_members_data = PythonOperator(
    python_callable=_insert_team_members,
    task_id='load_team_memebers_data',
    dag=dag
)


remove_team_members_csv = BashOperator(
    bash_command='rm -f $AIRFLOW_HOME/dags/tempFiles/SourceTeamMembers.csv',
    task_id='remove_team_members_csv',
    dag=dag
)


def download_student_success_team(**kwargs):
    url = 'https://docs.google.com/spreadsheets/d/1WCAsZj_nxYFwO01Zzaxko2WBjWXT7ekJ/export?format=csv&gid=1125428113#gid=1125428113'
    response = requests.get(url)
    if response.status_code == 200:
        file = io.BytesIO(response.content)
        df = pd.read_csv(file)
        df.to_csv(os.path.join(BASE_PATH, 'tempFiles', 'studentSuccessTeamSheet.csv'))
    else:
        raise Exception('could not download student success team file!')


download_ss_sheet = PythonOperator(
    python_callable=download_student_success_team,
    task_id='download_student_success_team_gsheet',
    dag=dag
)


def update_student_rows(**kwargs):
    df = pd.read_csv(os.path.join(BASE_PATH, 'tempFiles', 'studentSuccessTeamSheet.csv'))
    report_conn = BaseHook.get_connection(conn_id='supabase_report')
    conn = psycopg2.connect(
        host=report_conn.host,
        port=report_conn.port,
        database=report_conn.schema,
        user=report_conn.login,
        password=report_conn.password
    )

    cursor = conn.cursor()
    cursor.execute("SELECT * FROM ")



end_dag = EmptyOperator(
    task_id='ending_task',
    dag=dag
)



start_dag >> [truncate_school_report, truncate_seneca_programs_report]

truncate_school_report >> fetch_school_data >> transform_school_data >> load_school >> remove_school_csv
truncate_seneca_programs_report >> fetch_seneca_programs >> transform_programs_data >> load_seneca_programs >> remove_seneca_programs_csv

[remove_school_csv, remove_seneca_programs_csv] >> dummy_task

dummy_task >> [truncate_teams_report, truncate_participants_report]

truncate_teams_report >> fetch_teams_data >> transform_teams_data >> load_teams_data >> remove_teams_csv
truncate_participants_report >> fetch_participants_data >> transform_participants_data >> load_participants >> remove_participants_csv

[remove_participants_csv, remove_teams_csv] >> truncate_team_members_report
truncate_team_members_report >> fetch_team_members_data >> transform_team_members_data >> load_team_members_data >> remove_team_members_csv

remove_team_members_csv >> end_dag

