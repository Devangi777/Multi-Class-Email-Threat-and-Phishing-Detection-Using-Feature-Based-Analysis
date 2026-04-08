from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_engine import EmailThreatDetector

app = Flask(__name__)
# Enable CORS to allow requests directly from Chrome Extension
CORS(app) 

detector = EmailThreatDetector()

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    subject = data.get('subject', '')
    body = data.get('body', '')
    url = data.get('url', '')
    
    print(f"[RECEIVED] Subject: {subject[:30]}... URL: {url}")
    result = detector.predict(subject, body, url)
    return jsonify(result)

if __name__ == '__main__':
    print("Aegis Security Gateway API running on port 5000...")
    app.run(debug=True, port=5000)
