import os
import time
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

API_KEY = os.environ.get("GEMINI_API_KEY")

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "running", "message": "AI Backend Server is Online!"})

# यह रूट Google से आपकी API Key के एक्टिव मॉडल्स की सही लिस्ट लाकर देगा
@app.route("/models", methods=["GET"])
def list_models():
    if not API_KEY:
        return jsonify({"error": "GEMINI_API_KEY missing"}), 500
    try:
        url = f"https://generativelanguage.googleapis.com/v1beta/models?key={API_KEY}"
        resp = requests.get(url, timeout=10)
        return jsonify(resp.json()), resp.status_code
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json() or {}
        user_message = data.get("message", "")

        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        if not API_KEY:
            return jsonify({"error": "GEMINI_API_KEY environment variable missing"}), 500

        # प्राथमिक मॉडल gemini-3.8-flash (जो Google ने खुद एरर में दिया था)
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-3.8-flash:generateContent?key={API_KEY}"
        payload = {"contents": [{"parts": [{"text": user_message}]}]}
        headers = {"Content-Type": "application/json"}

        # 503 ओवरलोड से बचने के लिए 3 बार तुरंत ऑटो-रिट्राई
        last_res = None
        for attempt in range(3):
            response = requests.post(url, json=payload, headers=headers, timeout=20)
            res_data = response.json()

            if response.status_code == 200:
                ai_reply = res_data["candidates"][0]["content"]["parts"][0]["text"]
                return jsonify({"reply": ai_reply, "model": "gemini-3.8-flash"})

            last_res = res_data
            if response.status_code == 503:
                time.sleep(2)  # 2 सेकंड रुककर फिर से कोशिश
                continue
            else:
                break

        return jsonify({"error": last_res}), 503

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
