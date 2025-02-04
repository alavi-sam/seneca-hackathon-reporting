from flask import Flask
from dotenv import load_dotenv
import psycopg2


load_dotenv()

connection = psycopg2.connect(
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME
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
