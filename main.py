import os
from flask import Flask, request, jsonify
import google.generativeai as genai

app = Flask(__name__)

# Render के Environment Variable से API Key लेगा
api_key = os.environ.get("GEMINI_API_KEY")

if not api_key:
    print("Warning: GEMINI_API_KEY not found in environment!")
else:
    genai.configure(api_key=api_key)

@app.route("/", methods=["GET"])
def home():
    return jsonify({"status": "Server is running successfully!"})

@app.route("/chat", methods=["POST"])
def chat():
    try:
        if not api_key:
            return jsonify({"error": "GEMINI_API_KEY environment variable is missing on server"}), 500

        data = request.get_json()
        user_message = data.get("message", "") if data else ""

        if not user_message:
            return jsonify({"error": "No message provided"}), 400

        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(user_message)

        return jsonify({"reply": response.text})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
