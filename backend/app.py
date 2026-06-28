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

cursor.execute("""
CREATE TABLE IF NOT EXISTS pages (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    magazine_id INTEGER,

    page_number INTEGER,

    title TEXT,

    content TEXT,

    image_url TEXT,

    spotify_link TEXT

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

@app.route("/pages", methods=["POST"])
def add_page():

    data = request.get_json()

    cursor.execute("""
        INSERT INTO pages (
            magazine_id,
            page_number,
            title,
            content,
            image_url,
            spotify_link
        )
        VALUES (?, ?, ?, ?, ?, ?)
    """, (
        data["magazine_id"],
        data["page_number"],
        data["title"],
        data["content"],
        data["image_url"],
        data["spotify_link"]
    ))

    connection.commit()

    return {
        "message": "Page added successfully!"
    }, 201

@app.route("/pages/<int:magazine_id>", methods=["GET"])
def get_pages(magazine_id):

    cursor.execute("""
        SELECT * FROM pages
        WHERE magazine_id = ?
        ORDER BY page_number ASC
    """, (magazine_id,))

    rows = cursor.fetchall()

    pages = []

    for row in rows:

        pages.append({
            "id": row[0],
            "magazine_id": row[1],
            "page_number": row[2],
            "title": row[3],
            "content": row[4],
            "image_url": row[5],
            "spotify_link": row[6]
        })

    return {
        "pages": pages
    }

if __name__ == "__main__":
    app.run(debug=True)