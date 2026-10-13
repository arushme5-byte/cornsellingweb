import os
import sqlite3
import secrets
from datetime import datetime, timezone
from decimal import Decimal, InvalidOperation
from io import BytesIO
from urllib.parse import urlencode, quote

import qrcode
from flask import Flask, abort, flash, redirect, render_template, request, send_file, session, url_for
from werkzeug.middleware.proxy_fix import ProxyFix

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
DATABASE_PATH = os.environ.get("DATABASE_PATH", os.path.join(BASE_DIR, "social_flux.sqlite3"))
UPI_ID = os.environ.get("UPI_ID", "haaland78@ybl")
PAYEE_NAME = os.environ.get("PAYEE_NAME", "Social Flux")
# Replace with your real Telegram username or full support URL before publishing.
TELEGRAM_SUPPORT = os.environ.get("TELEGRAM_SUPPORT", "https://t.me/REPLACE_WITH_SUPPORT_USERNAME")
SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
CURRENCY = "INR"

app = Flask(__name__)
app.secret_key = SECRET_KEY
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1)

# Edit the 8 plan dictionaries here. Prices are always read from this server-side list.
PLANS = [
    {
        "id": 1, "name": "Social Media Starter", "image_url": "https://images.unsplash.com/photo-1611162617474-5b21e879e113?auto=format&fit=crop&w=1200&q=85",
        "caption": "Build a confident social presence.", "description": "Learn the fundamentals of creating and managing a polished social media presence.",
        "video_count": 12, "price": 499, "features": ["12 focused lessons", "Beginner-friendly roadmap", "Lifetime access (after verification)"]
    },
    {
        "id": 2, "name": "Content Creator Pro", "image_url": "https://images.unsplash.com/photo-1536240478700-b869070f9279?auto=format&fit=crop&w=1200&q=85",
        "caption": "Turn ideas into scroll-stopping content.", "description": "Explore practical content planning, production workflows, and creative storytelling.",
        "video_count": 18, "price": 799, "features": ["18 video lessons", "Content planning toolkit", "Lifetime access (after verification)"]
    },
    {
        "id": 3, "name": "Reels & Short Video Mastery", "image_url": "https://images.unsplash.com/photo-1492619375914-88005aa9e8fb?auto=format&fit=crop&w=1200&q=85",
        "caption": "Create short videos with a clear workflow.", "description": "Learn repeatable methods for scripting, filming, editing, and publishing short-form videos.",
        "video_count": 20, "price": 999, "features": ["20 video lessons", "Editing workflow", "Lifetime access (after verification)"]
    },
    {
        "id": 4, "name": "Digital Marketing Essentials", "image_url": "https://images.unsplash.com/photo-1460925895917-afdab827c52f?auto=format&fit=crop&w=1200&q=85",
        "caption": "Understand the digital growth toolkit.", "description": "Get an introduction to audience research, campaign planning, analytics, and optimization.",
        "video_count": 16, "price": 1199, "features": ["16 video lessons", "Campaign checklist", "Lifetime access (after verification)"]
    },
    {
        "id": 5, "name": "Instagram Growth Blueprint", "image_url": "https://images.unsplash.com/photo-1611262588024-d12430b98920?auto=format&fit=crop&w=1200&q=85",
        "caption": "Build a consistent profile and content system.", "description": "Explore profile optimization, content consistency, community engagement, and insights.",
        "video_count": 22, "price": 1499, "features": ["22 video lessons", "Profile audit checklist", "Lifetime access (after verification)"]
    },
    {
        "id": 6, "name": "Branding & Design Toolkit", "image_url": "https://images.unsplash.com/photo-1558655146-9f40138edfeb?auto=format&fit=crop&w=1200&q=85",
        "caption": "Make your brand feel cohesive.", "description": "Learn foundational visual identity concepts and practical design workflows.",
        "video_count": 14, "price": 1299, "features": ["14 video lessons", "Branding worksheets", "Lifetime access (after verification)"]
    },
    {
        "id": 7, "name": "Creator Monetization Lab", "image_url": "https://images.unsplash.com/photo-1553877522-43269d4ea984?auto=format&fit=crop&w=1200&q=85",
        "caption": "Explore sustainable creator business models.", "description": "Review audience value, offer design, and monetization fundamentals for creators.",
        "video_count": 17, "price": 1799, "features": ["17 video lessons", "Offer planning worksheet", "Lifetime access (after verification)"]
    },
    {
        "id": 8, "name": "Social Flux All-Access", "image_url": "https://images.unsplash.com/photo-1552664730-d307ca884978?auto=format&fit=crop&w=1200&q=85",
        "caption": "Bring your learning tracks together.", "description": "A bundled learning path covering social media, content, marketing, branding, and creator business basics.",
        "video_count": 60, "price": 2499, "features": ["60 video lessons", "All listed learning tracks", "Lifetime access (after verification)"]
    },
]

PLANS_BY_ID = {plan["id"]: plan for plan in PLANS}


