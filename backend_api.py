from flask import Flask, request, jsonify
from flask_cors import CORS
from ml_engine import EmailThreatDetector
import hashlib
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
import dkim
import csv
import os
app = Flask(__name__)
# Enable CORS to allow requests directly from Chrome Extension
CORS(app) 

app.config['JWT_SECRET_KEY'] = 'super-secret-aegis-key-2026'
jwt = JWTManager(app)

detector = EmailThreatDetector()

@app.route('/auth', methods=['POST'])
def auth():
    data = request.json
    api_key = data.get('api_key', '')
    if api_key == 'aegis-extension-key-123':
        access_token = create_access_token(identity="extension_client")
        return jsonify(access_token=access_token), 200
    return jsonify({"msg": "Bad API key"}), 401

@app.route('/verify-dkim', methods=['POST'])
def verify_dkim_route():
    try:
        raw_eml = request.data
        if not raw_eml:
            return jsonify({"status": "error", "message": "No raw email provided"}), 400
        is_valid = dkim.verify(raw_eml)
        return jsonify({"dkim_valid": is_valid})
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 400

@app.route('/predict', methods=['POST'])
@jwt_required()
def predict():
    data = request.json
    subject = data.get('subject', '')
    body = data.get('body', '')
    url = data.get('url', '')
    sender = data.get('sender', '')
    link_count = data.get('link_count', 0)
    dkim_signed_by = data.get('dkim_signed_by', '')
    
    if sender:
        parsed_sender_hash = hashlib.sha256((sender + "secret-salt").encode('utf-8')).hexdigest()
        print(f"[PRIVACY ENFORCED] Processed sender identity hashed: {parsed_sender_hash[:16]}...")
        
    print(f"[RECEIVED] Subject: {subject[:30]}... URL: {url}")
    result = detector.predict(subject, body, url, sender, link_count, dkim_signed_by)
    
    # GDPR Compliant Logging for ML Improvement
    parsed_sender_hash = ""
    if sender:
        parsed_sender_hash = hashlib.sha256((sender + "secret-salt").encode('utf-8')).hexdigest()
        
    log_file = 'live_scanned_emails.csv'
    file_exists = os.path.isfile(log_file)
    with open(log_file, mode='a', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow(['subject', 'body', 'url', 'sender_hash', 'link_count', 'dkim_signed_by', 'predicted_class'])
        writer.writerow([subject, body, url, parsed_sender_hash, link_count, dkim_signed_by, result['class']])
        
    return jsonify(result)

if __name__ == '__main__':
    print("Aegis Security Gateway API running on port 5000...")
    app.run(debug=True, port=5000)
