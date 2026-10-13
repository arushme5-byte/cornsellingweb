import os
import sqlite3
from datetime import datetime
from io import BytesIO
import base64
import qrcode
from flask import Flask, render_template_string, request, redirect, url_for, flash, g

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'social_flux_super_secret_key_2026')

DATABASE = 'database.db'

# --- Course Plans Data ---
COURSES = {
    1: {
        "id": 1,
        "name": "Full-Stack Web Mastery 2026",
        "image": "https://images.unsplash.com/photo-1555066931-4365d14bab8c?auto=format&fit=crop&w=800&q=80",
        "caption": "From Beginner to Advanced Full-Stack Developer",
        "description": "Master HTML, CSS, JavaScript, React, Node.js, Python Flask, and SQL through real-world production projects and architecture guidelines.",
        "video_count": "120+ HD Videos",
        "price": 2499,
        "original_price": 6999
    },
    2: {
        "id": 2,
        "name": "Advanced Python & Machine Learning",
        "image": "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?auto=format&fit=crop&w=800&q=80",
        "caption": "Dive into AI, Neural Networks & Data Science",
        "description": "Comprehensive curriculum covering NumPy, Pandas, Scikit-Learn, PyTorch, and building custom LLM-powered applications.",
        "video_count": "95+ HD Videos",
        "price": 2999,
        "original_price": 7999
    },
    3: {
        "id": 3,
        "name": "UI/UX Design & Figma Masterclass",
        "image": "https://images.unsplash.com/photo-1581291518633-83b4ebd1d83e?auto=format&fit=crop&w=800&q=80",
        "caption": "Design High-Converting Interfaces & Design Systems",
        "description": "Learn modern design thinking, wireframing, advanced prototyping, auto-layout, and interactive animations in Figma like a pro.",
        "video_count": "75+ HD Videos",
        "price": 1999,
        "original_price": 4999
    },
    4: {
        "id": 4,
        "name": "Cybersecurity & Ethical Hacking",
        "image": "https://images.unsplash.com/photo-1563986768609-322da13575f3?auto=format&fit=crop&w=800&q=80",
        "caption": "Protect Infrastructure & Master Penetration Testing",
        "description": "Learn network security, vulnerability assessments, Kali Linux tooling, web app penetration testing, and defense strategies.",
        "video_count": "110+ HD Videos",
        "price": 3499,
        "original_price": 8999
    },
    5: {
        "id": 5,
        "name": "DevOps & Cloud Engineering Bootcamp",
        "image": "https://images.unsplash.com/photo-1618401471353-b98aedd04e11?auto=format&fit=crop&w=800&q=80",
        "caption": "Docker, Kubernetes, AWS, CI/CD & Terraform",
        "description": "Master modern cloud infrastructure deployment, container orchestration, automated pipelines, and server management.",
        "video_count": "85+ HD Videos",
        "price": 2999,
        "original_price": 7499
    },
    6: {
        "id": 6,
        "name": "Mobile App Development with Flutter",
        "image": "https://images.unsplash.com/photo-1512941937669-90a1b58e7e9c?auto=format&fit=crop&w=800&q=80",
        "caption": "Build Cross-Platform iOS & Android Apps Fast",
        "description": "Learn Dart and Flutter from scratch to deploy high-performance, beautiful native apps on both App Store and Google Play.",
        "video_count": "90+ HD Videos",
        "price": 2299,
        "original_price": 5999
    },
    7: {
        "id": 7,
        "name": "Algorithmic Trading & Python Finance",
        "image": "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?auto=format&fit=crop&w=800&q=80",
        "caption": "Build Automated Trading Bots & Backtest Strategies",
        "description": "Connect to broker APIs, analyze financial market data, write quantitative trading algorithms, and manage automated risk.",
        "video_count": "60+ HD Videos",
        "price": 3999,
        "original_price": 9999
    },
    8: {
        "id": 8,
        "name": "AI Startup & SaaS Engineering Hub",
        "image": "https://images.unsplash.com/photo-1531403009284-440f080d1e12?auto=format&fit=crop&w=800&q=80",
        "caption": "Launch Scalable AI Micro-SaaS Businesses",
        "description": "End-to-end blueprint on conceptualizing, coding, integrating Stripe payments, marketing, and scaling a profitable AI micro-SaaS.",
        "video_count": "100+ HD Videos",
        "price": 4499,
        "original_price": 11999
    }
}

