from http.server import BaseHTTPRequestHandler
import json
import requests
import urllib.parse
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

# --- DYNAMIC ENVIRONMENT VARIABLES ---
# Vercel Dashboard se automatic values fetch hongi
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_2")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID_2")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL # Gmail par khud ko hi notification aane ke liye

class handler(BaseHTTPRequestHandler):
    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        
        # Form data parse karein
        data = urllib.parse.parse_qs(post_data)
        
        name = data.get('name', ['N/A'])[0]
        phone = data.get('phone', ['N/A'])[0]
        
        info_text = (
            f"👤 Name: {name}\n"
            f"📞 Phone: {phone}"
        )

        # 1. TELEGRAM BOT 2 ALERT
        if TELEGRAM_TOKEN and TELEGRAM_CHAT_ID:
            telegram_text = f"🚨 **New Tour Query Received!** 🚨\n\n{info_text}"
            telegram_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            try:
                requests.post(telegram_url, json={"chat_id": TELEGRAM_CHAT_ID, "text": telegram_text, "parse_mode": "Markdown"})
            except Exception as e:
                print(f"Telegram Error: {e}")

        # 2. GMAIL BACKUP
        if SENDER_EMAIL and SENDER_APP_PASSWORD:
            try:
                email_msg = MIMEMultipart()
                email_msg['From'] = SENDER_EMAIL
                email_msg['To'] = RECEIVER_EMAIL
                email_msg['Subject'] = f"New Lead: {name} ({phone})"
                email_msg.attach(MIMEText(info_text, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, email_msg.as_string())
                server.quit()
            except Exception as e:
                print(f"Gmail Error: {e}")

        # FRONTEND RESPONSE
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        response = {"status": "success", "message": "Query received!"}
        self.wfile.write(json.dumps(response).encode('utf-8'))
        return
