from flask import Flask, request
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

magazines = []

@app.route("/")
def home():
    return {
        "message": "MemoryLane API Running 🚀"
    }

@app.route("/magazines", methods=["GET"])
def get_magazines():

    return {
        "magazines": magazines
    }

@app.route("/magazines", methods=["POST"])
def create_magazine():

    data = request.get_json()

    magazines.append(data)

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