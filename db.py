import psycopg2
from dotenv import load_dotenv
import os


load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

URL = os.getenv("DATABASE_URL")

# connection = psycopg2.connect(
#         user=USER,
#         password=PASSWORD,
#         host=HOST,
#         port=PORT,
#         dbname=DBNAME
#     )


connection = psycopg2.connect(URL)


cursor = connection.cursor()
cursor.execute("select * from school;")
print(cursor.fetchone())