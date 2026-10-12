import os
import json
import secrets
import sqlite3
from flask import (
    Flask, render_template_string, request,
    redirect, url_for, flash, session
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

DB_PATH = os.environ.get("DB_PATH", "courses.db")

# ==========================================
# EDIT YOUR PLANS HERE
# ==========================================

PLANS = [
    {
        "id": 1,
        "name": "Starter Course",
        "videos": 12,
        "price": 199,
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=700",
        "description": "Start learning with this beginner-friendly course."
    },
    {
        "id": 2,
        "name": "Basic Course",
        "videos": 18,
        "price": 299,
        "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=700",
        "description": "Learn useful skills with practical lessons."
    },
    {
        "id": 3,
        "name": "Pro Course",
        "videos": 25,
        "price": 399,
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=700",
        "description": "Take your skills to the next level."
    },
    {
        "id": 4,
        "name": "Premium Course",
        "videos": 30,
        "price": 499,
        "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=700",
        "description": "Explore detailed lessons and examples."
    },
    {
        "id": 5,
        "name": "Master Course",
        "videos": 40,
        "price": 599,
        "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=700",
        "description": "Build confidence with a complete learning plan."
    },
    {
        "id": 6,
        "name": "Advanced Course",
        "videos": 50,
        "price": 699,
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=700",
        "description": "Learn advanced techniques step by step."
    },
    {
        "id": 7,
        "name": "Ultimate Course",
        "videos": 65,
        "price": 899,
        "image": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=700",
        "description": "A comprehensive collection of learning material."
    },
    {
        "id": 8,
        "name": "Lifetime Access",
        "videos": 100,
        "price": 1299,
        "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=700",
        "description": "Access the complete collection of course lessons."
    }
]

# ==========================================
# EDIT YOUR BRAND AND PAYMENT DETAILS
# ==========================================

BRAND_NAME = "FLUX ACADEMY"

# Replace with your actual Telegram support username.
TELEGRAM_SUPPORT = "https://t.me/YOUR_SUPPORT_USERNAME"

# Add your actual payment QR image URL here.
# Example: https://your-image-host.com/payment-qr.png
PAYMENT_QR_URL = ""

# Optional UPI ID displayed below the QR.
UPI_ID = "YOUR-UPI-ID@bank"

PAGE = r"""
<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#170b2d">
<title>{{ brand }} | Course Store</title>

<style>
* {
    box-sizing: border-box;
    margin: 0;
    padding: 0;
}

:root {
    --purple: #a855f7;
    --pink: #e879f9;
    --bg: #10091f;
    --card: rgba(255,255,255,.065);
    --muted: #c4b5d8;
}

body {
    min-height: 100vh;
    color: white;
    font-family: Inter, system-ui, Arial, sans-serif;
    background:
        radial-gradient(ellipse at 10% 0%, #55228c 0%, transparent 38%),
        radial-gradient(ellipse at 100% 30%, #32115b 0%, transparent 35%),
        linear-gradient(145deg, #10091f, #1b0c30 55%, #10091f);
}

button, input {
    font: inherit;
}

.container {
    width: min(1120px, 92%);
    margin: auto;
}

header {
    text-align: center;
    padding: 36px 0 25px;
}

.logo {
    width: 76px;
    height: 76px;
    border-radius: 50%;
    margin: 0 auto 12px;
    display: grid;
    place-items: center;
    font-size: 29px;
    font-weight: 900;
    color: white;
    background: linear-gradient(135deg, #c084fc, #7c3aed, #4c1d95);
    border: 2px solid rgba(255,255,255,.65);
    box-shadow: 0 0 35px #a855f755;
}

.brand {
    font-size: 13px;
    letter-spacing: 4px;
    color: #d8b4fe;
    font-weight: 800;
}

h1 {
    font-size: clamp(30px, 5vw, 49px);
    margin: 24px 0 10px;
    letter-spacing: -1px;
}

.gradient-text {
    background: linear-gradient(90deg, #e9d5ff, #c084fc, #f0abfc);
    -webkit-background-clip: text;
    background-clip: text;
    color: transparent;
}

.subtitle {
    color: var(--muted);
    line-height: 1.7;
    font-size: 14px;
}

.badge {
    display: inline-block;
    margin-top: 18px;
    padding: 8px 14px;
    border-radius: 30px;
    background: #a855f71c;
    border: 1px solid #a855f755;
    color: #e9d5ff;
    font-size: 12px;
}

.grid {
    display: grid;
    grid-template-columns: repeat(4, minmax(0, 1fr));
    gap: 20px;
    padding: 22px 0 55px;
}

.card {
    overflow: hidden;
    border-radius: 19px;
    background: var(--card);
    border: 1px solid rgba(216,180,254,.17);
    box-shadow: 0 10px 35px #00000025;
    backdrop-filter: blur(12px);
    transition: transform .2s, border-color .2s;
}

.card:hover {
    transform: translateY(-5px);
    border-color: #c084fcaa;
}

.cover {
    width: 100%;
    height: 150px;
    object-fit: cover;
    display: block;
    background: #32115b;
}

.card-content {
    padding: 16px;
}

.plan-number {
    font-size: 10px;
    letter-spacing: 2px;
    color: #d8b4fe;
    font-weight: 800;
}

h2 {
    font-size: 17px;
    margin: 8px 0 10px;
}

.description {
    color: #c4b5d8;
    font-size: 12px;
    line-height: 1.6;
    min-height: 39px;
}

.videos {
    margin: 14px 0;
    color: #e9d5ff;
    font-size: 13px;
}

.buy-btn {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 8px;
    width: 100%;
    border: 0;
    border-radius: 11px;
    padding: 13px 12px;
    color: white;
    cursor: pointer;
    text-decoration: none;
    font-size: 12px;
    font-weight: 800;
    background: linear-gradient(110deg, #9333ea, #c026d3);
    box-shadow: 0 5px 20px #9333ea30;
}

.buy-btn:hover {
    filter: brightness(1.13);
}

.price {
    font-size: 16px;
}

footer {
    text-align: center;
    padding: 20px 0 35px;
    font-size: 12px;
    color: #a99abf;
}

/* Floating support button */

.support {
    position: fixed;
    right: 18px;
    bottom: 20px;
    z-index: 20;
    display: flex;
    align-items: center;
    gap: 9px;
    padding: 14px 18px;
    color: white;
    text-decoration: none;
    font-weight: 800;
    font-size: 13px;
    background: linear-gradient(120deg, #7c3aed, #a855f7);
    border: 1px solid #e9d5ff66;
    border-radius: 40px;
    box-shadow: 0 8px 35px #7c3aed70;
}

/* Payment modal */

.modal {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 50;
    background: #080410d9;
    backdrop-filter: blur(8px);
    overflow-y: auto;
    padding: 24px 12px;
}

.modal-box {
    width: min(430px, 100%);
    margin: 20px auto;
    padding: 25px;
    border-radius: 23px;
    background: linear-gradient(150deg, #28113f, #160b25);
    border: 1px solid #c084fc55;
    box-shadow: 0 20px 80px #0008;
    text-align: center;
    position: relative;
}

.close {
    position: absolute;
    right: 16px;
    top: 12px;
    border: 0;
    background: transparent;
    color: white;
    font-size: 27px;
    cursor: pointer;
}

.modal-box h2 {
    font-size: 24px;
    margin: 14px 0 6px;
}

.modal-subtitle {
    font-size: 13px;
    color: #c4b5d8;
    margin-bottom: 20px;
}

.amount {
    font-size: 38px;
    font-weight: 900;
    color: #e9d5ff;
    margin: 8px 0 20px;
}

.qr {
    display: block;
    width: 190px;
    height: 190px;
    margin: 0 auto 14px;
    padding: 8px;
    background: white;
    border-radius: 12px;
    object-fit: contain;
}

.upi {
    font-size: 12px;
    color: #d8b4fe;
    margin-bottom: 22px;
    overflow-wrap: anywhere;
}

.form-label {
    display: block;
    text-align: left;
    font-size: 13px;
    font-weight: 700;
    margin: 14px 0 9px;
}

input {
    width: 100%;
    padding: 14px;
    background: #0f071b;
    color: white;
    border: 1px solid #7c3aed80;
    border-radius: 10px;
    outline: none;
}

input:focus {
    border-color: #c084fc;
}

.submit-btn {
    width: 100%;
    margin-top: 14px;
    border: 0;
    padding: 14px;
    border-radius: 10px;
    background: linear-gradient(110deg, #9333ea, #c026d3);
    color: white;
    font-weight: 900;
    cursor: pointer;
}

.notice {
    color: #c4b5d8;
    font-size: 11px;
    line-height: 1.6;
    margin-top: 14px;
}

.flash {
    margin: 12px auto;
    padding: 12px;
    border-radius: 10px;
    background: #3b1557;
    font-size: 13px;
}

.success {
    text-align: center;
    padding: 45px 10px;
}

.tick {
    width: 76px;
    height: 76px;
    margin: 0 auto 18px;
    border-radius: 50%;
    background: #16a34a22;
    border: 2px solid #4ade80;
    color: #4ade80;
    font-size: 43px;
    display: grid;
    place-items: center;
}

@media(max-width: 900px) {
    .grid {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 14px;
    }

    .cover {
        height: 125px;
    }

    .card-content {
        padding: 13px;
    }
}

@media(max-width: 360px) {
    .grid {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>
<div class="container">
    <header>
        <div class="logo">F</div>
        <div class="brand">{{ brand }}</div>
        <h1>Unlock Your <span class="gradient-text">Potential</span></h1>
        <p class="subtitle">
            Choose your plan. Learn new skills. Start today.
        </p>
        <div class="badge">✦ PREMIUM LEARNING EXPERIENCE ✦</div>
    </header>

    {% with messages = get_flashed_messages() %}
        {% if messages %}
            {% for message in messages %}
                <div class="flash">{{ message }}</div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% if success %}
        <div class="success">
            <div class="tick">✓</div>
            <h2>Submitted Successfully!</h2>
            <p class="subtitle" style="margin-top:12px">
                Your payment reference has been submitted for review.
                Course access is not automatic until payment is verified.
            </p>
            <a class="buy-btn" href="{{ url_for('home') }}"
               style="margin:24px auto;max-width:230px;justify-content:center">
                BACK TO PLANS
            </a>
        </div>
    {% else %}
        <main class="grid">
        {% for plan in plans %}
            <article class="card">
                <img class="cover"
                     src="{{ plan.image }}"
                     alt="{{ plan.name }}"
                     loading="lazy"
                     onerror="this.src='https://placehold.co/700x400/32115b/ffffff?text=Course+Image'">

                <div class="card-content">
                    <div class="plan-number">PLAN {{ "%02d"|format(plan.id) }}</div>
                    <h2>{{ plan.name }}</h2>
                    <p class="description">{{ plan.description }}</p>
                    <div class="videos">▶ {{ plan.videos }} Videos</div>

                    <button class="buy-btn"
                        onclick="openPayment({{ plan.id }}, {{ plan.price }}, {{ plan.name|tojson }})">
                        <span>UNLOCK ACCESS</span>
                        <span class="price">₹{{ plan.price }}</span>
                    </button>
                </div>
            </article>
        {% endfor %}
        </main>
    {% endif %}

    <footer>© {{ brand }} · Learn at your own pace</footer>
</div>

<a class="support" href="{{ support }}" target="_blank"
   rel="noopener noreferrer">
    <span>✈</span> 24/7 SUPPORT
</a>

<div class="modal" id="paymentModal" role="dialog"
     aria-modal="true" aria-labelledby="paymentTitle">
    <div class="modal-box">
        <button class="close" onclick="closePayment()" aria-label="Close">×</button>

        <div class="logo" style="width:55px;height:55px;font-size:22px">
            F
        </div>

        <h2 id="paymentTitle">Complete Your Payment</h2>
        <p class="modal-subtitle" id="selectedPlan">Selected course</p>
        <div class="amount" id="selectedAmount">₹199</div>

        {% if qr_url %}
            <img class="qr" src="{{ qr_url }}" alt="Payment QR code">
        {% else %}
            <div class="qr" style="color:#5b2188;font-size:13px;display:grid;place-items:center">
                Add your payment QR URL in app.py
            </div>
        {% endif %}

        <p class="upi">UPI: {{ upi }}</p>
        <p class="modal-subtitle">
            Scan the QR code and complete the payment.
        </p>

        <form action="{{ url_for('submit_payment') }}" method="POST">
            <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
            <input type="hidden" name="plan_id" id="planId">

            <label class="form-label" for="utr">
                Pay and enter UTR in the box
            </label>

            <input type="text" id="utr" name="utr"
                   placeholder="Enter UTR / Transaction ID"
                   minlength="6" maxlength="100"
                   autocomplete="off" required>

            <button type="submit" class="submit-btn">
                SUBMIT PAYMENT ✓
            </button>
        </form>

        <p class="notice">
            Submitting a UTR does not confirm payment. Your payment
            must be verified before course access is provided.
        </p>
    </div>
</div>

<script>
const modal = document.getElementById("paymentModal");

function openPayment(id, price, name) {
    document.getElementById("planId").value = id;
    document.getElementById("selectedAmount").textContent = "₹" + price;
    document.getElementById("selectedPlan").textContent = name;
    document.getElementById("utr").value = "";
    modal.style.display = "block";
    document.body.style.overflow = "hidden";
}

function closePayment() {
    modal.style.display = "none";
    document.body.style.overflow = "";
}

modal.addEventListener("click", function(event) {
    if (event.target === modal) closePayment();
});

document.addEventListener("keydown", function(event) {
    if (event.key === "Escape") closePayment();
});
</script>
</body>
</html>
"""


def get_db():
    conn = sqlite3.connect(DB_PATH, timeout=20)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    with get_db() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS payment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                plan_name TEXT NOT NULL,
                amount INTEGER NOT NULL,
                utr TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                status TEXT NOT NULL DEFAULT 'PENDING'
            )
        """)


@app.before_request
def prepare_session():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)


@app.route("/")
def home():
    return render_template_string(
        PAGE,
        brand=BRAND_NAME,
        plans=PLANS,
        support=TELEGRAM_SUPPORT,
        qr_url=PAYMENT_QR_URL,
        upi=UPI_ID,
        success=False,
        csrf_token=session["csrf_token"]
    )


@app.route("/submit-payment", methods=["POST"])
def submit_payment():
    if not secrets.compare_digest(
        request.form.get("csrf_token", ""),
        session.get("csrf_token", "")
    ):
        return "Invalid session. Please reload the page.", 400

    try:
        plan_id = int(request.form.get("plan_id", ""))
    except (TypeError, ValueError):
        return "Invalid plan.", 400

    plan = next((p for p in PLANS if p["id"] == plan_id), None)
    if plan is None:
        return "Plan not found.", 404

    utr = request.form.get("utr", "").strip()

    if not 6 <= len(utr) <= 100:
        flash("Please enter a valid UTR / transaction reference.")
        return redirect(url_for("home"))

    if any(ord(char) < 32 for char in utr):
        flash("Invalid UTR format.")
        return redirect(url_for("home"))

    # A UTR is only a claim until the payment is independently verified.
    # Never unlock a course solely because a form was submitted.
    with get_db() as conn:
        conn.execute("""
            INSERT INTO payment_submissions
            (plan_id, plan_name, amount, utr, status)
            VALUES (?, ?, ?, ?, 'PENDING')
        """, (plan["id"], plan["name"], plan["price"], utr))

    return render_template_string(
        PAGE,
        brand=BRAND_NAME,
        plans=PLANS,
        support=TELEGRAM_SUPPORT,
        qr_url=PAYMENT_QR_URL,
        upi=UPI_ID,
        success=True,
        csrf_token=session["csrf_token"]
    )


@app.route("/health")
def health():
    return {"status": "ok"}


init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