TELEGRAM_SUPPORT_URL = "https://t.me/socialflux_support"
UPI_ID = "haaland78@ybl"
PAYEE_NAME = "Social Flux"


def get_db():
    db = getattr(g, '_database', None)
    if db is None:
        db = g._database = sqlite3.connect(DATABASE)
        db.row_factory = sqlite3.Row
    return db

@app.teardown_appcontext
def close_connection(exception):
    db = getattr(g, '_database', None)
    if db is not None:
        db.close()

def init_db():
    with app.app_context():
        db = get_db()
        db.execute('''
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                utr TEXT UNIQUE NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
                submitted_at TEXT NOT NULL
            )
        ''')
        db.commit()

init_db()

# --- Common Global Styles & Scripts ---
GLOBAL_CSS = """
:root {
    --bg-black: #05020a;
    --bg-card: #0d0718;
    --bg-card-hover: #130a24;
    --primary-purple: #8b5cf6;
    --accent-pink: #ec4899;
    --text-main: #f3f4f6;
    --text-muted: #9ca3af;
    --border-color: #271b3c;
    --success-green: #10b981;
}
* { box-sizing: border-box; margin: 0; padding: 0; font-family: 'Inter', sans-serif; }
body { background-color: var(--bg-black); color: var(--text-main); min-height: 100vh; display: flex; flex-direction: column; overflow-x: hidden; }
header { background: rgba(5, 2, 10, 0.85); backdrop-filter: blur(12px); border-bottom: 1px solid var(--border-color); position: sticky; top: 0; z-index: 100; padding: 1rem 2rem; display: flex; justify-content: space-between; align-items: center; }
.logo-container { display: flex; align-items: center; gap: 0.75rem; text-decoration: none; }
.logo-badge { background: linear-gradient(135deg, #8b5cf6, #ec4899); width: 40px; height: 40px; border-radius: 10px; display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 1.25rem; color: white; box-shadow: 0 0 20px rgba(139, 92, 246, 0.5); }
.logo-text { font-size: 1.5rem; font-weight: 800; background: linear-gradient(to right, #ffffff, #c4b5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }
.nav-badge { background: rgba(139, 92, 246, 0.1); border: 1px solid rgba(139, 92, 246, 0.3); padding: 0.4rem 0.9rem; border-radius: 20px; font-size: 0.85rem; color: #c4b5fd; font-weight: 500; text-decoration: none; }
.telegram-float { position: fixed; bottom: 25px; right: 25px; background: #229ed9; color: white; width: 55px; height: 55px; border-radius: 50%; display: flex; align-items: center; justify-content: center; box-shadow: 0 6px 20px rgba(34, 158, 217, 0.5); z-index: 999; transition: all 0.3s ease; text-decoration: none; }
.telegram-float:hover { transform: scale(1.1); }
.telegram-float svg { width: 28px; height: 28px; fill: currentColor; }
footer { text-align: center; padding: 2rem; border-top: 1px solid var(--border-color); color: var(--text-muted); font-size: 0.85rem; background: var(--bg-black); }
.alert { padding: 0.85rem 1rem; border-radius: 8px; margin-bottom: 1.5rem; font-size: 0.9rem; background: rgba(239, 68, 68, 0.15); border: 1px solid rgba(239, 68, 68, 0.3); color: #fca5a5; }
"""

