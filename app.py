from flask import Flask
from dotenv import load_dotenv
import psycopg2
import os


load_dotenv()

USER = os.getenv("DB_USER")
PASSWORD = os.getenv("DB_PASSWORD")
HOST = os.getenv("DB_HOST")
PORT = os.getenv("DB_PORT")
DBNAME = os.getenv("DB_NAME")

connection = psycopg2.connect(
        user=USER,
        password=PASSWORD,
        host=HOST,
        port=PORT,
        dbname=DBNAME
    )

app = Flask(__name__)

cursor = connection.cursor()

@app.route("/")
def home():
    cursor.execute("select * from schools;")
    result = cursor.fetchone()
    return "Welcome to Flask on Heroku {}!".format(result)

if __name__ == "__main__":
    app.run(debug=True)
