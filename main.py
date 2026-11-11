import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Server is running successfully!"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if not API_KEY:
            return jsonify({"error": "GEMINI_API_KEY environment variable missing"}), 500

        # Google Gemini का सीधा REST API एंडपॉइंट
url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ]
        }

        headers = {"Content-Type": "application/json"}
        response = requests.post(url, json=payload, headers=headers)
        res_data = response.json()

        if response.status_code != 200:
            return jsonify({"error": res_data}), response.status_code

        bot_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
        return jsonify({"reply": bot_reply})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