def get_db():
    connection = sqlite3.connect(DATABASE_PATH, timeout=10)
    connection.row_factory = sqlite3.Row
    return connection


def init_db():
    os.makedirs(os.path.dirname(os.path.abspath(DATABASE_PATH)), exist_ok=True)
    with get_db() as db:
        db.execute("""
            CREATE TABLE IF NOT EXISTS payment_submissions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                plan_id INTEGER NOT NULL,
                reference TEXT NOT NULL COLLATE NOCASE UNIQUE,
                submitted_at TEXT NOT NULL,
                status TEXT NOT NULL DEFAULT 'PENDING',
            )
        """)
        # A separate plans table is intentionally not needed; plan definitions live in PLANS above.
        db.execute("CREATE INDEX IF NOT EXISTS idx_payment_submissions_plan_id ON payment_submissions(plan_id)")
        db.commit()


def get_plan(plan_id):
    try:
        numeric_id = int(plan_id)
    except (TypeError, ValueError):
        return None
    return PLANS_BY_ID.get(numeric_id)


def make_upi_uri(plan):
    params = {
        "pa": UPI_ID,
        "pn": PAYEE_NAME,
        "am": f'{Decimal(str(plan["price"])):.2f}',
        "cu": CURRENCY,
        "tn": f'SOCIAL FLUX - {plan["name"]} (Plan {plan["id"]})',
    }
    return "upi://pay?" + urlencode(params, quote_via=quote)


def telegram_url():
    return TELEGRAM_SUPPORT


@app.context_processor
def inject_shared_config():
    def csrf_token():
        token = session.get("csrf_token")
        if not token:
            token = secrets.token_urlsafe(32)
            session["csrf_token"] = token
        return token
    return {"telegram_support": telegram_url(), "csrf_token": csrf_token}


@app.route("/")
def index():
    return render_template("index.html", plans=PLANS)


@app.route("/payment/<int:plan_id>")
def payment(plan_id):
    plan = get_plan(plan_id)
    if not plan:
        abort(404)
    upi_uri = make_upi_uri(plan)
    return render_template("payment.html", plan=plan, upi_uri=upi_uri, upi_id=UPI_ID, payee_name=PAYEE_NAME)


@app.route("/qr/<int:plan_id>.png")
def payment_qr(plan_id):
    plan = get_plan(plan_id)
    if not plan:
        abort(404)
    qr = qrcode.QRCode(version=None, error_correction=qrcode.constants.ERROR_CORRECT_M, box_size=10, border=4)
    qr.add_data(make_upi_uri(plan))
    qr.make(fit=True)
    image = qr.make_image(fill_color="#120d1d", back_color="white")
    buffer = BytesIO()
    image.save(buffer, format="PNG")
    buffer.seek(0)
    return send_file(buffer, mimetype="image/png", max_age=300)


@app.route("/submit-reference/<int:plan_id>", methods=["POST"])
def submit_reference(plan_id):
    plan = get_plan(plan_id)
    if not plan:
        abort(404)

    submitted_csrf = request.form.get("csrf_token", "")
    session_csrf = session.get("csrf_token", "")
    if not submitted_csrf or not session_csrf or not secrets.compare_digest(submitted_csrf, session_csrf):
        flash("Your form session expired. Please try again.", "error")
        return redirect(url_for("payment", plan_id=plan_id))

    reference = request.form.get("reference", "").strip().upper()
    # Common UTR / bank reference formats are alphanumeric; keep a broad but bounded validator.
    if not re.fullmatch(r"[A-Z0-9]{8,35}", reference):
        flash("Enter a valid UTR / transaction reference (8–35 letters or digits).", "error")
        return redirect(url_for("payment", plan_id=plan_id))

    submitted_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    try:
        with get_db() as db:
            db.execute(
                "INSERT INTO payment_submissions (plan_id, reference, submitted_at, status) VALUES (?, ?, ?, 'PENDING')",
                (plan_id, reference, submitted_at),
            )
            db.commit()
            submission = db.execute(
                "SELECT id, plan_id, reference, submitted_at, status FROM payment_submissions WHERE reference = ?",
                (reference,),
            ).fetchone()
    except sqlite3.IntegrityError:
        flash("That transaction reference has already been submitted. Please check the reference or contact support.", "error")
        return redirect(url_for("payment", plan_id=plan_id))
    except sqlite3.Error:
        app.logger.exception("Database error while saving payment reference")
        flash("We couldn't save your reference right now. Please try again shortly.", "error")
        return redirect(url_for("payment", plan_id=plan_id))

    return render_template("success.html", plan=plan, submission=submission)


@app.route("/health")
def health():
    try:
        with get_db() as db:
            db.execute("SELECT 1").fetchone()
        return {"status": "ok", "database": "connected"}, 200
    except sqlite3.Error:
        app.logger.exception("Health check database failure")
        return {"status": "error", "database": "unavailable"}, 503


@app.errorhandler(404)
def not_found(_error):
    return render_template("not_found.html"), 404


@app.errorhandler(500)
def server_error(_error):
    return render_template("error.html"), 500


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", "5000")), debug=False)
