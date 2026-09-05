import os
import sqlite3
from dotenv import load_dotenv
from flask import Flask, redirect, request, render_template, session, g
from werkzeug.security import generate_password_hash, check_password_hash
from flask_cors import CORS
from sanitizer import sanitize_text, sanitize_html, sanitize_url

# Load environment variables from .env file if present
load_dotenv()

app = Flask(__name__)

# Load SECRET_KEY from environment. Fail startup clearly if missing.
secret_key = os.getenv("SECRET_KEY")
if not secret_key:
    raise RuntimeError(
        "CRITICAL SECURITY ERROR: 'SECRET_KEY' environment variable is missing. "
        "Please configure SECRET_KEY in your environment or .env file."
    )

app.secret_key = secret_key

# Configure session cookie security
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

# Enable SESSION_COOKIE_SECURE strictly in production environment
app_env = os.getenv("APP_ENV", "development").lower()
app.config["SESSION_COOKIE_SECURE"] = (app_env == "production")

CORS(app)

DATABASE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.db")

def get_db():
    if "db" not in g:
        g.db = sqlite3.connect(DATABASE)
        g.db.execute("PRAGMA foreign_keys = ON;")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop("db", None)
    if db is not None:
        db.close()

def init_db():
    db = sqlite3.connect(DATABASE)
    db.execute("PRAGMA foreign_keys = ON;")
    cursor = db.cursor()

    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    """)

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

    db.commit()
    db.close()

init_db()

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

    clean_username = sanitize_text(username)
    clean_email = sanitize_text(email)

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id
        FROM users
        WHERE email = ?
        """,
        (clean_email,)
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
            clean_username,
            clean_email,
            password_hash
        )
    )

    db.commit()

    return {
        "message": "User registered successfully!"
    }, 201

@app.route("/register", methods=["GET"])
def register_page():
    return render_template("register.html")

@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()

    email = data.get("email")
    password = data.get("password")

    if not email or not password:
        return {
            "message": "Email and password are required."
        }, 400

    clean_email = sanitize_text(email)

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT id, username, email, password_hash
        FROM users
        WHERE email = ?
        """,
        (clean_email,)
    )

    user = cursor.fetchone()

    if user is None:
        return {
            "message": "Invalid email or password."
        }, 401

    user_id = user[0]
    username = user[1]
    user_email = user[2]
    stored_password_hash = user[3]

    if not check_password_hash(
        stored_password_hash,
        password
    ):
        return {
            "message": "Invalid email or password."
        }, 401

    session["user_id"] = user_id
    session["username"] = username

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
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("dashboard.html")

@app.route("/create-magazine")
def create_magazine_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("create-magazine.html")

@app.route("/create-page")
def create_page():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("create-page.html")

@app.route("/magazine")
def magazine():
    user_id = session.get("user_id")
    if not user_id:
        return redirect("/login")
    return render_template("magazine.html")

@app.route("/magazines", methods=["GET"])
def get_magazines():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "Login required."
        }, 401

    db = get_db()
    cursor = db.cursor()

    cursor.execute(
        """
        SELECT
            id,
            title,
            description
        FROM magazines
        WHERE user_id = ?
        ORDER BY id DESC
        """,
        (user_id,)
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
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "Login required."
        }, 401

    data = request.get_json()
    title = data.get("title")
    description = data.get("description")

    if not title:
        return {
            "message": "Magazine title is required."
        }, 400

    clean_title = sanitize_text(title)
    clean_description = sanitize_text(description or "")

    db = get_db()
    cursor = db.cursor()

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
            clean_title,
            clean_description
        )
    )

    db.commit()

    return {
        "message": "Magazine created successfully!",
        "id": cursor.lastrowid
    }, 201

@app.route("/magazine/<int:magazine_id>", methods=["DELETE"])
def delete_magazine(magazine_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    db = get_db()
    cursor = db.cursor()

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

    cursor.execute("""
        DELETE FROM pages
        WHERE magazine_id = ?
    """, (magazine_id,))

    cursor.execute("""
        DELETE FROM magazines
        WHERE id = ?
    """, (magazine_id,))

    db.commit()

    return {
        "message": "Magazine deleted successfully!"
    }, 200

@app.route("/pages", methods=["POST"])
def add_page():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    data = request.get_json()
    magazine_id = data.get("magazine_id")
    if not magazine_id:
        return {
            "message": "Magazine ID is required."
        }, 400

    db = get_db()
    cursor = db.cursor()

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

    cursor.execute("""
        SELECT COUNT(*)
        FROM pages
        WHERE magazine_id = ?
    """, (magazine_id,))

    next_page_number = cursor.fetchone()[0] + 1

    clean_title = sanitize_text(data.get("title", ""))
    clean_content = sanitize_html(data.get("content", ""))
    clean_image_url = sanitize_url(data.get("image_url", ""))
    clean_spotify_link = sanitize_url(data.get("spotify_link", ""))

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
        clean_title,
        clean_content,
        clean_image_url,
        clean_spotify_link
    ))

    db.commit()

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

    db = get_db()
    cursor = db.cursor()

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

@app.route("/page/<int:page_id>", methods=["GET"])
def get_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT magazine_id
        FROM pages
        WHERE id = ?
    """, (page_id,))

    page_ref = cursor.fetchone()
    if page_ref is None:
        return {
            "message": "Page not found."
        }, 404

    magazine_id = page_ref[0]

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

    cursor.execute("""
        SELECT id, magazine_id, page_number, title, content, image_url, spotify_link
        FROM pages
        WHERE id = ?
    """, (page_id,))

    row = cursor.fetchone()
    if row is None:
        return {
            "message": "Page not found."
        }, 404

    return {
        "id": row[0],
        "magazine_id": row[1],
        "page_number": row[2],
        "title": row[3],
        "content": row[4],
        "image_url": row[5],
        "spotify_link": row[6]
    }, 200

