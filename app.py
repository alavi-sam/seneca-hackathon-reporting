from flask import Flask
from dotenv import load_dotenv
import psycopg2
import os


load_dotenv()

URL = os.getenv("DATABASE_URL")
connection = psycopg2.connect(URL)

app = Flask(__name__)

cursor = connection.cursor()

@app.route("/")
def home():
    cursor.execute("select * from school;")
    result = cursor.fetchone()
    return "Welcome to Flask on Heroku {}!".format(result)

if __name__ == "__main__":
    app.run(debug=True)
