import os
import json
import psycopg2
import requests
from flask import Flask, request, jsonify

app = Flask(__name__)

DB_HOST = os.getenv("DB_HOST", "db")
DB_USER = os.getenv("DB_USER", "admin")
DB_PASS = os.getenv("DB_PASS", "securepassword")
DB_NAME = os.getenv("DB_NAME", "feedback_db")
LLM_API_KEY = os.getenv("LLM_API_KEY")

def analyze_text_with_llm(text):
    url = "https://api.openai.com/v1/chat/completions"
    headers = {"Authorization": f"Bearer {LLM_API_KEY}", "Content-Type": "application/json"}
    payload = {
        "model": "gpt-4o-mini",
        "messages": [
            {"role": "system", "content": "Analyze text. Output ONLY JSON: {'product_category': str, 'sentiment': str, 'extracted_issue': str}"},
            {"role": "user", "content": text}
        ],
        "response_format": { "type": "json_object" }
    }
    response = requests.post(url, headers=headers, json=payload)
    return json.loads(response.json()["choices"][0]["message"]["content"])

@app.route('/webhook/feedback', methods=['POST'])
def process_feedback():
    data = request.json
    raw_text = data.get("text")
    ai_data = analyze_text_with_llm(raw_text)
    # Здесь логика записи в SQL
    return jsonify({"status": "success", "parsed_data": ai_data})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
