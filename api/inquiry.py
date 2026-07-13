from flask import Flask, request, jsonify, render_template
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# --- CONFIGURATION FROM VERCEL VARIABLES ---
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN_2")
TELEGRAM_CHAT_ID = os.environ.get("CHAT_ID_2")
SENDER_EMAIL = os.environ.get("SENDER_EMAIL")
SENDER_APP_PASSWORD = os.environ.get("SENDER_APP_PASSWORD")
RECEIVER_EMAIL = SENDER_EMAIL

# ... tumhare purane routes (jaise @app.route('/') wagera) yahan rehnge ...

@app.route('/api/inquiry', methods=['POST'])
def handle_inquiry():
    # Flask me form data status nikalne ke liye request.form use hota hai
    name = request.form.get('name', 'N/A')
    phone = request.form.get('phone', 'N/A')
    
    info_text = (
        f"👤 Name: {name}\n"
        f"📞 Phone: {phone}"
    )

    # 1. TELEGRAM NOTIFICATION
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

    # Frontend background script ko standard success response return karna
    return jsonify({"status": "success", "message": "Query received!"}), 200

if __name__ == '__main__':
    app.run(debug=True)
