import os
import io
import sqlite3
import secrets
from urllib.parse import urlencode

import qrcode

from flask import (
    Flask,
    request,
    redirect,
    url_for,
    render_template_string,
    abort,
    Response,
    session,
    flash
)

# =====================================================
# 1. FLASK CONFIGURATION
# =====================================================

app = Flask(__name__)

app.secret_key = os.environ.get(
    "SECRET_KEY",
    secrets.token_hex(32)
)

DB_PATH = os.environ.get("DB_PATH", "payments.db")

# Default Admin Credentials (Change these as needed)
ADMIN_USER = os.environ.get("ADMIN_USER", "admin")
ADMIN_PASS = os.environ.get("ADMIN_PASS", "fluxadmin123")

# =====================================================
# 2. WEBSITE SETTINGS
# =====================================================

SITE_NAME = "SOCIAL FLUX"

LOGO_URL = (
    "https://placehold.co/300x300/24113f/ffffff"
    "?text=FLUX"
)

DEFAULT_UPI_ID = os.environ.get("UPI_ID", "haaland78@ybl")
DEFAULT_PAYEE_NAME = os.environ.get("PAYEE_NAME", "Social Flux")

TELEGRAM_SUPPORT = "https://t.me/YOUR_SUPPORT_USERNAME"

# =====================================================
# 3. EDIT YOUR PLANS HERE
# =====================================================

PLANS = [
    {
        "id": 1,
        "name": "VIP FRESH CHILD PORN ",
        "price": 99,
        "image": "https://ibb.co/6c4RL0bj",
        "caption": "GET 70K+ CHILD FRESH PORN VIDEO",
        "videos": "7000+ Videos",
        "description": "ALL HIGH QUALITY VIDEOS 😍"
    },
    {
        "id": 2,
        "name": "PLAN 2",
        "price": 149,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+2",
        "caption": "Your second course plan.",
        "videos": "15+ Videos",
        "description": "Add the complete description of Plan 2 here."
    },
    {
        "id": 3,
        "name": "PLAN 3",
        "price": 199,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+3",
        "caption": "Your third course plan.",
        "videos": "20+ Videos",
        "description": "Add the complete description of Plan 3 here."
    },
    {
        "id": 4,
        "name": "PLAN 4",
        "price": 249,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+4",
        "caption": "Your fourth course plan.",
        "videos": "25+ Videos",
        "description": "Add the complete description of Plan 4 here."
    },
    {
        "id": 5,
        "name": "PLAN 5",
        "price": 299,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+5",
        "caption": "Your fifth course plan.",
        "videos": "30+ Videos",
        "description": "Add the complete description of Plan 5 here."
    },
    {
        "id": 6,
        "name": "PLAN 6",
        "price": 349,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+6",
        "caption": "Your sixth course plan.",
        "videos": "35+ Videos",
        "description": "Add the complete description of Plan 6 here."
    },
    {
        "id": 7,
        "name": "PLAN 7",
        "price": 399,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+7",
        "caption": "Your seventh course plan.",
        "videos": "40+ Videos",
        "description": "Add the complete description of Plan 7 here."
    },
    {
        "id": 8,
        "name": "PLAN 8",
        "price": 499,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+8",
        "caption": "Your eighth course plan.",
        "videos": "50+ Videos",
        "description": "Add the complete description of Plan 8 here."
    }
]


def get_plan(plan_id):
    return next((plan for plan in PLANS if plan["id"] == plan_id), None)


# =====================================================
# 4. DATABASE & SETTINGS
# =====================================================