@app.route("/page/<int:page_id>", methods=["PUT"])
def update_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    db = get_db()
    cursor = db.cursor()

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

    data = request.get_json()
    clean_title = sanitize_text(data.get("title", ""))
    clean_content = sanitize_html(data.get("content", ""))
    clean_image_url = sanitize_url(data.get("image_url", ""))
    clean_spotify_link = sanitize_url(data.get("spotify_link", ""))

    cursor.execute("""
        UPDATE pages
        SET
            title = ?,
            content = ?,
            image_url = ?,
            spotify_link = ?
        WHERE id = ?
    """, (
        clean_title,
        clean_content,
        clean_image_url,
        clean_spotify_link,
        page_id
    ))

    db.commit()

    return {
        "message": "Page updated successfully!"
    }, 200

@app.route("/page/<int:page_id>", methods=["DELETE"])
def delete_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    db = get_db()
    cursor = db.cursor()

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

    cursor.execute("""
        DELETE FROM pages
        WHERE id = ?
    """, (page_id,))

    db.commit()

    return {
        "message": "Page deleted successfully!"
    }, 200

@app.route("/page/<int:page_id>/move", methods=["PUT"])
def move_page(page_id):
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    data = request.json
    direction = data.get("direction")

    if direction not in ["up", "down"]:
        return {
            "message": "Invalid direction."
        }, 400

    db = get_db()
    cursor = db.cursor()

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
        }, 400

    neighbor_id = neighbor[0]
    neighbor_number = neighbor[1]

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

    db.commit()

    return {
        "message": "Page moved successfully!"
    }, 200

@app.route("/stats", methods=["GET"])
def get_stats():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "message": "You must be logged in."
        }, 401

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT COUNT(*)
        FROM magazines
        WHERE user_id = ?
    """, (user_id,))
    magazine_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pages
        JOIN magazines ON pages.magazine_id = magazines.id
        WHERE magazines.user_id = ?
    """, (user_id,))
    page_count = cursor.fetchone()[0]

    cursor.execute("""
        SELECT COUNT(*)
        FROM pages
        JOIN magazines ON pages.magazine_id = magazines.id
        WHERE magazines.user_id = ?
        AND pages.spotify_link IS NOT NULL
        AND pages.spotify_link != ''
    """, (user_id,))
    song_count = cursor.fetchone()[0]

    return {
        "magazines": magazine_count,
        "pages": page_count,
        "songs": song_count
    }, 200

@app.route("/me", methods=["GET"])
def get_current_user():
    user_id = session.get("user_id")
    if not user_id:
        return {
            "logged_in": False
        }

    db = get_db()
    cursor = db.cursor()

    cursor.execute("""
        SELECT id, username, email
        FROM users
        WHERE id = ?
    """, (user_id,))

    user = cursor.fetchone()

    if user is None:
        session.clear()
        return {
            "logged_in": False
        }

    return {
        "logged_in": True,
        "user": {
            "id": user[0],
            "username": user[1],
            "email": user[2]
        }
    }

if __name__ == "__main__":
    app.run(debug=True)