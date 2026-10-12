import os
import io
import secrets
import sqlite3
from urllib.parse import urlencode

import qrcode
from flask import (
    Flask, Response, abort, flash, redirect, render_template_string,
    request, session, url_for
)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", secrets.token_hex(32))

# Railway: attach a persistent volume and set DB_PATH=/data/courses.db
DB_PATH = os.environ.get("DB_PATH", "courses.db")

# ===================== EDIT THESE SETTINGS =====================
BRAND_NAME = "FLUX ACADEMY"
BRAND_LETTER = "F"
UPI_ID = "haaland78@ybl"
TELEGRAM_SUPPORT = "https://t.me/YOUR_SUPPORT_USERNAME"

# Replace the sample images with your own image URLs whenever you want.
PLANS = [
    {"id": 1, "name": "Starter Course", "videos": 12, "price": 199,
     "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=900",
     "description": "A beginner-friendly collection of lessons."},
    {"id": 2, "name": "Basic Course", "videos": 18, "price": 299,
     "image": "https://images.unsplash.com/photo-1498050108023-c5249f4df085?w=900",
     "description": "Learn useful skills step by step."},
    {"id": 3, "name": "Pro Course", "videos": 25, "price": 399,
     "image": "https://images.unsplash.com/photo-1522202176988-66273c2fd55f?w=900",
     "description": "Practical lessons to grow your skills."},
    {"id": 4, "name": "Premium Course", "videos": 30, "price": 499,
     "image": "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=900",
     "description": "Explore detailed lessons and examples."},
    {"id": 5, "name": "Master Course", "videos": 40, "price": 599,
     "image": "https://images.unsplash.com/photo-1497366754035-f200968a6e72?w=900",
     "description": "A complete plan for focused learning."},
    {"id": 6, "name": "Advanced Course", "videos": 50, "price": 699,
     "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=900",
     "description": "Go deeper with advanced lessons."},
    {"id": 7, "name": "Ultimate Course", "videos": 65, "price": 899,
     "image": "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=900",
     "description": "A broad collection of learning material."},
    {"id": 8, "name": "Lifetime Access", "videos": 100, "price": 1299,
     "image": "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=900",
     "description": "Access the complete course collection."},
]
# ===============================================================

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

def get_stats():
    with get_db() as conn:
        submitted = conn.execute(
            "SELECT COUNT(*) FROM payment_submissions"
        ).fetchone()[0]
        verified = conn.execute(
            "SELECT COUNT(*) FROM payment_submissions WHERE status='VERIFIED'"
        ).fetchone()[0]
    return {
        "total_plans": len(PLANS),
        "submitted_orders": submitted,
        "verified_purchases": verified,
    }

