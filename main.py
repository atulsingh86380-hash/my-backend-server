import os
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "AI Backend Server is Online!"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if not API_KEY:
            return jsonify({"error": "GEMINI_API_KEY missing"}), 500

        # सबसे भरोसेमंद मॉडल्स की लिस्ट (Gemma + Gemini)
        models = [
            "gemma-4-26b-a4b-it",
            "gemini-2.5-pro",
            "gemini-3.5-flash",
            "gemini-flash-latest"
        ]

        payload = {
            "contents": [
                {
                    "parts": [{"text": user_message}]
                }
            ]
        }
        headers = {"Content-Type": "application/json"}

        last_error = None
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
            try:
                response = requests.post(url, json=payload, headers=headers, timeout=15)
                res_data = response.json()

                if response.status_code == 200:
                    ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                    return jsonify({
                        "status": "success",
                        "model_used": model,
                        "reply": ai_reply
                    })
                
                last_error = res_data
            except Exception as req_err:
                last_error = str(req_err)
                continue

        return jsonify({"error": last_error}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
