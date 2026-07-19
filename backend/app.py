from flask import Flask, request, render_template, session
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
import sqlite3

app = Flask(__name__)
app.secret_key = "memorylane-dev-secret"
CORS(app)

connection = sqlite3.connect(
    "database.db",
    check_same_thread=False
)

cursor = connection.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    username TEXT NOT NULL,

    email TEXT UNIQUE NOT NULL,

    password_hash TEXT NOT NULL,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP

)
""")

connection.commit()

cursor.execute("""
CREATE TABLE IF NOT EXISTS magazines (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    user_id INTEGER NOT NULL,

    title TEXT NOT NULL,

    description TEXT,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    FOREIGN KEY (user_id)
        REFERENCES users(id)

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

@app.route("/register", methods=["POST"])
def register():

    data = request.get_json()

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return {
            "message": "Username, email and password are required."
        }, 400

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    existing_user = cursor.fetchone()

    if existing_user:
        return {
            "message": "Email already registered."
        }, 409

    password_hash = generate_password_hash(password)

    cursor.execute(
        """
        INSERT INTO users
        (
            username,
            email,
            password_hash
        )
        VALUES (?, ?, ?)
        """,
        (
            username,
            email,
            password_hash
        )
    )

    connection.commit()

    return {
        "message": "User registered successfully!"
    }, 201

@app.route("/register", methods=["GET"])
def register_page():

    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():

    # Step 1: Get data sent by the frontend
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    # Step 2: Check if fields are missing
    if not email or not password:

        return {
            "message": "Email and password are required."
        }, 400

    # Step 3: Find the user by email
    cursor.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE email = ?
        """,
        (email,)
    )

    user = cursor.fetchone()

    # Step 4: If no user exists
    if user is None:

        return {
            "message": "Invalid email or password."
        }, 401

    # Step 5: Get user information from database
    user_id = user[0]

    username = user[1]

    user_email = user[2]

    stored_password_hash = user[3]

    # Step 6: Check if password is correct
    if not check_password_hash(
        stored_password_hash,
        password
    ):

        return {
            "message": "Invalid email or password."
        }, 401

    # Step 7: Create login session
    session["user_id"] = user_id

    session["username"] = username

    # Step 8: Return successful response
    return {
        "message": "Login successful!",
        "user": {
            "id": user_id,
            "username": username,
            "email": user_email
        }
    }, 200

@app.route("/login", methods=["GET"])
def login_page():

    return render_template("login.html")

@app.route("/logout", methods=["POST"])
def logout():

    session.clear()

    return {
        "message": "Logged out successfully!"
    }, 200

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/dashboard")
def dashboard():
    return render_template("dashboard.html")


@app.route("/create-magazine")
def create_magazine_page():
    return render_template("create-magazine.html")


@app.route("/create-page")
def create_page():
    return render_template("create-page.html")


@app.route("/magazine")
def magazine():
    return render_template("magazine.html")


@app.route("/magazines", methods=["GET"])
def get_magazines():

    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    cursor.execute(
        """
        SELECT id, title, description, created_at
        FROM magazines
        WHERE user_id = ?
        """,
        (user_id,)
    )

    rows = cursor.fetchall()

    magazines = []

    for row in rows:

        magazines.append({

            "id": row[0],

            "title": row[1],

            "description": row[2],

            "created_at": row[3]

        })

    return {
        "magazines": magazines
    }

@app.route("/magazines", methods=["POST"])
def create_magazine():

    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    data = request.get_json()

    title = data.get("title")
    description = data.get("description", "")

    if not title:
        return {
            "message": "Magazine title is required."
        }, 400

    cursor.execute(
        """
        INSERT INTO magazines
        (
            user_id,
            title,
            description
        )
        VALUES (?, ?, ?)
        """,
        (
            user_id,
            title,
            description
        )
    )

    connection.commit()

    magazine_id = cursor.lastrowid

    return {
        "message": "Magazine created successfully!",
        "magazine": {
            "id": magazine_id,
            "user_id": user_id,
            "title": title,
            "description": description
        }
    }, 201

@app.route("/magazine/<int:magazine_id>", methods=["DELETE"])
def delete_magazine(magazine_id):

    # 1. Check if user is logged in
    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # 2. Check if the magazine belongs to the logged-in user
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Magazine not found."
        }, 404

    # 3. Delete all pages belonging to the magazine
    cursor.execute("""
        DELETE FROM pages
        WHERE magazine_id = ?
    """, (magazine_id,))

    # 4. Delete the magazine
    cursor.execute("""
        DELETE FROM magazines
        WHERE id = ?
    """, (magazine_id,))

    connection.commit()

    return {
        "message": "Magazine deleted successfully!"
    }, 200

@app.route("/pages", methods=["POST"])
def add_page():

    # 1. Get logged-in user
    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # 2. Get request data
    data = request.get_json()

    magazine_id = data.get("magazine_id")

    if not magazine_id:
        return {
            "message": "Magazine ID is required."
        }, 400

    # 3. Check magazine ownership
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Magazine not found."
        }, 404

    # 4. Find next page number
    cursor.execute("""
        SELECT COUNT(*)
        FROM pages
        WHERE magazine_id = ?
    """, (magazine_id,))

    next_page_number = cursor.fetchone()[0] + 1

    # 5. Insert page
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
        magazine_id,
        next_page_number,
        data.get("title", ""),
        data.get("content", ""),
        data.get("image_url", ""),
        data.get("spotify_link", "")
    ))

    connection.commit()

    return {
        "message": "Page added successfully!"
    }, 201

@app.route("/pages/<int:magazine_id>", methods=["GET"])
def get_pages(magazine_id):

    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # Check if the magazine belongs to the logged-in user
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Magazine not found."
        }, 404

    # Now fetch the pages
    cursor.execute("""
        SELECT *
        FROM pages
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

    # 1. Get logged-in user
    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # 2. Find the page and its magazine
    cursor.execute("""
        SELECT magazine_id
        FROM pages
        WHERE id = ?
    """, (page_id,))

    page = cursor.fetchone()

    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine_id = page[0]

    # 3. Check magazine ownership
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    # 4. Get updated data
    data = request.get_json()

    title = data.get("title", "")
    content = data.get("content", "")
    image_url = data.get("image_url", "")
    spotify_link = data.get("spotify_link", "")

    # 5. Update page
    cursor.execute("""
        UPDATE pages

        SET
            title = ?,
            content = ?,
            image_url = ?,
            spotify_link = ?

        WHERE id = ?
    """, (
        title,
        content,
        image_url,
        spotify_link,
        page_id
    ))

    connection.commit()

    return {
        "message": "Page updated successfully!"
    }, 200

@app.route("/page/<int:page_id>", methods=["DELETE"])
def delete_page(page_id):

    # 1. Get logged-in user
    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # 2. Find the page
    cursor.execute("""
        SELECT magazine_id
        FROM pages
        WHERE id = ?
    """, (page_id,))

    page = cursor.fetchone()

    if page is None:
        return {
            "message": "Page not found."
        }, 404

    magazine_id = page[0]

    # 3. Check magazine ownership
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    # 4. Delete the page
    cursor.execute("""
        DELETE FROM pages
        WHERE id = ?
    """, (page_id,))

    connection.commit()

    return {
        "message": "Page deleted successfully!"
    }, 200

@app.route("/page/<int:page_id>/move", methods=["PUT"])
def move_page(page_id):

    # 1. Check if user is logged in
    user_id = session.get("user_id")

    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    # 2. Get direction
    data = request.json

    direction = data.get("direction")

    if direction not in ["up", "down"]:
        return {
            "message": "Invalid direction."
        }, 400

    # 3. Find the current page
    cursor.execute("""
        SELECT id, magazine_id, page_number
        FROM pages
        WHERE id = ?
    """, (page_id,))

    current = cursor.fetchone()

    if current is None:
        return {
            "message": "Page not found."
        }, 404

    current_id = current[0]
    magazine_id = current[1]
    current_number = current[2]

    # 4. Check if the logged-in user owns this magazine
    cursor.execute("""
        SELECT id
        FROM magazines
        WHERE id = ?
        AND user_id = ?
    """, (magazine_id, user_id))

    magazine = cursor.fetchone()

    if magazine is None:
        return {
            "message": "Page not found."
        }, 404

    # 5. Find neighboring page
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

    # 6. No neighboring page
    if neighbor is None:

        return {
            "message": "Cannot move further."
        }, 400

    neighbor_id = neighbor[0]
    neighbor_number = neighbor[1]

    # 7. Swap page numbers
    cursor.execute(
        """
        UPDATE pages
        SET page_number = ?
        WHERE id = ?
        """,
        (neighbor_number, current_id)
    )

    cursor.execute(
        """
        UPDATE pages
        SET page_number = ?
        WHERE id = ?
        """,
        (current_number, neighbor_id)
    )

    connection.commit()

    return {
        "message": "Page moved successfully!"
    }, 200

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

if __name__ == "__main__":
    app.run(debug=True)