import sqlite3

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

def get_db():

    return connection, cursor