import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Render के Environment Variable से API Key लेना
api_key = os.environ.get("GEMINI_API_KEY")

if api_key:
    genai.configure(api_key=api_key)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Server is running successfully!"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        data = request.get_json()
        user_message = data.get("message", "")
        
        if not user_message:
            return jsonify({"error": "Message is required"}), 400

        # सही और स्टेबल मॉडल नाम
        model = genai.GenerativeModel("gemini-1.5-flash-latest")
        response = model.generate_content(user_message)

        return jsonify({"reply": response.text})

    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
