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

    magazine_id INTEGER NOT NULL,

    page_number INTEGER,

    title TEXT,

    content TEXT,

    image_url TEXT,

    spotify_link TEXT,

    FOREIGN KEY (magazine_id)
        REFERENCES magazines(id)

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
@app.route("/page/<int:page_id>", methods=["PUT"])
def update_page(page_id):

    data = request.json

    cursor.execute("""
        UPDATE pages

        SET
            title=?,
            content=?,
            image_url=?,
            spotify_link=?

        WHERE id=?
    """, (

        data["title"],
        data["content"],
        data["image_url"],
        data["spotify_link"],
        page_id

    ))

    connection.commit()

    return {
        "message": "Page updated successfully!"
    }


@app.route("/page/<int:page_id>", methods=["DELETE"])
def delete_page(page_id):

    cursor.execute("""
        DELETE FROM pages
        WHERE id = ?
    """, (page_id,))

    connection.commit()

    return {
        "message": "Page deleted successfully!"
    }

@app.route("/stats", methods=["GET"])
def get_stats():

    cursor.execute(
        "SELECT COUNT(*) FROM magazines"
    )

    magazine_count = cursor.fetchone()[0]

    cursor.execute(
        "SELECT COUNT(*) FROM pages"
    )

    page_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pages
        WHERE spotify_link IS NOT NULL
        AND spotify_link != ''
    """)

    song_count = cursor.fetchone()[0]

    return {
        "magazines": magazine_count,
        "pages": page_count,
        "songs": song_count
    }

@app.route("/page/<int:page_id>", methods=["GET"])
def get_page(page_id):

    cursor.execute("""
        SELECT * FROM pages
        WHERE id = ?
    """, (page_id,))

    row = cursor.fetchone()

    if row is None:
        return {"message": "Page not found"}, 404

    return {
        "id": row[0],
        "magazine_id": row[1],
        "page_number": row[2],
        "title": row[3],
        "content": row[4],
        "image_url": row[5],
        "spotify_link": row[6]
    }

@app.route("/page/<int:page_id>/move", methods=["PUT"])
def move_page(page_id):

    data = request.json

    direction = data["direction"]

    cursor.execute("""
    SELECT id, magazine_id, page_number
    FROM pages
    WHERE id = ?
""", (page_id,))

    current = cursor.fetchone()

    if current is None:
        return {"message": "Page not found"}, 404

    current_id = current[0]
    magazine_id = current[1]
    current_number = current[2]

    if direction == "up":

        cursor.execute("""
            SELECT id, page_number
            FROM pages
            WHERE magazine_id = ?
            AND page_number < ?
            ORDER BY page_number DESC
            LIMIT 1
        """, (magazine_id, current_number))

    else:

        cursor.execute("""
            SELECT id, page_number
            FROM pages
            WHERE magazine_id = ?
            AND page_number > ?
            ORDER BY page_number ASC
            LIMIT 1
        """, (magazine_id, current_number))
        neighbor = cursor.fetchone()

    if neighbor is None:

        return {
            "message": "Cannot move further."
        }
    neighbor_id = neighbor[0]
    neighbor_number = neighbor[1]

    cursor.execute(
        "UPDATE pages SET page_number=? WHERE id=?",
        (neighbor_number, current_id)
    )

    cursor.execute(
        "UPDATE pages SET page_number=? WHERE id=?",
        (current_number, neighbor_id)
    )

    connection.commit()

    return {
        "message": "Page moved successfully!"
    }

if __name__ == "__main__":
    app.run(debug=True)