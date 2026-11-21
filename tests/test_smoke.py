import os
import sys
import tempfile
import pytest

# Ensure backend directory is in python path
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
BACKEND_DIR = os.path.join(BASE_DIR, "backend")
if BACKEND_DIR not in sys.path:
    sys.path.insert(0, BACKEND_DIR)

# Set test environment variables
os.environ["SECRET_KEY"] = "test-smoke-secret-key-12345"
os.environ["APP_ENV"] = "testing"

@pytest.fixture
def app_instance():
    """
    Creates a test application instance pointing to a temporary SQLite database.
    Supports both the legacy app.py and the refactored create_app factory.
    """
    temp_fd, temp_db_path = tempfile.mkstemp(suffix=".db")
    os.close(temp_fd)

    app = None

    # Check if the refactored factory create_app exists
    try:
        from app import create_app
        from config import TestingConfig

        class CustomTestingConfig(TestingConfig):
            TESTING = True
            SQLALCHEMY_DATABASE_URI = f"sqlite:///{temp_db_path}"

        app = create_app(CustomTestingConfig)
        with app.app_context():
            from app.extensions import db
            db.create_all()

    except (ImportError, ModuleNotFoundError):
        # Fall back to legacy backend/app.py
        import app as legacy_app
        legacy_app.DATABASE = temp_db_path
        legacy_app.init_db()
        app = legacy_app.app

    app.config["TESTING"] = True

    yield app

    # Cleanup temporary database
    if os.path.exists(temp_db_path):
        try:
            os.remove(temp_db_path)
        except OSError:
            pass


@pytest.fixture
def client(app_instance):
    return app_instance.test_client()


