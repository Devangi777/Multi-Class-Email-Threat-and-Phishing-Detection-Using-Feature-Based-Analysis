import re
import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.svm import SVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import recall_score
import warnings
warnings.filterwarnings('ignore')

SUSPICIOUS_KEYWORDS = ['password', 'account', 'verify', 'bank', 'login', 'update', 'urgent', 'suspended', 'billing', 'invoice', 'credit']
URGENCY_PHRASES = ['immediate action', 'act now', 'urgent', 'within 24 hours', 'account suspended', 'final notice', 'click here']
INSTITUTIONAL_KEYWORDS = ['university', 'institute', 'registrar', 'academic', 'campus', 'college', 'professor', 'faculty', 'student']
FORMAL_PHRASES = ['dear', 'regards', 'sincerely', 'thank you', 'best wishes', 'yours faithfully', 'yours truly']
TRUSTED_DOMAINS = ['vit.ac.in', 'linkedin.com', 'google.com', 'microsoft.com', 'github.com']
MARKETING_KEYWORDS = ['unsubscribe', 'promo', 'newsletter', 'offer', 'discount', 'subscribe', 'free', 'view in browser', 'opt out']

class EmailThreatDetector:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(max_features=100)
        self.model = None
        self.model_name = ""
        self.train_models()
        
    def extract_features(self, subject, body, url, sender="", link_count=0):
        full_text = str(subject) + " " + str(body)
        text_lower = full_text.lower()
        
        suspicious_count = sum(text_lower.count(kw) for kw in SUSPICIOUS_KEYWORDS)
        urgency_count = sum(1 for u in URGENCY_PHRASES if u in text_lower)
        institutional_count = sum(1 for k in INSTITUTIONAL_KEYWORDS if k in text_lower)
        formal_count = sum(1 for f in FORMAL_PHRASES if f in text_lower)
        marketing_count = sum(text_lower.count(m) for m in MARKETING_KEYWORDS)
        
        sender_str = str(sender).lower()
        domain = ""
        if "@" in sender_str:
            domain = sender_str.split("@")[-1].strip("<>")
        is_trusted_domain = 1 if domain in TRUSTED_DOMAINS else 0
        
        url_str = str(url) if url else ""
        url_length = len(url_str)
        url_dots = url_str.count('.')
        is_ip_url = 1 if re.search(r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}', url_str) else 0
        special_chars = sum(url_str.count(c) for c in ['@', '-', '_', '?', '='])
        
        capital_ratio = sum(1 for c in full_text if c.isupper()) / (len(full_text) + 1)
        exclam_ratio = full_text.count('!') / (len(full_text) + 1)
        email_length = len(full_text)
        link_ratio = url_length / (email_length + 1)
        length_feature = min(email_length / 1000.0, 1.0)
        
        features = {
            'suspicious_count': suspicious_count,
            'urgency_count': urgency_count,
            'institutional_count': institutional_count,
            'formal_count': formal_count,
            'marketing_count': marketing_count,
            'is_trusted_domain': is_trusted_domain,
            'url_length': min(url_length, 100) / 100.0,
            'url_dots': url_dots,
            'is_ip_url': is_ip_url,
            'url_specials': special_chars,
            'capital_ratio': capital_ratio,
            'exclam_ratio': exclam_ratio,
            'length_feature': length_feature,
            'link_ratio': link_ratio,
            'link_count': link_count
        }
        return full_text, features
        
    def prepare_dataset(self):
        data = [
            {"subject": "Team Meeting", "body": "Hi, let's meet at 10 AM to discuss the new features. Please bring the report.", "url": "", "sender": "manager@company.com", "link_count": 0, "label": 0},
            {"subject": "Project update", "body": "The files are attached. Thanks for your contribution to the team.", "url": "http://company.com/files", "sender": "hr@company.com", "link_count": 1, "label": 0},
            {"subject": "Buy cheap watches", "body": "Discount watches here! Buy now! Limited offer! unsubscribe", "url": "http://cheapwatches.com", "sender": "spam@deals.com", "link_count": 5, "label": 1},
            {"subject": "Congrats you won", "body": "You won the lottery. Claim your prize immediately.", "url": "http://prize.com", "sender": "luck@prize.com", "link_count": 2, "label": 1},
            {"subject": "Urgent: Account Suspended", "body": "Immediate action required. Verify your account or it will be suspended.", "url": "http://192.168.1.1/login", "sender": "admin@fakebank.com", "link_count": 1, "label": 2},
            {"subject": "Bank Security Alert", "body": "Your bank account has an unauthorized login. Click here to verify password.", "url": "http://secure-update-login.com-verify.com/auth", "sender": "security@fakebank.com", "link_count": 1, "label": 2},
            {"subject": "Invoice Attached", "body": "Please review the attached invoice for last month's services.", "url": "", "sender": "billing@vendor.com", "link_count": 0, "label": 0},
            {"subject": "Get 50% off", "body": "Exclusive offer, buy now and save big!! promo inside", "url": "http://deals.com", "sender": "promo@deals.com", "link_count": 6, "label": 1},
            {"subject": "Verify Billing", "body": "Update your billing immediately. Final notice or account will be cancelled.", "url": "http://payment.verify-account-info.com/?id=123", "sender": "support@fakebilling.com", "link_count": 1, "label": 2},
            {"subject": "Lunch?", "body": "Are we still on for lunch? Let me know.", "url": "", "sender": "colleague@company.com", "link_count": 0, "label": 0},
            {"subject": "IT Support - Password Expiring", "body": "Your password expires in 2 hours. Click here to update.", "url": "http://10.0.0.5/update", "sender": "it@fakedomain.com", "link_count": 2, "label": 2},
            {"subject": "Newsletter", "body": "Read our latest news and updates regarding the company. view in browser", "url": "http://newsletter.com", "sender": "news@company.com", "link_count": 8, "label": 1},
            {"subject": "Welcome to VIT", "body": "Dear Student, please find attached the academic calendar.", "url": "http://vit.ac.in/academic", "sender": "registrar@vit.ac.in", "link_count": 1, "label": 0},
            {"subject": "LinkedIn Update", "body": "You have 5 new profile views. Sincerely, the team.", "url": "http://linkedin.com/in", "sender": "noreply@linkedin.com", "link_count": 1, "label": 0}
        ]
        df = pd.DataFrame(data)
        X_text = []
        X_num = []
        y = df['label'].values
        
        for _, row in df.iterrows():
            text, feats = self.extract_features(row['subject'], row['body'], row['url'], row.get('sender', ''), row.get('link_count', 0))
            X_text.append(text)
            X_num.append(list(feats.values()))
            
        X_vec = self.vectorizer.fit_transform(X_text).toarray()
        X_final = np.hstack((X_vec, np.array(X_num)))
        return X_final, y

    def train_models(self):
        X, y = self.prepare_dataset()
        models = {
            "Multinomial Naive Bayes": MultinomialNB(),
            "Support Vector Machine": SVC(kernel='linear', probability=True),
            "Random Forest": RandomForestClassifier(n_estimators=50, random_state=42)
        }
        best_score = -1
        best_clf = None
        best_name = ""
        
        for name, clf in models.items():
            clf.fit(X, y)
            preds = clf.predict(X)
            score = recall_score(y, preds, average='macro', zero_division=0)
            if score > best_score:
                best_score = score
                best_clf = clf
                best_name = name
                
        self.model = best_clf
        self.model_name = best_name

    def predict(self, subject, body, url, sender="", link_count=0):
        text, feats = self.extract_features(subject, body, url, sender, int(link_count) if link_count else 0)
        X_vec = self.vectorizer.transform([text]).toarray()
        X_num = np.array([list(feats.values())])
        X_final = np.hstack((X_vec, X_num))
        
        pred_class = self.model.predict(X_final)[0]
        try:
            proba = self.model.predict_proba(X_final)[0]
            ml_confidence = round(max(proba) * 100, 2)
        except:
            ml_confidence = 85.0
            
        final_class = pred_class
        confidence = ml_confidence
        reasons = []

        is_phishing = False
        
        # Rule-based overrides ONLY for explicit Phishing behaviors
        if feats['is_ip_url'] == 1:
            is_phishing = True
            reasons.append("Critical Warning: Direct IP-based URL detected across payload.")
        if feats['url_dots'] > 4:
            is_phishing = True
            reasons.append("High subdomain nesting detected, indicating domain obfuscation.")
        if feats['suspicious_count'] >= 2 and feats['url_length'] > 0.0:
            is_phishing = True
            reasons.append("Suspicious credential/login keywords found alongside embedded links.")

        if is_phishing:
            final_class = 2
            confidence = min(99.0, ml_confidence + 15)
        elif final_class == 1:
            reasons.append("Machine learning heuristics classify this pattern as typical Spam/Promotional content.")
        elif final_class == 2:
            reasons.append("Machine learning logic verifies high probability of a Phishing attempt.")
        else:
            reasons.append("Machine learning natively verifies email structure aligns with safe parameters.")

        class_map = {
            0: {"class": "Legitimate", "risk": "Low", "action": "Deliver", "color": "green", "risk_score": 10},
            1: {"class": "Spam", "risk": "High", "action": "Quarantine", "color": "orange", "risk_score": 75},
            2: {"class": "Phishing", "risk": "Critical", "action": "Block + Alert", "color": "red", "risk_score": 98}
        }
        
        result = class_map[final_class]
        result['reasons'] = reasons
        result['model'] = self.model_name
        result['confidence'] = round(confidence, 2)
        
        highlight_words = []
        highlight_words.extend(SUSPICIOUS_KEYWORDS)
        highlight_words.extend(URGENCY_PHRASES)
        highlight_words.extend(MARKETING_KEYWORDS)
        result['highlight_words'] = highlight_words
        
        return result
