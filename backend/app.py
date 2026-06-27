from flask import Flask
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

@app.route("/")
def home():
    return {
        "message": "MemoryLane API Running 🚀"
    }

@app.route("/magazines")
def magazines():
    return {
        "magazines": []
    }

@app.route("/pages")
def pages():
    return {
        "pages": []
    }

if __name__ == "__main__":
    app.run(debug=True)