def test_auth_workflow(client):
    # 1. Register with missing fields
    res = client.post("/register", json={"username": "alice", "email": ""})
    assert res.status_code == 400
    assert res.get_json()["message"] == "Username, email and password are required."

    # 2. Successful registration for User A
    res = client.post("/register", json={
        "username": "Alice",
        "email": "alice@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 201
    assert res.get_json()["message"] == "User registered successfully!"

    # 3. Duplicate email registration
    res = client.post("/register", json={
        "username": "AliceDuplicate",
        "email": "alice@example.com",
        "password": "Password123!"
    })
    assert res.status_code == 409
    assert res.get_json()["message"] == "Email already registered."

    # 4. Register User B
    res = client.post("/register", json={
        "username": "Bob",
        "email": "bob@example.com",
        "password": "BobPassword456!"
    })
    assert res.status_code == 201

    # 5. Check /me before login
    res = client.get("/me")
    assert res.status_code == 200
    assert res.get_json()["logged_in"] is False

    # 6. Login invalid credentials
    res = client.post("/login", json={"email": "alice@example.com", "password": "WrongPassword"})
    assert res.status_code == 401
    assert res.get_json()["message"] == "Invalid email or password."

    # 7. Login successful for Alice
    res = client.post("/login", json={"email": "alice@example.com", "password": "Password123!"})
    assert res.status_code == 200
    data = res.get_json()
    assert data["message"] == "Login successful!"
    assert data["user"]["email"] == "alice@example.com"
    assert data["user"]["username"] == "Alice"

    # 8. Check /me after login
    res = client.get("/me")
    assert res.status_code == 200
    me_data = res.get_json()
    assert me_data["logged_in"] is True
    assert me_data["user"]["email"] == "alice@example.com"

    # 9. Logout
    res = client.post("/logout")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Logged out successfully!"

    # 10. Verify /me after logout
    res = client.get("/me")
    assert res.get_json()["logged_in"] is False


def test_magazines_crud_and_ownership(client):
    # Unauthenticated create / list
    assert client.get("/magazines").status_code == 401
    assert client.post("/magazines", json={"title": "Mag"}).status_code == 401

    # Register & login Alice
    client.post("/register", json={"username": "Alice", "email": "alice@example.com", "password": "pass"})
    client.post("/login", json={"email": "alice@example.com", "password": "pass"})

    # Missing title validation
    res = client.post("/magazines", json={"title": "", "description": "desc"})
    assert res.status_code == 400
    assert res.get_json()["message"] == "Magazine title is required."

    # Create Magazine 1
    res = client.post("/magazines", json={"title": "Alice Trip", "description": "Summer 2026"})
    assert res.status_code == 201
    mag1_id = res.get_json()["id"]

    # Create Magazine 2
    res = client.post("/magazines", json={"title": "Alice Recipes", "description": "Cooking"})
    assert res.status_code == 201
    mag2_id = res.get_json()["id"]

    # List magazines
    res = client.get("/magazines")
    assert res.status_code == 200
    mags = res.get_json()["magazines"]
    assert len(mags) == 2
    assert mags[0]["id"] == mag2_id  # Ordered by id DESC
    assert mags[1]["id"] == mag1_id

    # Register & login Bob
    client.post("/logout")
    client.post("/register", json={"username": "Bob", "email": "bob@example.com", "password": "pass"})
    client.post("/login", json={"email": "bob@example.com", "password": "pass"})

    # Bob's magazine list is empty
    res = client.get("/magazines")
    assert len(res.get_json()["magazines"]) == 0

    # Bob attempts to delete Alice's magazine -> 404
    res = client.delete(f"/magazine/{mag1_id}")
    assert res.status_code == 404
    assert res.get_json()["message"] == "Magazine not found."


def test_pages_crud_move_resequence_and_cascade(client):
    # Register & login Alice
    client.post("/register", json={"username": "Alice", "email": "alice@example.com", "password": "pass"})
    client.post("/login", json={"email": "alice@example.com", "password": "pass"})

    # Create a magazine
    res = client.post("/magazines", json={"title": "Photo Book", "description": "Memories"})
    mag_id = res.get_json()["id"]

    # Page creation validations
    assert client.post("/pages", json={"magazine_id": None}).status_code == 400

    # Register & login Bob to test foreign magazine ownership
    client.post("/logout")
    client.post("/register", json={"username": "Bob", "email": "bob@example.com", "password": "pass"})
    client.post("/login", json={"email": "bob@example.com", "password": "pass"})

    res = client.post("/pages", json={"magazine_id": mag_id, "title": "Bob hacking page"})
    assert res.status_code == 404
    assert res.get_json()["message"] == "Magazine not found."

    # Log Alice back in
    client.post("/logout")
    client.post("/login", json={"email": "alice@example.com", "password": "pass"})

    # Alice creates Page 1 (with spotify song)
    res = client.post("/pages", json={
        "magazine_id": mag_id,
        "title": "Page 1 - Paris",
        "content": "<p>Eiffel Tower</p>",
        "image_url": "https://example.com/eiffel.jpg",
        "spotify_link": "https://open.spotify.com/track/12345"
    })
    assert res.status_code == 201

    # Alice creates Page 2
    res = client.post("/pages", json={
        "magazine_id": mag_id,
        "title": "Page 2 - Rome",
        "content": "<p>Colosseum</p>",
        "image_url": "https://example.com/rome.jpg",
        "spotify_link": ""
    })
    assert res.status_code == 201

    # Alice creates Page 3
    res = client.post("/pages", json={
        "magazine_id": mag_id,
        "title": "Page 3 - Tokyo",
        "content": "<p>Shibuya</p>",
        "image_url": "",
        "spotify_link": ""
    })
    assert res.status_code == 201

    # Verify pages list & sequential page numbers
    res = client.get(f"/pages/{mag_id}")
    assert res.status_code == 200
    pages = res.get_json()["pages"]
    assert len(pages) == 3
    p1_id, p2_id, p3_id = pages[0]["id"], pages[1]["id"], pages[2]["id"]
    assert pages[0]["page_number"] == 1
    assert pages[1]["page_number"] == 2
    assert pages[2]["page_number"] == 3

    # Check stats endpoint
    res = client.get("/stats")
    assert res.status_code == 200
    stats = res.get_json()
    assert stats["magazines"] == 1
    assert stats["pages"] == 3
    assert stats["songs"] == 1

    # Get single page
    res = client.get(f"/page/{p1_id}")
    assert res.status_code == 200
    assert res.get_json()["title"] == "Page 1 - Paris"

    # Bob tries to access Alice's page -> 404
    client.post("/logout")
    client.post("/login", json={"email": "bob@example.com", "password": "pass"})
    assert client.get(f"/page/{p1_id}").status_code == 404
    assert client.put(f"/page/{p1_id}", json={"title": "Hacked"}).status_code == 404
    assert client.delete(f"/page/{p1_id}").status_code == 404
    assert client.put(f"/page/{p1_id}/move", json={"direction": "down"}).status_code == 404

    # Back to Alice
    client.post("/logout")
    client.post("/login", json={"email": "alice@example.com", "password": "pass"})

    # Update page 1
    res = client.put(f"/page/{p1_id}", json={
        "title": "Page 1 - Paris Updated",
        "content": "<p>Updated Content</p>",
        "image_url": "https://example.com/new.jpg",
        "spotify_link": ""
    })
    assert res.status_code == 200
    assert res.get_json()["message"] == "Page updated successfully!"

    # Test Move operations:
    # 1. Invalid direction
    res = client.put(f"/page/{p1_id}/move", json={"direction": "sideways"})
    assert res.status_code == 400

    # 2. Cannot move up when at top
    res = client.put(f"/page/{p1_id}/move", json={"direction": "up"})
    assert res.status_code == 400
    assert res.get_json()["message"] == "Cannot move further."

    # 3. Move Page 1 down
    res = client.put(f"/page/{p1_id}/move", json={"direction": "down"})
    assert res.status_code == 200
    assert res.get_json()["message"] == "Page moved successfully!"

    # Verify new page order: P2 is now #1, P1 is now #2, P3 is #3
    res = client.get(f"/pages/{mag_id}")
    pages = res.get_json()["pages"]
    assert pages[0]["id"] == p2_id
    assert pages[0]["page_number"] == 1
    assert pages[1]["id"] == p1_id
    assert pages[1]["page_number"] == 2
    assert pages[2]["id"] == p3_id
    assert pages[2]["page_number"] == 3

    # Delete middle page (P1) and verify strict contiguous resequencing (1..2)
    res = client.delete(f"/page/{p1_id}")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Page deleted successfully!"

    res = client.get(f"/pages/{mag_id}")
    pages = res.get_json()["pages"]
    assert len(pages) == 2
    assert pages[0]["id"] == p2_id
    assert pages[0]["page_number"] == 1
    assert pages[1]["id"] == p3_id
    assert pages[1]["page_number"] == 2

    # Cascade delete magazine and check that pages are also deleted
    res = client.delete(f"/magazine/{mag_id}")
    assert res.status_code == 200
    assert res.get_json()["message"] == "Magazine deleted successfully!"

    # Pages for deleted magazine return 404
    assert client.get(f"/pages/{mag_id}").status_code == 404
    assert client.get(f"/page/{p2_id}").status_code == 404


def test_views_and_template_rendering(client):
    # Public views
    res = client.get("/")
    assert res.status_code == 200
    assert b"MemoryLane" in res.data
    assert b"Turn memories into beautiful digital magazines" in res.data

    res = client.get("/login")
    assert res.status_code == 200
    assert b"Welcome Back" in res.data
    assert b"loginForm" in res.data

    res = client.get("/register")
    assert res.status_code == 200
    assert b"Create Your MemoryLane Account" in res.data
    assert b"registerForm" in res.data

    # Protected views redirect to login when unauthenticated
    for endpoint in ["/dashboard", "/create-magazine", "/create-page", "/magazine"]:
        res = client.get(endpoint)
        assert res.status_code == 302
        assert "/login" in res.headers["Location"]

    # Authenticate user
    client.post("/register", json={"username": "Alice", "email": "alice@example.com", "password": "pass"})
    client.post("/login", json={"email": "alice@example.com", "password": "pass"})

    # Protected views render successfully when authenticated
    res = client.get("/dashboard")
    assert res.status_code == 200
    assert b"My Magazines" in res.data
    assert b"magazineCount" in res.data

    res = client.get("/create-magazine")
    assert res.status_code == 200
    assert b"Create Magazine" in res.data
    assert b"magazineForm" in res.data

    res = client.get("/create-page")
    assert res.status_code == 200
    assert b"Create Page" in res.data
    assert b"pageForm" in res.data

    res = client.get("/magazine")
    assert res.status_code == 200
    assert b"Magazine Reader" in res.data
    assert b"exportBtn" in res.data

