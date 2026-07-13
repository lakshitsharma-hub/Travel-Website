from flask import Flask, render_template, request
import requests
from datetime import datetime
from flask import send_from_directory
import os

app = Flask(__name__)

# Bot 1: Values Vercel ke dashboard se uthayi jayengi (Main Production Bot)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
CHAT_ID = os.environ.get('CHAT_ID')

# Bot 2: Tumhara naya Personal Test Bot (Vercel ENV se aayega)
BOT_TOKEN_2 = os.environ.get('TELEGRAM_TOKEN_2')
CHAT_ID_2 = os.environ.get('CHAT_ID_2')

# Telegram Notification Engine (Multi-Bot Setup)
def send_telegram_msg(data):
    # Dono bots ki list
    bots = [
        {"token": TELEGRAM_TOKEN, "chat_id": CHAT_ID},
        {"token": BOT_TOKEN_2, "chat_id": CHAT_ID_2}
    ]
    
    # Message ka format
    text = f"🏔️ New Lead Alert!\n\n👤 Name: {data['name']}\n📞 Phone: {data['phone']}\n🎒 Package: {data['package']}\n⏰ Time: {data['timestamp']}"
    
    # Loop chala kar dono bots ko parallel message bhejna
    for bot in bots:
        # Check karna ki token available hai (agar Vercel env missing ho toh error na aaye)
        if bot["token"] and bot["chat_id"]:
            url = f"https://api.telegram.org/bot{bot['token']}/sendMessage"
            payload = {"chat_id": bot["chat_id"], "text": text}
            try:
                # Timeout 5 seconds rakha hai taaki page load na atke
                requests.post(url, json=payload, timeout=5)
            except Exception as e:
                print(f"Telegram Error for bot {bot['token'][:10]}... :", e)

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
            "name": request.form.get('name'),
            "phone": request.form.get('phone'),
            "package": request.form.get('package')
        }
        
        # Telegram par message bhejna
        send_telegram_msg(lead_data)
        
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