GLOBAL_JS = """
document.addEventListener('DOMContentLoaded', () => {
    const paymentForm = document.getElementById('paymentForm');
    if (paymentForm) {
        paymentForm.addEventListener('submit', (e) => {
            const utrInput = document.getElementById('utr');
            const submitBtn = document.getElementById('submitBtn');
            if (utrInput && utrInput.value.trim().length < 6) {
                e.preventDefault();
                alert('Please enter a valid 12-digit UPI reference (UTR) number.');
                utrInput.focus();
                return;
            }
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = 'Verifying & Submitting...';
                submitBtn.style.opacity = '0.7';
            }
        });
    }
    const upiSpan = document.getElementById('upiIdText');
    if (upiSpan) {
        upiSpan.style.cursor = 'pointer';
        upiSpan.title = 'Click to copy UPI ID';
        upiSpan.addEventListener('click', () => {
            navigator.clipboard.writeText(upiSpan.innerText).then(() => {
                const orig = upiSpan.innerText;
                upiSpan.innerText = 'Copied!';
                upiSpan.style.color = '#10b981';
                setTimeout(() => { upiSpan.innerText = orig; upiSpan.style.color = ''; }, 2000);
            });
        });
    }
});
"""

# --- HTML Templates ---
INDEX_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Social Flux — Premium Tech & Business Courses</title>
    <style>{GLOBAL_CSS}
    .hero {{ text-align: center; padding: 4rem 1.5rem 2rem; max-width: 900px; margin: 0 auto; }}
    .hero h1 {{ font-size: clamp(2.2rem, 5vw, 3.8rem); font-weight: 900; line-height: 1.15; margin-bottom: 1.2rem; background: linear-gradient(to right, #ffffff, #e9d5ff, #c4b5fd); -webkit-background-clip: text; -webkit-text-fill-color: transparent; }}
    .hero p {{ font-size: clamp(1rem, 2vw, 1.2rem); color: var(--text-muted); line-height: 1.6; margin-bottom: 2rem; }}
    .container {{ max-width: 1300px; margin: 0 auto; padding: 2rem 1.5rem 5rem; flex: 1; }}
    .section-title {{ font-size: 1.8rem; font-weight: 700; margin-bottom: 2rem; display: flex; align-items: center; gap: 0.75rem; border-left: 4px solid var(--primary-purple); padding-left: 0.75rem; }}
    .courses-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(290px, 1fr)); gap: 2rem; }}
    .course-card {{ background-color: var(--bg-card); border: 1px solid var(--border-color); border-radius: 16px; overflow: hidden; display: flex; flex-direction: column; transition: all 0.3s ease; }}
    .course-card:hover {{ transform: translateY(-6px); border-color: rgba(139, 92, 246, 0.5); box-shadow: 0 12px 30px rgba(139, 92, 246, 0.2); background-color: var(--bg-card-hover); }}
    .course-img-wrapper {{ width: 100%; height: 190px; overflow: hidden; }}
    .course-img-wrapper img {{ width: 100%; height: 100%; object-fit: cover; transition: transform 0.5s ease; }}
    .course-card:hover .course-img-wrapper img {{ transform: scale(1.05); }}
    .course-content {{ padding: 1.5rem; display: flex; flex-direction: column; flex: 1; }}
    .course-title {{ font-size: 1.2rem; font-weight: 700; margin-bottom: 0.5rem; color: var(--text-main); }}
    .course-caption {{ font-size: 0.85rem; color: #c4b5fd; font-weight: 600; margin-bottom: 0.75rem; text-transform: uppercase; }}
    .course-desc {{ font-size: 0.92rem; color: var(--text-muted); line-height: 1.5; margin-bottom: 1.25rem; flex: 1; }}
    .course-meta {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 1.25rem; padding-top: 0.75rem; border-top: 1px solid rgba(255, 255, 255, 0.05); font-size: 0.85rem; color: var(--text-muted); }}
    .video-badge {{ display: flex; align-items: center; gap: 0.4rem; background: rgba(139, 92, 246, 0.1); padding: 0.3rem 0.6rem; border-radius: 6px; color: #d8b4fe; }}
    .price-section {{ display: flex; align-items: baseline; gap: 0.75rem; margin-bottom: 1.25rem; }}
    .current-price {{ font-size: 1.6rem; font-weight: 800; color: #ffffff; }}
    .original-price {{ font-size: 1rem; color: var(--text-muted); text-decoration: line-through; }}
    .btn-buy {{ background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border: none; padding: 0.85rem 1.25rem; border-radius: 10px; font-weight: 700; font-size: 1rem; text-align: center; text-decoration: none; cursor: pointer; transition: all 0.2s ease; display: flex; align-items: center; justify-content: center; gap: 0.5rem; }}
    .btn-buy:hover {{ background: linear-gradient(135deg, #8b5cf6, #7c3aed); box-shadow: 0 6px 20px rgba(139, 92, 246, 0.6); transform: translateY(-2px); }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo-container">
            <div class="logo-badge">SF</div>
            <span class="logo-text">SOCIAL FLUX</span>
        </a>
        <div class="nav-badge">🔥 2026 Batch Live</div>
    </header>

    <section class="hero">
        <h1>Master In-Demand Skills with Industry Experts</h1>
        <p>Accelerate your career with elite, production-grade video courses built for modern engineers, creators, and founders.</p>
    </section>

    <main class="container">
        <h2 class="section-title">Featured Course Plans</h2>
        <div class="courses-grid">
            {{ courses_html|safe }}
        </div>
    </main>

    <a href="{{ telegram_url }}" target="_blank" class="telegram-float" title="Chat with Support on Telegram">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.03-1.99 1.27-5.62 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.37-.26-2.03-.48-.82-.27-1.47-.42-1.42-.88.03-.25.38-.51 1.05-.78 4.1-1.79 6.84-2.97 8.22-3.53 3.91-1.62 4.72-1.9 5.25-1.9.12 0 .39.03.56.17.14.12.18.28.2.45-.02.07-.02.13-.04.23z"/></svg>
    </a>

    <footer>
        <p>&copy; 2026 Social Flux Inc. All rights reserved. Secure Encrypted Payments.</p>
    </footer>
    <script>{{ global_js|safe }}</script>
</body>
</html>
"""

PAYMENT_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Complete Payment — {{ course.name }} | Social Flux</title>
    <style>{GLOBAL_CSS}
    .payment-wrapper {{ max-width: 900px; margin: 2rem auto; padding: 0 1.5rem; width: 100%; }}
    .payment-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 20px; padding: 2.5rem; box-shadow: 0 20px 40px rgba(0,0,0,0.5); }}
    .payment-section-title {{ font-size: 1.25rem; font-weight: 700; margin-bottom: 1.25rem; display: flex; align-items: center; gap: 0.75rem; color: #e9d5ff; }}
    .payment-step {{ margin-bottom: 2.5rem; padding-bottom: 2rem; border-bottom: 1px solid var(--border-color); }}
    .payment-step:last-child {{ border-bottom: none; margin-bottom: 0; padding-bottom: 0; }}
    .order-summary-box {{ display: flex; gap: 1.5rem; background: rgba(13, 7, 24, 0.6); padding: 1.25rem; border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2); align-items: center; }}
    .order-summary-img {{ width: 120px; height: 90px; border-radius: 8px; object-fit: cover; }}
    .order-summary-details h3 {{ font-size: 1.15rem; margin-bottom: 0.3rem; }}
    .order-summary-details p {{ font-size: 0.85rem; color: var(--text-muted); margin-bottom: 0.5rem; }}
    .order-total-price {{ font-size: 1.3rem; font-weight: 800; color: var(--success-green); }}
    .upi-apps-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(140px, 1fr)); gap: 1rem; }}
    .upi-app-btn {{ background: #130a24; border: 1px solid var(--border-color); border-radius: 12px; padding: 1rem; color: white; text-align: center; text-decoration: none; font-weight: 600; font-size: 0.9rem; display: flex; flex-direction: column; align-items: center; gap: 0.6rem; transition: all 0.2s ease; }}
    .upi-app-btn:hover {{ border-color: var(--primary-purple); background: rgba(139, 92, 246, 0.15); transform: translateY(-2px); }}
    .upi-app-icon {{ width: 38px; height: 38px; border-radius: 50%; background: #7c3aed; display: flex; align-items: center; justify-content: center; font-weight: bold; font-size: 1rem; }}
    .qr-container {{ display: flex; flex-direction: column; align-items: center; background: white; padding: 1.5rem; border-radius: 16px; width: fit-content; margin: 0 auto 1rem; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
    .qr-container img {{ width: 200px; height: 200px; display: block; }}
    .upi-id-box {{ text-align: center; font-size: 0.9rem; color: var(--text-muted); }}
    .upi-id-box span {{ color: white; font-weight: 700; background: #1a102f; padding: 0.2rem 0.6rem; border-radius: 6px; border: 1px solid var(--border-color); }}
    .form-group {{ margin-bottom: 1.25rem; }}
    .form-group label {{ display: block; font-size: 0.9rem; font-weight: 600; margin-bottom: 0.5rem; color: #e9d5ff; }}
    .form-input {{ width: 100%; background: #05020a; border: 1px solid var(--border-color); padding: 0.85rem 1rem; border-radius: 10px; color: white; font-size: 1rem; outline: none; }}
    .form-input:focus {{ border-color: var(--primary-purple); box-shadow: 0 0 10px rgba(139, 92, 246, 0.2); }}
    .btn-submit {{ width: 100%; background: linear-gradient(135deg, #10b981, #059669); color: white; border: none; padding: 1rem; border-radius: 10px; font-weight: 700; font-size: 1rem; cursor: pointer; transition: all 0.2s ease; }}
    .btn-submit:hover {{ background: linear-gradient(135deg, #059669, #047857); }}
    @media(max-width: 768px) {{ .order-summary-box {{ flex-direction: column; align-items: flex-start; }} .order-summary-img {{ width: 100%; height: 140px; }} }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo-container">
            <div class="logo-badge">SF</div>
            <span class="logo-text">SOCIAL FLUX</span>
        </a>
        <a href="/" class="nav-badge">← Back to Courses</a>
    </header>

    <div class="payment-wrapper">
        <div class="payment-card">
            {% if error %}
                <div class="alert">{{ error }}</div>
            {% endif %}

            <form id="paymentForm" action="/submit_payment" method="POST">
                <input type="hidden" name="plan_id" value="{{ course.id }}">

                <div class="payment-step">
                    <div class="payment-section-title"><span>1. Order Summary</span></div>
                    <div class="order-summary-box">
                        <img src="{{ course.image }}" alt="{{ course.name }}" class="order-summary-img">
                        <div class="order-summary-details">
                            <h3>{{ course.name }}</h3>
                            <p>{{ course.caption }}</p>
                            <div class="order-total-price">Total Payable: ₹{{ course.price }}</div>
                        </div>
                    </div>
                </div>

                <div class="payment-step">
                    <div class="payment-section-title"><span>2. Pay with UPI App (Mobile)</span></div>
                    <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1rem;">Clicking any UPI app below will attempt to open the app directly on supported mobile devices.</p>
                    <div class="upi-apps-grid">
                        <a href="{{ upi_link }}" class="upi-app-btn"><div class="upi-app-icon" style="background: #4285F4;">G</div><span>Google Pay</span></a>
                        <a href="{{ upi_link }}" class="upi-app-btn"><div class="upi-app-icon" style="background: #5f259f;">P</div><span>PhonePe</span></a>
                        <a href="{{ upi_link }}" class="upi-app-btn"><div class="upi-app-icon" style="background: #00baf2;">Pt</div><span>Paytm</span></a>
                        <a href="{{ upi_link }}" class="upi-app-btn"><div class="upi-app-icon" style="background: #ff6600;">B</div><span>BHIM UPI</span></a>
                        <a href="{{ upi_link }}" class="upi-app-btn"><div class="upi-app-icon" style="background: #7c3aed;">UPI</div><span>Other Apps</span></a>
                    </div>
                </div>

                <div class="payment-step">
                    <div class="payment-section-title"><span>3. Scan to Pay (Desktop / Secondary Phone)</span></div>
                    <div class="qr-container">
                        <img src="data:image/png;base64,{{ qr_code_b64 }}" alt="UPI Payment QR Code">
                    </div>
                    <div class="upi-id-box">
                        <p style="margin-bottom: 0.3rem;">Scan using any UPI app or pay directly to UPI ID:</p>
                        <span id="upiIdText" title="Click to copy">{{ upi_id }}</span>
                        <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.4rem;">Payee Name: <strong>{{ payee_name }}</strong> | Amount: <strong>₹{{ course.price }}</strong></p>
                    </div>
                </div>

                <div class="payment-step">
                    <div class="payment-section-title"><span>4. Enter Payment Reference (UTR / UPI Ref No)</span></div>
                    <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 1rem;">Once you complete the payment on your UPI app, enter your 12-digit UTR or Transaction Reference number below.</p>
                    <div class="form-group">
                        <label for="utr">UPI Transaction Reference / UTR Number *</label>
                        <input type="text" id="utr" name="utr" class="form-input" placeholder="e.g. 403928102938" required autocomplete="off">
                    </div>
                    <button type="submit" id="submitBtn" class="btn-submit">Submit Payment Reference</button>
                </div>
            </form>
        </div>
    </div>

    <a href="{{ telegram_url }}" target="_blank" class="telegram-float" title="Chat with Support on Telegram">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.03-1.99 1.27-5.62 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.37-.26-2.03-.48-.82-.27-1.47-.42-1.42-.88.03-.25.38-.51 1.05-.78 4.1-1.79 6.84-2.97 8.22-3.53 3.91-1.62 4.72-1.9 5.25-1.9.12 0 .39.03.56.17.14.12.18.28.2.45-.02.07-.02.13-.04.23z"/></svg>
    </a>

    <footer><p>&copy; 2026 Social Flux Inc. All rights reserved.</p></footer>
    <script>{{ global_js|safe }}</script>
</body>
</html>
"""

SUCCESS_HTML = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Payment Submitted — Social Flux</title>
    <style>{GLOBAL_CSS}
    .payment-wrapper {{ max-width: 900px; margin: 2rem auto; padding: 0 1.5rem; width: 100%; }}
    .payment-card {{ background: var(--bg-card); border: 1px solid var(--border-color); border-radius: 20px; padding: 2.5rem; box-shadow: 0 20px 40px rgba(0,0,0,0.5); text-align: center; }}
    .success-icon {{ width: 70px; height: 70px; background: rgba(16, 185, 129, 0.2); border: 2px solid var(--success-green); color: var(--success-green); border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 2rem; margin: 0 auto 1.5rem; }}
    .status-badge-pending {{ display: inline-block; background: rgba(245, 158, 11, 0.15); color: #fcd34d; border: 1px solid rgba(245, 158, 11, 0.3); padding: 0.3rem 0.9rem; border-radius: 20px; font-weight: 600; font-size: 0.85rem; }}
    .btn-home {{ background: linear-gradient(135deg, #7c3aed, #6d28d9); color: white; border: none; padding: 0.85rem 1.25rem; border-radius: 10px; font-weight: 700; font-size: 1rem; text-decoration: none; display: inline-block; width: 100%; text-align: center; }}
    </style>
</head>
<body>
    <header>
        <a href="/" class="logo-container">
            <div class="logo-badge">SF</div>
            <span class="logo-text">SOCIAL FLUX</span>
        </a>
    </header>

    <div class="payment-wrapper">
        <div class="payment-card">
            <div class="success-icon">✓</div>
            <h2 style="font-size: 1.8rem; margin-bottom: 0.5rem; color: white;">Payment Reference Received</h2>
            <p style="color: var(--text-muted); margin-bottom: 2rem;">Thank you! Your transaction reference has been securely recorded in our verification queue.</p>

            <div style="background: rgba(13, 7, 24, 0.6); border: 1px solid var(--border-color); border-radius: 12px; padding: 1.5rem; text-align: left; margin-bottom: 2rem;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Selected Course:</span>
                    <strong style="color: white;">{{ course.name }}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Amount:</span>
                    <strong style="color: var(--success-green);">₹{{ course.price }}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Submitted UTR:</span>
                    <strong style="color: #c4b5fd; font-family: monospace;">{{ utr }}</strong>
                </div>
                <div style="display: flex; justify-content: space-between; margin-bottom: 0.75rem; border-bottom: 1px solid rgba(255,255,255,0.05); padding-bottom: 0.5rem;">
                    <span style="color: var(--text-muted);">Submission Time:</span>
                    <span style="color: white; font-size: 0.9rem;">{{ submitted_at }}</span>
                </div>
                <div style="display: flex; justify-content: space-between; align-items: center;">
                    <span style="color: var(--text-muted);">Current Status:</span>
                    <div class="status-badge-pending">PENDING VERIFICATION</div>
                </div>
            </div>

            <p style="font-size: 0.88rem; color: var(--text-muted); margin-bottom: 2rem; line-height: 1.6;">
                Our finance team is verifying your transaction reference against our bank settlement ledger. Course access credentials will be automatically dispatched once confirmed.
            </p>

            <a href="/" class="btn-home">Return to Homepage</a>
        </div>
    </div>

    <a href="{{ telegram_url }}" target="_blank" class="telegram-float" title="Chat with Support on Telegram">
        <svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm4.64 6.8c-.15 1.58-.8 5.42-1.13 7.19-.14.75-.42 1-.68 1.03-.58.05-1.02-.38-1.58-.75-.88-.58-1.38-.94-2.23-1.5-.99-.65-.35-1.01.22-1.59.15-.15 2.71-2.48 2.76-2.69.01-.03.01-.14-.07-.2-.08-.06-.19-.04-.27-.02-.12.03-1.99 1.27-5.62 3.72-.53.36-1.01.54-1.44.53-.47-.01-1.37-.26-2.03-.48-.82-.27-1.47-.42-1.42-.88.03-.25.38-.51 1.05-.78 4.1-1.79 6.84-2.97 8.22-3.53 3.91-1.62 4.72-1.9 5.25-1.9.12 0 .39.03.56.17.14.12.18.28.2.45-.02.07-.02.13-.04.23z"/></svg>
    </a>

    <footer><p>&copy; 2026 Social Flux Inc. All rights reserved.</p></footer>
</body>
</html>
"""


# --- Flask Routes ---
@app.route('/health')
def health_check():
    return {"status": "healthy", "service": "Social Flux API"}, 200


@app.route('/')
def index():
    # Build course cards dynamically
    courses_html = ""
    for course_id, course in COURSES.items():
        courses_html += f"""
        <div class="course-card">
            <div class="course-img-wrapper">
                <img src="{course['image']}" alt="{course['name']}" loading="lazy">
            </div>
            <div class="course-content">
                <h3 class="course-title">{course['name']}</h3>
                <div class="course-caption">{course['caption']}</div>
                <p class="course-desc">{course['description']}</p>
                <div class="course-meta">
                    <div class="video-badge">
                        <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
                        <span>{course['video_count']}</span>
                    </div>
                    <span>Lifetime Access</span>
                </div>
                <div class="price-section">
                    <span class="current-price">₹{course['price']}</span>
                    <span class="original-price">₹{course['original_price']}</span>
                </div>
                <a href="/payment/{course['id']}" class="btn-buy">
                    <span>Buy Now — ₹{course['price']}</span>
                    <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"></line><polyline points="12 5 19 12 12 19"></polyline></svg>
                </a>
            </div>
        </div>
        """
    return render_template_string(INDEX_HTML, courses_html=courses_html, telegram_url=TELEGRAM_SUPPORT_URL, global_js=GLOBAL_JS)


@app.route('/payment/<int:plan_id>')
def payment(plan_id):
    if plan_id not in COURSES:
        return redirect(url_for('index'))
    
    course = COURSES[plan_id]
    amount = course['price']
    upi_link = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME}&am={amount}.00&cu=INR&tn=SocialFlux_Course_{plan_id}"
    
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(upi_link)
    qr.make(fit=True)
    img = qr.make_image(fill_color="#0b0614", back_color="#ffffff")
    
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    qr_code_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')

    return render_template_string(PAYMENT_HTML, 
                                  course=course, 
                                  upi_link=upi_link, 
                                  upi_id=UPI_ID, 
                                  payee_name=PAYEE_NAME,
                                  qr_code_b64=qr_code_b64,
                                  telegram_url=TELEGRAM_SUPPORT_URL,
                                  global_js=GLOBAL_JS,
                                  error=None)


@app.route('/submit_payment', methods=['POST'])
def submit_payment():
    plan_id = request.form.get('plan_id', type=int)
    utr = request.form.get('utr', '').strip()
    
    if not plan_id or plan_id not in COURSES:
        return redirect(url_for('index'))
    
    course = COURSES[plan_id]
    
    if not utr or len(utr) < 6:
        # Re-render payment with error
        amount = course['price']
        upi_link = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME}&am={amount}.00&cu=INR&tn=SocialFlux_Course_{plan_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0b0614", back_color="#ffffff")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return render_template_string(PAYMENT_HTML, 
                                      course=course, 
                                      upi_link=upi_link, 
                                      upi_id=UPI_ID, 
                                      payee_name=PAYEE_NAME,
                                      qr_code_b64=qr_code_b64,
                                      telegram_url=TELEGRAM_SUPPORT_URL,
                                      global_js=GLOBAL_JS,
                                      error="Please enter a valid 12-digit UTR reference number.")

    submitted_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    db = get_db()
    try:
        db.execute('''
            INSERT INTO payments (plan_id, plan_name, amount, utr, status, submitted_at)
            VALUES (?, ?, ?, ?, 'PENDING', ?)
        ''', (course['id'], course['name'], course['price'], utr, submitted_at))
        db.commit()
    except sqlite3.IntegrityError:
        # Duplicate UTR handling
        amount = course['price']
        upi_link = f"upi://pay?pa={UPI_ID}&pn={PAYEE_NAME}&am={amount}.00&cu=INR&tn=SocialFlux_Course_{plan_id}"
        qr = qrcode.QRCode(version=1, box_size=10, border=4)
        qr.add_data(upi_link)
        qr.make(fit=True)
        img = qr.make_image(fill_color="#0b0614", back_color="#ffffff")
        buffered = BytesIO()
        img.save(buffered, format="PNG")
        qr_code_b64 = base64.b64encode(buffered.getvalue()).decode('utf-8')
        
        return render_template_string(PAYMENT_HTML, 
                                      course=course, 
                                      upi_link=upi_link, 
                                      upi_id=UPI_ID, 
                                      payee_name=PAYEE_NAME,
                                      qr_code_b64=qr_code_b64,
                                      telegram_url=TELEGRAM_SUPPORT_URL,
                                      global_js=GLOBAL_JS,
                                      error="This UTR / Transaction Reference has already been submitted.")
    
    return render_template_string(SUCCESS_HTML, 
                                  course=course, 
                                  utr=utr, 
                                  submitted_at=submitted_at, 
                                  telegram_url=TELEGRAM_SUPPORT_URL)


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
