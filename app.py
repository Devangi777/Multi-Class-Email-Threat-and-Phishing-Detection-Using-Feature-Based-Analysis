from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from ml_engine import EmailThreatDetector

app = Flask(__name__)
CORS(app)
detector = EmailThreatDetector()

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    subject = data.get('subject', '')
    body = data.get('body', '')
    url = data.get('url', '')
    sender = data.get('sender', '')
    link_count = data.get('link_count', 0)
    
    result = detector.predict(subject, body, url, sender, link_count)
    return jsonify(result)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
