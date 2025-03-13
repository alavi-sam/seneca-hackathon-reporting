from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
import os
from dotenv import load_dotenv
import requests
from io import BytesIO
import pandas as pd
import psycopg2


conn = psycopg2.connect(
    host='aws-0-us-west-1.pooler.supabase.com',
    port='6543',
    database='postgres',
    user='postgres.autrxhhiehfmziavcryj',
    password='sSaGxHLwJtoiEcYY'
)



DAGS_FOLDER = os.path.join(os.getenv("AIRFLOW_HOME"), "dags")


# SCOPES = ['https://www.googleapis.com/auth/drive']

# sa = service_account.Credentials.from_service_account_file(os.path.join(DAGS_FOLDER, 'sheetsAPI.json'), scopes=SCOPES)

def download_file(file_id, destination):
    pass    


# download_file('1PZMEIFuMlWwcozguuXRnEtDLHJiLAhl-FqwxkMDAfN0', 'test.csv')

response = requests.get('https://docs.google.com/spreadsheets/d/1WCAsZj_nxYFwO01Zzaxko2WBjWXT7ekJ/export?format=csv&gid=1125428113#gid=1125428113')
file = BytesIO(response.content)
df = pd.read_csv(file)

sheet_dict = {row['Email']: row.to_dict() for _, row in df.iterrows()}

cursor = conn.cursor()
cursor.execute('SELECT * FROM participants;')
db_cols = [col[0] for col in cursor.description]
db_rows = cursor.fetchall()
db_dict = {row['email']: row for row in (
    dict(zip(db_cols, row)) for row in db_rows
)}



for email in sheet_dict.keys():  
    cursor.execute(f"SELECT * FROM participants where email='{email}';")
    db_data = cursor.fetchone()
    break

print()