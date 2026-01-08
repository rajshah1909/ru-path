# src/app.py
import os

from flask import Flask, request, jsonify
from flask_cors import CORS

from .data_loader import DataLoader
from .chatbot import ParkingChatbot

app = Flask(__name__)
CORS(app)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

buildings_path = os.path.join(BASE_DIR, "Buildings.json")
bus_routes_path = os.path.join(BASE_DIR, "rutgers_bus_routes.json")
parking_path = os.path.join(BASE_DIR, "rupath_parking_base.json")

data_loader = DataLoader(
    buildings_path=buildings_path,
    bus_routes_path=bus_routes_path,
    parking_path=parking_path,
)

chatbot = ParkingChatbot(data_loader)


@app.route("/api/chat", methods=["POST"])
def api_chat():
    data = request.get_json(force=True) or {}
    message = data.get("message", "")
    session_id = data.get("session_id")
    reply = chatbot.chat(message, session_id=session_id)

    return jsonify({
        "reply": reply,
        "response": reply,
        "session_id": session_id
    })


@app.route("/api/test", methods=["GET"])
def api_test():
    return jsonify({"status": "ok"})


@app.route("/api/reset", methods=["POST"])
def api_reset():
    chatbot.logic.reset()
    chatbot.sessions.clear()
    return jsonify({"status": "reset"})


if __name__ == "__main__":
    # Run as:  python -m src.app   from the project root
    app.run(host="0.0.0.0", port=5000, debug=True)