def init_database():
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                amount REAL NOT NULL,
                utr TEXT NOT NULL UNIQUE,
                status TEXT NOT NULL DEFAULT 'PENDING',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            )
        """)
        # Initialize default settings if not present
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key='upi_id'")
        if not cursor.fetchone():
            conn.execute("INSERT INTO settings (key, value) VALUES ('upi_id', ?)", (DEFAULT_UPI_ID,))
        
        cursor.execute("SELECT value FROM settings WHERE key='payee_name'")
        if not cursor.fetchone():
            conn.execute("INSERT INTO settings (key, value) VALUES ('payee_name', ?)", (DEFAULT_PAYEE_NAME,))
        
        conn.commit()


init_database()


def get_setting(key, default):
    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT value FROM settings WHERE key=?", (key,))
        row = cursor.fetchone()
        return row[0] if row else default


def set_setting(key, value):
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, value))
        conn.commit()


# =====================================================
# 5. PREMIUM CSS
# =====================================================

CSS = """
:root {
    --bg: #090611;
    --card: #151020;
    --purple: #9b5cff;
    --purple-light: #c4a2ff;
    --text: #f7f2ff;
    --muted: #b9aecb;
    --border: #30213f;
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
    margin: 0;
    color: var(--text);
    background: radial-gradient(ellipse at top, #211037 0%, var(--bg) 55%);
    font-family: Arial, Helvetica, sans-serif;
    min-height: 100vh;
}

a { color: inherit; }

.container {
    width: min(1120px, 100%);
    margin: auto;
    padding: 22px;
}

.navbar {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 8px 0 28px;
}

.nav-left {
    display: flex;
    align-items: center;
    gap: 13px;
}

.logo {
    width: 55px;
    height: 55px;
    border-radius: 50%;
    object-fit: cover;
    border: 2px solid var(--purple);
    box-shadow: 0 0 22px #8b5cf655;
    flex-shrink: 0;
}

.brand {
    font-size: 22px;
    font-weight: 900;
    letter-spacing: 1px;
}

.brand span { color: var(--purple-light); }

.tagline {
    color: var(--muted);
    font-size: 12px;
    margin-top: 5px;
}

.hero {
    padding: 26px 0 35px;
    animation: fadeUp .7s ease both;
}

.badge {
    display: inline-block;
    background: #291940;
    border: 1px solid #593b79;
    color: #d8c0ff;
    border-radius: 100px;
    padding: 8px 13px;
    font-size: 12px;
    margin-bottom: 13px;
}

.hero h1 {
    font-size: clamp(30px, 6vw, 52px);
    line-height: 1.1;
    margin: 0 0 15px;
}

.gradient-text {
    background: linear-gradient(90deg, #c5a4ff, #9956ff, #e5ccff);
    color: transparent;
    background-clip: text;
    -webkit-background-clip: text;
}

.hero p {
    max-width: 620px;
    color: var(--muted);
    line-height: 1.7;
}

.section-title {
    font-size: 25px;
    margin: 15px 0 20px;
}

.plans-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 22px;
}

.plan-card {
    background: linear-gradient(150deg, #1a1228, #100c19);
    border: 1px solid var(--border);
    border-radius: 19px;
    overflow: hidden;
    transition: transform .25s ease, border-color .25s ease, box-shadow .25s ease;
}

.plan-card:hover {
    transform: translateY(-5px);
    border-color: #8151ba;
    box-shadow: 0 14px 38px #0005;
}

.plan-image {
    display: block;
    width: 100%;
    aspect-ratio: 16 / 9;
    object-fit: cover;
    background: #21152e;
}

.plan-content { padding: 20px; }

.plan-label {
    color: var(--purple-light);
    font-size: 11px;
    font-weight: bold;
    letter-spacing: 1.5px;
    text-transform: uppercase;
}

.plan-name {
    font-size: 22px;
    margin: 10px 0;
}

.caption {
    font-size: 14px;
    color: var(--muted);
    line-height: 1.7;
    min-height: 45px;
    overflow-wrap: anywhere;
}

.video-count {
    display: inline-block;
    color: #d6c1ff;
    background: #291c3c;
    border-radius: 7px;
    padding: 8px 10px;
    font-size: 12px;
    margin-top: 8px;
}

.price-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;
    margin: 19px 0;
}

.price-label { color: var(--muted); font-size: 12px; }
.price { font-size: 27px; font-weight: 900; margin-top: 4px; }

.button {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    min-height: 48px;
    border: 0;
    border-radius: 11px;
    background: linear-gradient(100deg, #7541d8, #a75bff);
    color: white;
    text-decoration: none;
    font-weight: 800;
    font-size: 14px;
    padding: 13px 15px;
    cursor: pointer;
    transition: transform .2s ease, filter .2s ease;
}

.button:hover { filter: brightness(1.13); transform: translateY(-2px); }
.button.secondary { background: #241a32; border: 1px solid #4c3765; }

.payment-panel {
    max-width: 650px;
    margin: 12px auto 35px;
    padding: 23px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: #151020;
}

.payment-image {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    border-radius: 13px;
    margin-bottom: 18px;
}

.payment-panel h1 { font-size: 28px; margin: 7px 0 12px; }
.payment-panel h2 { font-size: 19px; margin-top: 27px; }

.muted { color: var(--muted); line-height: 1.7; font-size: 14px; overflow-wrap: anywhere; }

.order-summary {
    padding: 17px;
    border-radius: 13px;
    background: #20172e;
    border: 1px solid #39264d;
    margin: 20px 0;
}

.total-row {
    display: flex;
    justify-content: space-between;
    gap: 15px;
    align-items: center;
}

.total-price { font-size: 26px; font-weight: 900; color: var(--purple-light); }

.app-grid {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 11px;
    margin: 15px 0;
}

.app-button {
    text-decoration: none;
    text-align: center;
    background: #21182f;
    border: 1px solid #45325a;
    border-radius: 12px;
    padding: 16px 8px;
    transition: background .2s, transform .2s;
}

.app-button:hover { background: #342049; transform: translateY(-2px); }
.app-icon { display: block; font-size: 25px; margin-bottom: 8px; }
.app-name { font-size: 13px; font-weight: bold; }

.qr-box {
    padding: 18px;
    background: white;
    border-radius: 15px;
    width: fit-content;
    max-width: 100%;
    margin: 18px auto;
    text-align: center;
}

.qr-image { display: block; width: min(260px, 65vw); height: auto; }

.input {
    width: 100%;
    min-height: 48px;
    padding: 13px;
    color: white;
    background: #0d0915;
    border: 1px solid #49345d;
    border-radius: 10px;
    outline: none;
    margin: 10px 0;
    font-size: 15px;
}

.input:focus { border-color: var(--purple); box-shadow: 0 0 0 3px #9b5cff20; }

.alert {
    padding: 14px;
    border-radius: 10px;
    margin-bottom: 15px;
    font-size: 13px;
    line-height: 1.5;
}
.alert-error { background: #3d1515; border: 1px solid #753030; color: #ffb8b8; }
.alert-success { background: #153d1f; border: 1px solid #307542; color: #b8ffc7; }

.admin-table {
    width: 100%;
    border-collapse: collapse;
    margin-top: 20px;
    background: #110c1c;
    border-radius: 12px;
    overflow: hidden;
    border: 1px solid var(--border);
}

.admin-table th, .admin-table td {
    padding: 12px 15px;
    text-align: left;
    font-size: 13px;
    border-bottom: 1px solid var(--border);
}

.admin-table th { background: #20172e; color: var(--purple-light); }

.badge-pending { background: #3b2b13; color: #ffe08a; padding: 4px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }
.badge-success { background: #153d1f; color: #b8ffc7; padding: 4px 8px; border-radius: 5px; font-size: 11px; font-weight: bold; }

.support-button {
    position: fixed;
    right: 18px;
    bottom: 18px;
    z-index: 10;
    background: #7541d8;
    color: white;
    text-decoration: none;
    padding: 14px 17px;
    border-radius: 50px;
    font-weight: bold;
    font-size: 13px;
    box-shadow: 0 6px 25px #0008;
}

.footer { text-align: center; padding: 35px 10px; color: var(--muted); font-size: 12px; }

@media (max-width: 650px) {
    .container { padding: 16px; }
    .plans-grid { grid-template-columns: 1fr; gap: 17px; }
}
"""


# =====================================================
# 6. HTML TEMPLATES
# =====================================================

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{{ site_name }} | Course Plans</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="container">
    <header class="navbar">
        <div class="nav-left">
            <img class="logo" src="{{ logo_url }}" alt="Logo">
            <div>
                <div class="brand">SOCIAL <span>FLUX</span></div>
                <div class="tagline">YOUR LEARNING STARTS HERE</div>
            </div>
        </div>
        <div>
            <a href="{{ url_for('admin_login') }}" class="button secondary" style="min-height: 38px; padding: 8px 15px; font-size: 12px;">Admin Login</a>
        </div>
    </header>

    <section class="hero">
        <div class="badge">✦ PREMIUM COURSE COLLECTION</div>
        <h1>Choose Your<br><span class="gradient-text">Perfect Plan</span></h1>
        <p>Explore our available course plans. Choose your plan, pay securely via UPI, and submit your UTR to get instant access.</p>
    </section>

    <h2 class="section-title">Available Plans</h2>

    <section class="plans-grid">
        {% for p in plans %}
        <article class="plan-card">
            <img class="plan-image" src="{{ p.image }}" alt="{{ p.name }}" loading="lazy">
            <div class="plan-content">
                <div class="plan-label">PREMIUM COURSE</div>
                <h2 class="plan-name">{{ p.name }}</h2>
                <p class="caption">{{ p.caption }}</p>
                <div class="video-count">▶ {{ p.videos }}</div>
                <div class="price-row">
                    <div>
                        <div class="price-label">PLAN PRICE</div>
                        <div class="price">₹{{ "%.2f"|format(p.price) }}</div>
                    </div>
                </div>
                <a class="button" href="{{ url_for('payment_page', plan_id=p.id) }}">
                    Buy Now — ₹{{ p.price }}
                </a>
            </div>
        </article>
        {% endfor %}
    </section>

    <footer class="footer">© {{ site_name }}. All rights reserved.</footer>
</div>

<a class="support-button" href="{{ support_url }}" target="_blank" rel="noopener noreferrer">
    ✈ 24/7 Support
</a>
</body>
</html>
"""


PAYMENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Payment | {{ p.name }}</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="container">
    <header class="navbar">
        <div class="nav-left">
            <img class="logo" src="{{ logo_url }}" alt="Logo">
            <div>
                <div class="brand">SOCIAL <span>FLUX</span></div>
                <div class="tagline">PAYMENT CHECKOUT</div>
            </div>
        </div>
    </header>

    <main class="payment-panel">
        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ 'error' if category == 'error' else 'success' }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <img class="payment-image" src="{{ p.image }}" alt="{{ p.name }}">
        <div class="plan-label">YOUR SELECTED PLAN</div>
        <h1>{{ p.name }}</h1>
        <p class="muted">{{ p.description }}</p>

        <section class="order-summary">
            <div class="total-row">
                <div>
                    <strong>{{ p.name }}</strong>
                    <div class="muted">{{ p.videos }}</div>
                </div>
                <div class="total-price">₹{{ "%.2f"|format(p.price) }}</div>
            </div>
        </section>

        <h2>1. Pay with UPI App</h2>
        <p class="muted">Click an app below to pay the exact amount instantly.</p>

        <div class="app-grid">
            <a class="app-button" href="{{ upi_links['upi'] }}">
                <span class="app-icon">🟢</span>
                <span class="app-name">Other UPI Apps</span>
            </a>
            <a class="app-button" href="{{ upi_links['gpay'] }}">
                <span class="app-icon">🔵</span>
                <span class="app-name">Google Pay</span>
            </a>
            <a class="app-button" href="{{ upi_links['phonepe'] }}">
                <span class="app-icon">🟣</span>
                <span class="app-name">PhonePe</span>
            </a>
            <a class="app-button" href="{{ upi_links['paytm'] }}">
                <span class="app-icon">🔷</span>
                <span class="app-name">Paytm</span>
            </a>
            <a class="app-button" href="{{ upi_links['bhim'] }}">
                <span class="app-icon">🇮🇳</span>
                <span class="app-name">BHIM UPI</span>
            </a>
        </div>

        <h2>2. Scan to Pay</h2>
        <p class="muted">Scan the QR code below using any UPI scanner app.</p>
        <div class="qr-box">
            <img class="qr-image" src="{{ url_for('payment_qr', plan_id=p.id) }}" alt="UPI QR Code">
        </div>
        <p class="muted" style="text-align: center; font-size: 12px; margin-top: -10px;">Payee UPI ID: <strong>{{ upi_id }}</strong></p>

        <h2>3. Submit UTR / Reference Number</h2>
        <p class="muted">After completing the payment, enter your 12-digit UTR transaction reference number below so we can verify and grant access.</p>

        <form action="{{ url_for('submit_utr', plan_id=p.id) }}" method="POST">
            <input type="text" name="utr" class="input" placeholder="Enter 12-digit UTR / Reference Number" required>
            <button type="submit" class="button">Submit UTR for Verification</button>
        </form>

        <a class="button secondary" href="{{ url_for('index') }}" style="margin-top: 20px;">
            ← Back to Plans
        </a>
    </main>

    <footer class="footer">© {{ site_name }}. All rights reserved.</footer>
</div>

<a class="support-button" href="{{ support_url }}" target="_blank" rel="noopener noreferrer">
    ✈ 24/7 Support
</a>
</body>
</html>
"""


ADMIN_LOGIN_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Login | {{ site_name }}</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="container" style="max-width: 450px; margin-top: 60px;">
    <div class="payment-panel">
        <h1 style="text-align: center;">Admin Login</h1>
        <p class="muted" style="text-align: center; margin-bottom: 25px;">Enter credentials to access your dashboard.</p>

        {% with messages = get_flashed_messages(with_categories=true) %}
          {% if messages %}
            {% for category, message in messages %}
              <div class="alert alert-{{ 'error' if category == 'error' else 'success' }}">{{ message }}</div>
            {% endfor %}
          {% endif %}
        {% endwith %}

        <form method="POST">
            <label class="muted" style="display:block; margin-bottom: 5px;">Username</label>
            <input type="text" name="username" class="input" required>

            <label class="muted" style="display:block; margin-bottom: 5px;">Password</label>
            <input type="password" name="password" class="input" required>

            <button type="submit" class="button" style="margin-top: 15px;">Login</button>
        </form>

        <div style="text-align: center; margin-top: 20px;">
            <a href="{{ url_for('index') }}" class="muted" style="text-decoration: underline; font-size: 13px;">← Return to Website</a>
        </div>
    </div>
</div>
</body>
</html>
"""


ADMIN_DASHBOARD_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Admin Dashboard | {{ site_name }}</title>
    <style>{{ css }}</style>
</head>
<body>
<div class="container">
    <header class="navbar">
        <div class="nav-left">
            <div>
                <div class="brand">ADMIN <span>DASHBOARD</span></div>
                <div class="tagline">MANAGE PAYMENTS & UPI SETTINGS</div>
            </div>
        </div>
        <div>
            <a href="{{ url_for('admin_logout') }}" class="button secondary" style="min-height: 38px; padding: 8px 15px; font-size: 12px;">Logout</a>
        </div>
    </header>

    {% with messages = get_flashed_messages(with_categories=true) %}
      {% if messages %}
        {% for category, message in messages %}
          <div class="alert alert-{{ 'error' if category == 'error' else 'success' }}">{{ message }}</div>
        {% endfor %}
      {% endif %}
    {% endwith %}

    <div class="payment-panel" style="max-width: 100%; margin-bottom: 30px;">
        <h2>⚙ Update UPI ID Settings</h2>
        <p class="muted">Change your active UPI ID here. This automatically updates all QR codes and checkout buttons instantly.</p>
        
        <form action="{{ url_for('admin_update_upi') }}" method="POST" style="display: flex; gap: 10px; flex-wrap: wrap; margin-top: 15px;">
            <input type="text" name="upi_id" class="input" value="{{ current_upi }}" placeholder="Enter new UPI ID (e.g. yourname@ybl)" style="flex: 1; min-width: 250px; margin: 0;" required>
            <input type="text" name="payee_name" class="input" value="{{ current_payee }}" placeholder="Payee Name" style="width: 200px; margin: 0;" required>
            <button type="submit" class="button" style="width: auto; padding: 0 25px;">Save UPI</button>
        </form>
    </div>

    <div class="payment-panel" style="max-width: 100%;">
        <h2>💳 Customer Payments & UTRs</h2>
        <p class="muted">Review submitted UTR transaction references from customers.</p>

        {% if payments %}
        <div style="overflow-x: auto;">
            <table class="admin-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Plan</th>
                        <th>Amount</th>
                        <th>UTR / Ref</th>
                        <th>Status</th>
                        <th>Time</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    {% for p in payments %}
                    <tr>
                        <td>#{{ p[0] }}</td>
                        <td><strong>{{ p[2] }}</strong></td>
                        <td>₹{{ "%.2f"|format(p[3]) }}</td>
                        <td><code>{{ p[4] }}</code></td>
                        <td>
                            {% if p[5] == 'VERIFIED' %}
                                <span class="badge-success">VERIFIED</span>
                            {% else %}
                                <span class="badge-pending">PENDING</span>
                            {% endif %}
                        </td>
                        <td class="muted" style="font-size: 11px;">{{ p[6] }}</td>
                        <td>
                            {% if p[5] != 'VERIFIED' %}
                            <a href="{{ url_for('admin_verify_payment', payment_id=p[0]) }}" class="button" style="min-height: 32px; padding: 5px 12px; font-size: 12px; width: auto;">Verify</a>
                            {% else %}
                            <span class="muted" style="font-size: 12px;">Done</span>
                            {% endif %}
                        </td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
        {% else %}
        <p class="muted" style="text-align: center; padding: 30px;">No payments submitted yet.</p>
        {% endif %}
    </div>

    <div style="text-align: center; margin-top: 20px;">
        <a href="{{ url_for('index') }}" class="muted" style="text-decoration: underline; font-size: 13px;">← Return to Main Website</a>
    </div>

    <footer class="footer">© {{ site_name }}. All rights reserved.</footer>
</div>
</body>
</html>
"""


# =====================================================
# 7. FLASK ROUTES
# =====================================================

@app.route("/")
def index():
    return render_template_string(
        HOME_HTML,
        site_name=SITE_NAME,
        logo_url=LOGO_URL,
        plans=PLANS,
        support_url=TELEGRAM_SUPPORT,
        css=CSS
    )


@app.route("/pay/<int:plan_id>")
def payment_page(plan_id):
    p = get_plan(plan_id)
    if not p:
        abort(404)

    current_upi = get_setting("upi_id", DEFAULT_UPI_ID)
    current_payee = get_setting("payee_name", DEFAULT_PAYEE_NAME)

    upi_params = {
        "pa": current_upi,
        "pn": current_payee,
        "am": f"{p['price']:.2f}",
        "cu": "INR",
        "tn": f"Payment for {p['name']}"
    }

    query_string = urlencode(upi_params)

    upi_links = {
        "upi": f"upi://pay?{query_string}",
        "gpay": f"tez://upi/pay?{query_string}",
        "phonepe": f"phonepe://pay?{query_string}",
        "paytm": f"paytmmp://pay?{query_string}",
        "bhim": f"bhim://upi/pay?{query_string}"
    }

    return render_template_string(
        PAYMENT_HTML,
        p=p,
        logo_url=LOGO_URL,
        site_name=SITE_NAME,
        support_url=TELEGRAM_SUPPORT,
        upi_id=current_upi,
        upi_links=upi_links,
        css=CSS
    )


@app.route("/qr/<int:plan_id>")
def payment_qr(plan_id):
    p = get_plan(plan_id)
    if not p:
        abort(404)

    current_upi = get_setting("upi_id", DEFAULT_UPI_ID)
    current_payee = get_setting("payee_name", DEFAULT_PAYEE_NAME)

    upi_str = (
        f"upi://pay?pa={current_upi}&pn={current_payee}"
        f"&am={p['price']:.2f}&cu=INR&tn=Payment%20for%20{p['name']}"
    )

    qr = qrcode.QRCode(box_size=10, border=2)
    qr.add_data(upi_str)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    buffer.seek(0)

    return Response(buffer.getvalue(), mimetype="image/png")


@app.route("/submit_utr/<int:plan_id>", methods=["POST"])
def submit_utr(plan_id):
    p = get_plan(plan_id)
    if not p:
        abort(404)

    utr = request.form.get("utr", "").strip()
    if not utr:
        flash("Please enter a valid UTR / Transaction Reference Number.", "error")
        return redirect(url_for("payment_page", plan_id=plan_id))

    try:
        with sqlite3.connect(DB_PATH) as conn:
            conn.execute("""
                INSERT INTO payments (plan_id, plan_name, amount, utr, status)
                VALUES (?, ?, ?, ?, 'PENDING')
            """, (p["id"], p["name"], p["price"], utr))
            conn.commit()
        flash("UTR submitted successfully! Your payment is pending verification.", "success")
    except sqlite3.IntegrityError:
        flash("This UTR number has already been submitted. Please check or contact support.", "error")

    return redirect(url_for("payment_page", plan_id=plan_id))


# =====================================================
# 8. ADMIN ROUTES
# =====================================================

@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == ADMIN_USER and password == ADMIN_PASS:
            session["admin_logged_in"] = True
            return redirect(url_for("admin_dashboard"))
        else:
            flash("Invalid username or password.", "error")

    return render_template_string(ADMIN_LOGIN_HTML, site_name=SITE_NAME, css=CSS)


@app.route("/admin/dashboard")
def admin_dashboard():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    current_upi = get_setting("upi_id", DEFAULT_UPI_ID)
    current_payee = get_setting("payee_name", DEFAULT_PAYEE_NAME)

    with sqlite3.connect(DB_PATH) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, plan_id, plan_name, amount, utr, status, created_at FROM payments ORDER BY id DESC")
        payments = cursor.fetchall()

    return render_template_string(
        ADMIN_DASHBOARD_HTML,
        site_name=SITE_NAME,
        current_upi=current_upi,
        current_payee=current_payee,
        payments=payments,
        css=CSS
    )


@app.route("/admin/update_upi", methods=["POST"])
def admin_update_upi():
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    new_upi = request.form.get("upi_id", "").strip()
    new_payee = request.form.get("payee_name", "").strip()

    if new_upi:
        set_setting("upi_id", new_upi)
    if new_payee:
        set_setting("payee_name", new_payee)

    flash("UPI settings updated successfully!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/verify/<int:payment_id>")
def admin_verify_payment(payment_id):
    if not session.get("admin_logged_in"):
        return redirect(url_for("admin_login"))

    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("UPDATE payments SET status='VERIFIED' WHERE id=?", (payment_id,))
        conn.commit()

    flash(f"Payment #{payment_id} marked as Verified!", "success")
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("admin_logged_in", None)
    flash("Logged out successfully.", "success")
    return redirect(url_for("admin_login"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
