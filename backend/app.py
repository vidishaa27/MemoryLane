from flask import Flask, request
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
CORS(app)

connection = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS magazines (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    title TEXT NOT NULL,

    description TEXT

)
""")

connection.commit()

@app.route("/")
def home():
    return {
        "message": "MemoryLane API Running 🚀"
    }

@app.route("/magazines", methods=["GET"])
def get_magazines():

    cursor.execute(
        "SELECT * FROM magazines"
    )

    rows = cursor.fetchall()

    magazines = []

    for row in rows:

        magazines.append({

            "id": row[0],

            "title": row[1],

            "description": row[2]

        })

    return {
        "magazines": magazines
    }

@app.route("/magazines", methods=["POST"])
def create_magazine():

    data = request.get_json()

    cursor.execute(
        """
        INSERT INTO magazines
        (title, description)

        VALUES (?, ?)
        """,
        (
            data["title"],
            data["description"]
        )
    )

    connection.commit()

    return {
        "message": "Magazine created successfully!",
        "magazine": data
    }, 201

@app.route("/pages")
def pages():
    return {
        "pages": []
    }

if __name__ == "__main__":
    app.run(debug=True)