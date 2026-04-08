# CipherMail Guard System Setup

## Overview
You now have a fully functional 2-part system:
1. **Flask REST API & Web Dashboard (Backend)**
2. **Chrome Extension (Frontend integration)**

## Step 1: Run the Backend Engine
The extension relies on your local Python server to do the Heavy ML lifting.
Open a terminal in your project directory:
```bash
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
pip install flask-cors
python app.py
```
*(Keep this terminal running. It will listen on http://127.0.0.1:5000)*

## Step 2: Install the Chrome Extension
1. Open Google Chrome.
2. Type `chrome://extensions/` in the URL bar and hit enter.
3. Turn on **Developer mode** (toggle switch usually in the top right corner).
4. Click **"Load unpacked"** in the top left.
5. Select the newly created `extension` folder inside your project directory (`c:\Users\Devangi\OneDrive\Desktop\multi class email threat detection\extension`).

## Step 3: Test the System!
1. Open Gmail (`mail.google.com`).
2. Click on any email to open it.
3. Automatically, the **🛡️ CipherMail Guard** side-panel will slide into the top-right of your screen inside Gmail!
4. It will show exactly how the system scores the email in real-time.
