from flask import Flask, render_template, request
import requests
from datetime import datetime
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

# Telegram Notification Engine (Single Bot Setup)
def send_telegram_msg(data):
    if TELEGRAM_TOKEN and CHAT_ID:
        text = f"🏔️ New Lead Alert!\n\n👤 Name: {data['name']}\n📞 Phone: {data['phone']}\n🎒 Package: {data['package']}\n⏰ Time: {data['timestamp']}"
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {"chat_id": CHAT_ID, "text": text}
        try:
            # Timeout 5 seconds rakha hai taaki page load na atke
            requests.post(url, json=payload, timeout=5)
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
        # Form se data nikalna
        lead_data = {
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "name": request.form.get('name', 'N/A'),
            "phone": request.form.get('phone', 'N/A'),
            "package": request.form.get('package', 'N/A')
        }
        
        # 1. Sirf Naye Telegram Bot par message bhejna
        send_telegram_msg(lead_data)
        
        # 2. Gmail par message bhejna
        if SENDER_EMAIL and SENDER_APP_PASSWORD:
            try:
                info_text = f"👤 Name: {lead_data['name']}\n📞 Phone: {lead_data['phone']}\n🎒 Package: {lead_data['package']}\n⏰ Time: {lead_data['timestamp']}"
                
                email_msg = MIMEMultipart()
                email_msg['From'] = SENDER_EMAIL
                email_msg['To'] = SENDER_EMAIL # Aapko apni mail par alert chahiye
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
                <p>Your premium experience request has been received.</p>
                <p>Our local expert will contact you shortly.</p>
                <a href="/" class="btn">&larr; Back to Home</a>
            </body>
        </html>
        """

# Vercel entry point
if __name__ == '__main__':
    app.run(debug=True)
