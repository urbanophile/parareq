import flask
from flask import request, jsonify
import json

app = flask.Flask(__name__)


@app.route("/api", methods=["POST"])
def api():
    data = request.get_json()
    print(data)
    return jsonify(data)
