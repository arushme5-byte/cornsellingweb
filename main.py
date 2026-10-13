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
    Response
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

# =====================================================
# 2. WEBSITE SETTINGS
# =====================================================

SITE_NAME = "SOCIAL FLUX"

# Change this URL to change the circular heading logo.
LOGO_URL = (
    "https://placehold.co/300x300/24113f/ffffff"
    "?text=FLUX"
)

# Your payment details
UPI_ID = os.environ.get(
    "UPI_ID",
    "haaland78@ybl"
)

PAYEE_NAME = os.environ.get(
    "PAYEE_NAME",
    "Social Flux"
)

# Replace with your actual Telegram support URL.
TELEGRAM_SUPPORT = "https://t.me/YOUR_SUPPORT_USERNAME"

# =====================================================
# 3. EDIT YOUR PLANS HERE
# =====================================================
#
# Change image, caption, name and price here.
# All 8 plans are editable from this single section.
#
# Prices below are examples. Replace them with yours.
# =====================================================

PLANS = [
    {
        "id": 1,
        "name": "PLAN 1",
        "price": 99,
        "image": "https://placehold.co/900x500/21113f/ffffff?text=PLAN+1",
        "caption": "Your first course plan. Add your course details here.",
        "videos": "10+ Videos",
        "description": (
            "Access course lessons and learning material. "
            "Replace this description with your actual course details."
        )
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
    """Return a plan using its ID."""
    return next(
        (plan for plan in PLANS if plan["id"] == plan_id),
        None
    )


# =====================================================
# 4. DATABASE
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


init_database()


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

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    color: var(--text);
    background:
        radial-gradient(
            ellipse at top,
            #211037 0%,
            var(--bg) 55%
        );
    font-family: Arial, Helvetica, sans-serif;
    min-height: 100vh;
}

a {
    color: inherit;
}

.container {
    width: min(1120px, 100%);
    margin: auto;
    padding: 22px;
}

.navbar {
    display: flex;
    align-items: center;
    gap: 13px;
    padding: 8px 0 28px;
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

.brand span {
    color: var(--purple-light);
}

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
    background: linear-gradient(
        90deg,
        #c5a4ff,
        #9956ff,
        #e5ccff
    );
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
    background: linear-gradient(
        150deg,
        #1a1228,
        #100c19
    );
    border: 1px solid var(--border);
    border-radius: 19px;
    overflow: hidden;
    transition:
        transform .25s ease,
        border-color .25s ease,
        box-shadow .25s ease;
    animation: fadeUp .6s ease both;
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

.plan-content {
    padding: 20px;
}

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

.price-label {
    color: var(--muted);
    font-size: 12px;
}

.price {
    font-size: 27px;
    font-weight: 900;
    margin-top: 4px;
}

.button {
    display: flex;
    justify-content: center;
    align-items: center;
    width: 100%;
    min-height: 48px;
    border: 0;
    border-radius: 11px;
    background: linear-gradient(
        100deg,
        #7541d8,
        #a75bff
    );
    color: white;
    text-decoration: none;
    font-weight: 800;
    font-size: 14px;
    padding: 13px 15px;
    cursor: pointer;
    transition:
        transform .2s ease,
        filter .2s ease;
}

.button:hover {
    filter: brightness(1.13);
    transform: translateY(-2px);
}

.button:active {
    transform: scale(.98);
}

.button.secondary {
    background: #241a32;
    border: 1px solid #4c3765;
}

.payment-panel {
    max-width: 650px;
    margin: 12px auto 35px;
    padding: 23px;
    border-radius: 20px;
    border: 1px solid var(--border);
    background: #151020;
    animation: fadeUp .45s ease both;
}

.payment-image {
    width: 100%;
    max-height: 260px;
    object-fit: cover;
    border-radius: 13px;
    margin-bottom: 18px;
}

.payment-panel h1 {
    font-size: 28px;
    margin: 7px 0 12px;
}

.payment-panel h2 {
    font-size: 19px;
    margin-top: 27px;
}

.muted {
    color: var(--muted);
    line-height: 1.7;
    font-size: 14px;
    overflow-wrap: anywhere;
}

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

.total-price {
    font-size: 26px;
    font-weight: 900;
    color: var(--purple-light);
}

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

.app-button:hover {
    background: #342049;
    transform: translateY(-2px);
}

.app-icon {
    display: block;
    font-size: 25px;
    margin-bottom: 8px;
}

.app-name {
    font-size: 13px;
    font-weight: bold;
}

.qr-box {
    padding: 18px;
    background: white;
    border-radius: 15px;
    width: fit-content;
    max-width: 100%;
    margin: 18px auto;
    text-align: center;
}

.qr-image {
    display: block;
    width: min(260px, 65vw);
    height: auto;
}

.upi-id {
    overflow-wrap: anywhere;
    text-align: center;
    color: var(--purple-light);
    font-weight: bold;
}

.form-field {
    display: block;
    font-size: 13px;
    margin-bottom: 7px;
}

.input {
    width: 100%;
    min-height: 48px;
    padding: 13px;
    color: white;
    background: #0d0915;
    border: 1px solid #49345d;
    border-radius: 10px;
    outline: none;
    margin-bottom: 13px;
    font-size: 15px;
}

.input:focus {
    border-color: var(--purple);
    box-shadow: 0 0 0 3px #9b5cff20;
}

.notice {
    font-size: 12px;
    color: var(--muted);
    line-height: 1.7;
    margin-top: 15px;
}

.notice-box {
    padding: 14px;
    border-radius: 10px;
    background: #21182e;
    border: 1px solid #49345d;
    color: #d6c7e8;
    font-size: 13px;
    line-height: 1.7;
    margin: 14px 0;
}

.status {
    display: inline-block;
    color: #ffe08a;
    background: #3b2b13;
    border-radius: 7px;
    padding: 8px 12px;
    font-size: 12px;
    font-weight: bold;
}

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

.footer {
    text-align: center;
    padding: 35px 10px;
    color: var(--muted);
    font-size: 12px;
}

@keyframes fadeUp {
    from {
        opacity: 0;
        transform: translateY(12px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

@media (max-width: 650px) {
    .container {
        padding: 16px;
    }

    .plans-grid {
        grid-template-columns: 1fr;
        gap: 17px;
    }

    .plan-content {
        padding: 17px;
    }

    .hero {
        padding-top: 15px;
    }

    .payment-panel {
        padding: 17px;
    }

    .payment-panel h1 {
        font-size: 24px;
    }

    .support-button {
        right: 12px;
        bottom: 12px;
    }
}

@media (prefers-reduced-motion: reduce) {
    *,
    *::before,
    *::after {
        animation-duration: .01ms !important;
        transition-duration: .01ms !important;
        scroll-behavior: auto !important;
    }
}
"""


# =====================================================
# 6. HOMEPAGE HTML
# =====================================================

HOME_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <meta name="theme-color" content="#090611">

    <title>{{ site_name }} | Course Plans</title>

    <style>{{ css }}</style>
</head>

<body>

<div class="container">

    <header class="navbar">

        <img
            class="logo"
            src="{{ logo_url }}"
            alt="Website Logo"
        >

        <div>
            <div class="brand">
                SOCIAL <span>FLUX</span>
            </div>

            <div class="tagline">
                YOUR LEARNING STARTS HERE
            </div>
        </div>

    </header>


    <section class="hero">

        <div class="badge">
            ✦ PREMIUM COURSE COLLECTION
        </div>

        <h1>
            Choose Your<br>
            <span class="gradient-text">
                Perfect Plan
            </span>
        </h1>

        <p>
            Explore our available course plans.
            Choose the plan you need and continue
            to the secure payment instructions.
        </p>

    </section>


    <h2 class="section-title">
        Available Plans
    </h2>


    <section class="plans-grid">

        {% for p in plans %}

        <article class="plan-card">

            <!-- PLAN IMAGE -->
            <img
                class="plan-image"
                src="{{ p.image }}"
                alt="{{ p.name }}"
                loading="lazy"
            >

            <div class="plan-content">

                <div class="plan-label">
                    PREMIUM COURSE
                </div>

                <!-- PLAN HEADING -->
                <h2 class="plan-name">
                    {{ p.name }}
                </h2>

                <!-- CAPTION -->
                <p class="caption">
                    {{ p.caption }}
                </p>

                <!-- VIDEO COUNT -->
                <div class="video-count">
                    ▶ {{ p.videos }}
                </div>

                <div class="price-row">

                    <div>
                        <div class="price-label">
                            PLAN PRICE
                        </div>

                        <div class="price">
                            ₹{{ "%.2f"|format(p.price) }}
                        </div>
                    </div>

                </div>

                <!-- WORKING BUY BUTTON -->
                <a
                    class="button"
                    href="{{ url_for(
                        'payment_page',
                        plan_id=p.id
                    ) }}"
                >
                    Buy Now — ₹{{ p.price }}
                </a>

            </div>

        </article>

        {% endfor %}

    </section>


    <footer class="footer">
        © {{ site_name }}. All rights reserved.
    </footer>

</div>


<a
    class="support-button"
    href="{{ support_url }}"
    target="_blank"
    rel="noopener noreferrer"
>
    ✈ 24/7 Support
</a>

</body>
</html>
"""


# =====================================================
# 7. PAYMENT PAGE HTML
# =====================================================

PAYMENT_HTML = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">

    <meta name="viewport"
          content="width=device-width, initial-scale=1">

    <meta name="theme-color" content="#090611">

    <title>Payment | {{ p.name }}</title>

    <style>{{ css }}</style>
</head>

<body>

<div class="container">

    <header class="navbar">

        <img
            class="logo"
            src="{{ logo_url }}"
            alt="Website Logo"
        >

        <div>
            <div class="brand">
                SOCIAL <span>FLUX</span>
            </div>

            <div class="tagline">
                PAYMENT CHECKOUT
            </div>
        </div>

    </header>


    <main class="payment-panel">

        <!-- SELECTED PLAN IMAGE -->
        <img
            class="payment-image"
            src="{{ p.image }}"
            alt="{{ p.name }}"
        >


        <div class="plan-label">
            YOUR SELECTED PLAN
        </div>

        <h1>{{ p.name }}</h1>

        <p class="muted">
            {{ p.description }}
        </p>


        <!-- ORDER SUMMARY -->
        <section class="order-summary">

            <div class="total-row">

                <div>
                    <strong>{{ p.name }}</strong>

                    <div class="muted">
                        {{ p.videos }}
                    </div>
                </div>

                <div class="total-price">
                    ₹{{ "%.2f"|format(p.price) }}
                </div>

            </div>

        </section>


        <!-- UPI APP SECTION -->
        <h2>1. Pay with UPI App</h2>

        <p class="muted">
            Choose an app below. On compatible mobile
            devices, it will try to open your UPI app.
            Check the receiver and amount before paying.
        </p>


        <div class="app-grid">

            <a
                class="app-button"
                href="{{ upi_links['upi'] }}"
            >
                <span class="app-icon">🟢</span>
                <span class="app-name">
                    Other UPI Apps
                </span>
            </a>


            <a
                class="app-button"
                href="{{ upi_links['gpay'] }}"
            >
                <span class="app-icon">🔵</span>
                <span class="app-name">
                    Google Pay
                </span>
            </a>


            <a
                class="app-button"
                href="{{ upi_links['phonepe'] }}"
            >
                <span class="app-icon">🟣</span>
                <span class="app-name">
                    PhonePe
                </span>
            </a>


            <a
                class="app-button"
                href="{{ upi_links['paytm'] }}"
            >
                <span class="app-icon">🔷</span>
                <span class="app-name">
                    Paytm
                </span>
            </a>


            <a
                class="app-button"
                href="{{ upi_links['bhim'] }}"
            >
                <span class="app-icon">🇮🇳</span>
                <span class="app-name">
                    BHIM UPI
                </span>
            </a>

        </div>


        <!-- QR CODE SECTION -->
        <h2>2. Scan to Pay</h2>

        <p class="muted">
            Open a UPI app on another phone and scan
            the QR code below.
        </p>


        <div class="qr-box">

            <img
                class="qr-image"
                src="{{ url_for(
                    'payment_qr',
                    plan_id=p.id
                ) }}"
                alt="UPI Payment QR Code"
            >

        </d