PAGE = r"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#10071f">
<title>{{ brand }} — Premium Courses</title>
<style>
:root{--bg:#10071f;--purple:#a855f7;--pink:#e879f9;--muted:#c7b8db}
*{box-sizing:border-box;margin:0;padding:0}
body{min-height:100vh;color:#fff;font-family:Inter,system-ui,-apple-system,Arial,sans-serif;background:radial-gradient(ellipse at 5% 0%,#57258b 0,transparent 34%),radial-gradient(ellipse at 100% 35%,#35105e 0,transparent 32%),linear-gradient(145deg,#10071f,#1a0b2e 58%,#0d0618)}
button,input{font:inherit}
.wrap{width:min(850px,92%);margin:auto}
header{text-align:center;padding:34px 0 20px}
.logo{width:76px;height:76px;margin:0 auto 12px;border-radius:50%;display:grid;place-items:center;font-size:30px;font-weight:950;background:linear-gradient(135deg,#e9d5ff,#a855f7 50%,#581c87);border:2px solid #ffffffa6;box-shadow:0 0 36px #a855f766}
.brand{letter-spacing:4px;color:#e9d5ff;font-size:13px;font-weight:900}
h1{font-size:clamp(30px,6vw,49px);letter-spacing:-1px;margin:23px 0 10px}
.grad{background:linear-gradient(90deg,#f5d0fe,#c084fc,#f0abfc);color:transparent;background-clip:text;-webkit-background-clip:text}
.subtitle{color:var(--muted);font-size:14px;line-height:1.7}
.pill{display:inline-block;margin-top:16px;padding:8px 13px;border:1px solid #c084fc55;border-radius:30px;background:#a855f71c;color:#f3e8ff;font-size:11px;letter-spacing:1px}
.stats{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px;margin:25px auto 30px}
.stat{padding:17px 8px;text-align:center;border-radius:17px;background:linear-gradient(145deg,#351653a8,#1a0b2dbb);border:1px solid #c084fc38;box-shadow:0 12px 30px #0002}
.stat span{display:block;color:#d8b4fe;font-size:10px;font-weight:800;letter-spacing:.7px}
.stat strong{display:block;margin-top:8px;font-size:27px}
.section-head{display:flex;align-items:end;justify-content:space-between;gap:12px;margin:22px 0 15px}
.section-head h2{font-size:22px}
.section-head p{font-size:12px;color:var(--muted)}
.plans{display:grid;grid-template-columns:1fr;gap:18px;padding-bottom:38px}
.card{display:grid;grid-template-columns:225px minmax(0,1fr);overflow:hidden;border:1px solid #c084fc40;border-radius:22px;background:linear-gradient(115deg,#a855f71b,#ffffff07);box-shadow:0 13px 36px #0003;transition:transform .2s,border-color .2s}
.card:hover{transform:translateY(-3px);border-color:#d8b4fe9c}
.cover{width:100%;height:100%;min-height:210px;object-fit:cover;background:#32115b}
.content{padding:22px;display:flex;flex-direction:column;align-items:flex-start}
.kicker{font-size:10px;letter-spacing:2px;color:#d8b4fe;font-weight:900}
.content h3{font-size:21px;margin:8px 0}
.desc{font-size:13px;color:#c7b8db;line-height:1.65}
.videos{font-size:13px;color:#f3e8ff;margin:14px 0 18px}
.buy{margin-top:auto;width:100%;display:flex;align-items:center;justify-content:space-between;gap:12px;border:0;border-radius:12px;padding:14px 15px;color:white;text-decoration:none;font-size:12px;font-weight:900;background:linear-gradient(105deg,#7c3aed,#a855f7,#c026d3);box-shadow:0 7px 22px #9333ea35;cursor:pointer}
.buy:hover{filter:brightness(1.12)}
.price{font-size:17px;white-space:nowrap}
footer{text-align:center;padding:20px 0 38px;color:#a99abf;font-size:12px}
.support{position:fixed;z-index:20;right:17px;bottom:19px;display:flex;align-items:center;gap:9px;padding:14px 17px;border-radius:50px;background:linear-gradient(110deg,#2563eb,#7c3aed);border:1px solid #ffffff55;color:white;text-decoration:none;font-size:12px;font-weight:900;box-shadow:0 8px 32px #7c3aed80}
.modal{display:none;position:fixed;z-index:50;inset:0;overflow:auto;padding:20px 12px;background:#080410e8;backdrop-filter:blur(9px)}
.modal-box{position:relative;width:min(430px,100%);margin:15px auto;padding:25px;border-radius:24px;border:1px solid #c084fc65;background:linear-gradient(150deg,#2b1242,#150a24);box-shadow:0 20px 80px #0009;text-align:center}
.close{position:absolute;right:15px;top:10px;border:0;background:transparent;color:white;font-size:28px;cursor:pointer}
.small-logo{width:52px;height:52px;font-size:21px;margin-bottom:14px}
.modal-box h2{font-size:23px;margin:8px 0}
.modal-sub{font-size:13px;line-height:1.6;color:var(--muted);margin:7px 0 15px}
.amount{font-size:38px;font-weight:950;color:#f3e8ff;margin:8px 0 18px}
.qr{width:200px;height:200px;display:block;object-fit:contain;background:#fff;border-radius:12px;padding:7px;margin:0 auto 13px}
.upi{font-size:12px;color:#e9d5ff;overflow-wrap:anywhere;margin-bottom:16px}
.label{display:block;text-align:left;font-size:13px;font-weight:800;margin:13px 0 8px}
input{width:100%;padding:14px;border-radius:11px;border:1px solid #7c3aed99;background:#10071f;color:white;outline:none}
input:focus{border-color:#e9d5ff}
.submit{width:100%;margin-top:13px;padding:14px;border:0;border-radius:11px;color:white;background:linear-gradient(100deg,#7c3aed,#c026d3);font-weight:900;cursor:pointer}
.note{font-size:11px;line-height:1.6;color:#b8a7ce;margin-top:13px}
.flash{padding:12px;border-radius:12px;margin:12px 0;background:#4c1d55;color:#fce7f3;font-size:13px}
.success{max-width:650px;margin:25px auto 45px;text-align:center;padding:30px;border-radius:22px;background:#ffffff09;border:1px solid #4ade8066}
.tick{width:72px;height:72px;display:grid;place-items:center;margin:0 auto 16px;border-radius:50%;border:2px solid #4ade80;color:#4ade80;background:#16a34a22;font-size:42px}
@media(max-width:560px){.wrap{width:92%}.card{grid-template-columns:112px minmax(0,1fr)}.cover{min-height:100%;height:100%;max-height:none}.content{padding:14px}.content h3{font-size:16px}.desc{font-size:12px}.videos{margin:11px 0}.buy{padding:12px 10px;font-size:10px}.price{font-size:15px}.stats{gap:7px}.stat{padding:14px 4px}.stat span{font-size:8px;letter-spacing:0}.stat strong{font-size:22px}.modal-box{padding:22px 17px}}
@media(prefers-reduced-motion:reduce){*{transition:none!important}}
</style>
</head>
<body>
<div class="wrap">
<header>
  <div class="logo">{{ letter }}</div>
  <div class="brand">{{ brand }}</div>
  <h1>Unlock Your <span class="grad">Potential</span></h1>
  <p class="subtitle">Premium courses. Practical lessons. Your next level starts here.</p>
  <div class="pill">✦ YOUR LEARNING JOURNEY STARTS HERE ✦</div>
</header>

<div class="stats">
  <div class="stat"><span>AVAILABLE PLANS</span><strong>{{ stats.total_plans }}</strong></div>
  <div class="stat"><span>ORDERS SUBMITTED</span><strong>{{ stats.submitted_orders }}</strong></div>
  <div class="stat"><span>VERIFIED PURCHASES</span><strong>{{ stats.verified_purchases }}</strong></div>
</div>

{% with messages = get_flashed_messages() %}
{% if messages %}{% for message in messages %}<div class="flash">{{ message }}</div>{% endfor %}{% endif %}
{% endwith %}

{% if success %}
<section class="success">
  <div class="tick">✓</div>
  <h2>Submission Received</h2>
  <p class="subtitle" style="margin-top:12px">Your UTR has been submitted for review. This green tick confirms submission only; course access will be granted after payment verification.</p>
  <a class="buy" href="{{ url_for('home') }}" style="margin:22px auto 0;max-width:230px;justify-content:center">BACK TO PLANS</a>
</section>
{% else %}
<div class="section-head"><div><h2>Choose Your Plan</h2><p style="margin-top:6px">Pick the course that fits you</p></div><p>8 PLANS</p></div>
<main class="plans">
{% for plan in plans %}
<article class="card">
  <img class="cover" src="{{ plan.image }}" alt="{{ plan.name }}" loading="lazy"
       onerror="this.onerror=null;this.src='https://placehold.co/700x500/32115b/ffffff?text=Course+Image'">
  <div class="content">
    <div class="kicker">PLAN {{ "%02d"|format(plan.id) }}</div>
    <h3>{{ plan.name }}</h3>
    <p class="desc">{{ plan.description }}</p>
    <div class="videos">▶ &nbsp;{{ plan.videos }} videos included</div>
    <button class="buy" onclick="openPayment({{ plan.id }},{{ plan.price }},{{ plan.name|tojson }})">
      <span>UNLOCK ACCESS</span><span class="price">₹{{ plan.price }}</span>
    </button>
  </div>
</article>
{% endfor %}
</main>
{% endif %}
<footer>© {{ brand }} · Premium Learning Experience</footer>
</div>

<a class="support" href="{{ support }}" target="_blank" rel="noopener noreferrer">✈ &nbsp; 24/7 TELEGRAM SUPPORT</a>

<div class="modal" id="paymentModal" role="dialog" aria-modal="true" aria-labelledby="paymentTitle">
<div class="modal-box">
  <button class="close" onclick="closePayment()" aria-label="Close payment">×</button>
  <div class="logo small-logo">{{ letter }}</div>
  <h2 id="paymentTitle">Complete Your Payment</h2>
  <p class="modal-sub" id="selectedPlan">Selected course</p>
  <div class="amount" id="selectedAmount">₹199</div>
  <img class="qr" id="paymentQR" src="" alt="UPI payment QR code">
  <div class="upi">UPI ID: {{ upi }}</div>
  <p class="modal-sub">Scan this QR in your UPI app and pay the exact amount shown above.</p>
  <form action="{{ url_for('submit_payment') }}" method="POST">
    <input type="hidden" name="csrf_token" value="{{ csrf_token }}">
    <input type="hidden" name="plan_id" id="planId">
    <label class="label" for="utr">Pay and enter UTR in the box</label>
    <input type="text" id="utr" name="utr" minlength="6" maxlength="100" placeholder="Enter UTR / transaction ID" autocomplete="off" required>
    <button type="submit" class="submit">SUBMIT PAYMENT ✓</button>
  </form>
  <p class="note">Submitting a UTR does not verify payment. Your order stays pending until the payment is checked.</p>
</div>
</div>

<script>
const modal=document.getElementById("paymentModal");
function openPayment(id,price,name){
  document.getElementById("planId").value=id;
  document.getElementById("selectedAmount").textContent="₹"+price;
  document.getElementById("selectedPlan").textContent=name;
  document.getElementById("utr").value="";
  const qr=document.getElementById("paymentQR");
  qr.src="/payment-qr/"+id;
  modal.style.display="block";
  document.body.style.overflow="hidden";
}
function closePayment(){modal.style.display="none";document.body.style.overflow="";}
modal.addEventListener("click",e=>{if(e.target===modal)closePayment();});
document.addEventListener("keydown",e=>{if(e.key==="Escape")closePayment();});
</script>
</body>
</html>
"""

@app.before_request
def ensure_csrf():
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)

@app.route("/")
def home():
    return render_template_string(
        PAGE, brand=BRAND_NAME, letter=BRAND_LETTER, plans=PLANS,
        support=TELEGRAM_SUPPORT, upi=UPI_ID, stats=get_stats(),
        success=False, csrf_token=session["csrf_token"]
    )

@app.route("/payment-qr/<int:plan_id>")
def payment_qr(plan_id):
    plan = next((p for p in PLANS if p["id"] == plan_id), None)
    if plan is None:
        abort(404)

    # UPI deep link encodes the selected plan's amount. This creates a QR;
    # it does NOT verify payment or automatically unlock the course.
    payload = "upi://pay?" + urlencode({
        "pa": UPI_ID,
        "pn": BRAND_NAME,
        "am": f'{plan["price"]:.2f}',
        "cu": "INR",
        "tn": f'{plan["name"]} course'
    })
    qr = qrcode.QRCode(
        version=None,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=9,
        border=4
    )
    qr.add_data(payload)
    qr.make(fit=True)
    image = qr.make_image(fill_color="black", back_color="white")
    output = io.BytesIO()
    image.save(output, format="PNG")
    return Response(output.getvalue(), mimetype="image/png",
                    headers={"Cache-Control": "no-store"})

@app.route("/submit-payment", methods=["POST"])
def submit_payment():
    submitted_token = request.form.get("csrf_token", "")
    saved_token = session.get("csrf_token", "")
    if not submitted_token or not saved_token or not secrets.compare_digest(submitted_token, saved_token):
        return "Session expired. Reload the page and try again.", 400

    try:
        plan_id = int(request.form.get("plan_id", ""))
    except (TypeError, ValueError):
        return "Invalid plan.", 400

    plan = next((p for p in PLANS if p["id"] == plan_id), None)
    if plan is None:
        abort(404)

    utr = request.form.get("utr", "").strip()
    if not 6 <= len(utr) <= 100 or any(ord(ch) < 32 for ch in utr):
        flash("Please enter a valid UTR / transaction reference.")
        return redirect(url_for("home"))

    with get_db() as conn:
        conn.execute(
            """INSERT INTO payment_submissions
               (plan_id, plan_name, amount, utr, status)
               VALUES (?, ?, ?, ?, 'PENDING')""",
            (plan["id"], plan["name"], plan["price"], utr)
        )

    return render_template_string(
        PAGE, brand=BRAND_NAME, letter=BRAND_LETTER, plans=PLANS,
        support=TELEGRAM_SUPPORT, upi=UPI_ID, stats=get_stats(),
        success=True, csrf_token=session["csrf_token"]
    )

@app.route("/health")
def health():
    return {"status": "ok"}

init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")))
