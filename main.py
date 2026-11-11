import os
import time
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
            return jsonify({"error": "GEMINI_API_KEY environment variable missing"}), 500

        # केवल वर्तमान एक्टिव और सपोर्टेड मॉडल्स
        models = [
            "gemini-3.8-flash",
            "gemini-3.8-flash-lite"
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

        # 503 लोड से निपटने के लिए रिट्राई + फॉलबैक
        for model in models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={API_KEY}"
            for attempt in range(2):  # हर मॉडल को 2 बार मौका (अस्थायी 503 से बचने के लिए)
                try:
                    response = requests.post(url, json=payload, headers=headers, timeout=15)
                    res_data = response.json()

                    if response.status_code == 200:
                        ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                        return jsonify({"reply": ai_reply, "model": model})

                    last_error = res_data

                    # अगर 503 हाई डिमांड है तो 1.5 सेकंड रुककर दोबारा कोशिश
                    if response.status_code == 503:
                        time.sleep(1.5)
                        continue
                    else:
                        break  # 404 या अन्य एरर होने पर सीधे अगले मॉडल पर जाएं
                except Exception as req_err:
                    last_error = str(req_err)
                    time.sleep(1)

        return jsonify({"error": last_error}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
