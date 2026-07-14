from flask import Flask, render_template, request
import requests
from datetime import datetime, timedelta
from flask import send_from_directory
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Sirf Naya Telegram Bot (Vercel ENV: TELEGRAM_TOKEN_2 aur CHAT_ID_2)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN_2')
CHAT_ID = os.environ.get('CHAT_ID_2')

# Gmail Credentials (Vercel ENV se aayenge)
SENDER_EMAIL = os.environ.get('SENDER_EMAIL')
SENDER_APP_PASSWORD = os.environ.get('SENDER_APP_PASSWORD')

# Telegram Notification Engine (Bulletproof Setup)
def send_telegram_msg(data):
    if TELEGRAM_TOKEN and CHAT_ID:
        # Markdown hata diya taaki kisi bhi symbol (+, -) se message block na ho
        text = (
            f"🏔️ New Lead Alert!\n\n"
            f"👤 Name: {data['name']}\n"
            f"📞 Phone: {data['phone']}\n"
            f"📍 Destination: {data['destination']}\n"
            f"⏰ Time (IST): {data['timestamp']}\n\n"
            f"⚡ Action Required: Please contact the client at the earliest to confirm their requirements."
        )
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text} # Parse mode removed
        try:
            res = requests.post(url, json=payload, timeout=5)
            if res.status_code != 200:
                print(f"Telegram API Rejected: {res.text}")
        except Exception as e:
            print(f"Telegram Error: {e}")

# Ye route Google ko sitemap dikhayega
@app.route('/sitemap.xml')
def static_from_root():
    return send_from_directory(os.getcwd(), 'sitemap.xml')

@app.route('/blog/tirthan-valley')
def tirthan_blog():
    return render_template('tirthan.html')

# Main Website Route
@app.route('/')
def home():
    return render_template('index.html')

# Mountain Driving Blog Route
@app.route('/blog/mountain-driving')
def driving_blog():
    return render_template('driving.html')

# Himachali Dham Blog Route
@app.route('/blog/himachali-dham')
def dham_blog():
    return render_template('dham.html')

# Top 10 Routes Master Guide Route
@app.route('/blog/top-10-routes')
def top_routes_blog():
    return render_template('top-10-routes.html')

@app.route('/robots.txt')
def robots_txt():
    return send_from_directory(os.getcwd(), 'robots.txt')

# Form Submission Route
@app.route('/submit', methods=['POST'])
def submit():
    if request.method == 'POST':
        # Vercel UTC time ko IST (+05:30) me convert karna
        ist_now = datetime.utcnow() + timedelta(hours=5, minutes=30)
        formatted_time = ist_now.strftime("%d %b %Y, %I:%M %p")
        
        # Form se data nikalna (New UI ke hisab se destination add kiya)
        lead_data = {
            "timestamp": formatted_time,
            "name": request.form.get('name', request.form.get('FULL NAME', 'N/A')),
            "phone": request.form.get('phone', request.form.get('PHONE', 'N/A')),
            "destination": request.form.get('destination', request.form.get('package', 'N/A'))
        }
        
        # 1. Telegram par message bhejna
        send_telegram_msg(lead_data)
        
        # 2. Gmail par message bhejna
        if SENDER_EMAIL and SENDER_APP_PASSWORD:
            try:
                info_text = (
                    f"🏔️ New Lead Alert For All Himachal Yatra !\n\n"
                    f"👤 Name: {lead_data['name']}\n"
                    f"📞 Phone: {lead_data['phone']}\n"
                    f"📍 Destination: {lead_data['destination']}\n"
                    f"⏰ Time : {lead_data['timestamp']}\n\n"
                    f"⚡ Action Required: Please contact the client at the earliest to confirm their requirements."
                )
                
                email_msg = MIMEMultipart()
                email_msg['From'] = SENDER_EMAIL
                email_msg['To'] = SENDER_EMAIL 
                email_msg['Subject'] = f"New Lead: {lead_data['name']} ({lead_data['phone']})"
                email_msg.attach(MIMEText(info_text, 'plain'))
                
                server = smtplib.SMTP('smtp.gmail.com', 587)
                server.starttls()
                server.login(SENDER_EMAIL, SENDER_APP_PASSWORD)
                server.sendmail(SENDER_EMAIL, SENDER_EMAIL, email_msg.as_string())
                server.quit()
            except Exception as e:
                print(f"Gmail Error: {e}")
        
        # Premium Success Page
        return """
        <!DOCTYPE html>
        <html>
            <head>
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <style>
                    body { background-color: #050a12; color: #ffffff; font-family: 'Montserrat', sans-serif; text-align: center; padding-top: 15vh; }
                    h1 { color: #D4AF37; font-family: 'Playfair Display', serif; font-size: 3rem; margin-bottom: 10px; }
                    p { font-size: 1.2rem; opacity: 0.8; }
                    .btn { background: transparent; color: #D4AF37; border: 2px solid #D4AF37; padding: 12px 30px; text-decoration: none; border-radius: 50px; display: inline-block; margin-top: 20px; transition: 0.3s; }
                    .btn:hover { background: #D4AF37; color: #050a12; }
                </style>
            </head>
            <body>
                <h1>Thank You!</h1>
                <p>Your personalized travel request has been received.</p>
                <p>Our local expert will contact you shortly.</p>
                <a href="/" class="btn">&larr; Back to Home</a>
            </body>
        </html>
        """

if __name__ == '__main__':
    app.run(debug=True)
