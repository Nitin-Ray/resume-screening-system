"""AI Resume Screening & Job Matching System - Flask app (login + admin dashboard)"""
import os
from datetime import datetime
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from extractor import extract_text
from skills import build_profile, looks_like_resume
from matcher import match_score
from suggestions import get_suggestions
from database import (init_db, create_user, get_user_by_email, save_result, get_history,
                      get_stats, get_users_with_stats, get_user, get_user_records, get_record, get_user_record)

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "resume-screening-dev-key")
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
app.config["UPLOAD_FOLDER"] = os.path.join(BASE_DIR, "uploads")  # always next to the code
os.makedirs(app.config["UPLOAD_FOLDER"], exist_ok=True)
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024
ALLOWED = {".pdf", ".docx"}
ROLES = ("Recruiter", "Job Seeker")  # Admin cannot be registered from the form
init_db()


def login_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if "user_id" not in session:
            flash("Please login first.")
            return redirect(url_for("login"))
        return f(*a, **kw)
    return wrapper


def admin_required(f):
    @wraps(f)
    def wrapper(*a, **kw):
        if session.get("role") != "Admin":
            flash("Access denied. Admin only.")
            return redirect(url_for("index"))
        return f(*a, **kw)
    return wrapper


def split_skills(s):
    return [x for x in (s or "").split(", ") if x]


def remove_file(path):
    """Delete an uploaded file that was rejected, so unused files do not pile up."""
    try:
        os.remove(path)
    except OSError:
        pass


def analyze_record(rec):
    """Analyse a saved record again from its stored file and job description.
    Returns (result, profile); falls back to the saved summary if the file is not available."""
    res = profile = None
    if rec["stored_file"] and rec["jd"]:
        path = os.path.join(app.config["UPLOAD_FOLDER"], rec["stored_file"])
        if os.path.exists(path):
            text = extract_text(path)
            if text.strip():
                res, profile = match_score(text, rec["jd"]), build_profile(text)
    if res is None:  # old record / file missing: show saved summary
        res = {"score": rec["score"], "skill_pct": None, "text_pct": None,
               "matched": split_skills(rec["matched"]), "missing": split_skills(rec["missing"])}
    return res, profile


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        pw, pw2 = request.form.get("password", ""), request.form.get("confirm", "")
        role = request.form.get("role", "")
        if not name or len(name) > 100 or " " in email or "@" not in email or "." not in email.rsplit("@", 1)[-1]:
            flash("Please enter a valid name and email.")
        elif role not in ROLES:
            flash("Please select a role.")
        elif len(pw) < 6 or not pw.strip():
            flash("Password must be at least 6 characters long.")
        elif pw != pw2:
            flash("Passwords do not match.")
        elif not create_user(name, email, generate_password_hash(pw), role):
            flash("This email is already registered.")
        else:
            flash("Account created successfully! Please login.")
            return redirect(url_for("login"))
        return redirect(url_for("register"))
    return render_template("register.html", roles=ROLES)


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = get_user_by_email(request.form.get("email", "").strip().lower())
        if user and check_password_hash(user["password_hash"], request.form.get("password", "")):
            session.clear()
            session.update(user_id=user["id"], name=user["name"], role=user["role"])
            return redirect(url_for("admin_dashboard" if user["role"] == "Admin" else "index"))
        flash("Invalid email or password.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.")
    return redirect(url_for("login"))


@app.route("/", methods=["GET", "POST"])
@login_required
def index():
    if session["role"] == "Admin":
        return redirect(url_for("admin_dashboard"))
    if request.method == "POST":
        f, jd = request.files.get("resume"), request.form.get("jd", "").strip()
        if not f or not f.filename or not jd:
            flash("Both resume and job description are required.")
            return redirect(url_for("index"))
        # The extension is taken from the original name (names in Hindi/Marathi etc. lose it in secure_filename)
        base, ext = os.path.splitext(f.filename.replace("\\", "/").split("/")[-1])
        if ext.lower() not in ALLOWED:
            flash("Only PDF or DOCX files are allowed.")
            return redirect(url_for("index"))
        name = (base + ext.lower())[:100]  # name shown to the user
        stored = f"{session['user_id']}_{datetime.now():%Y%m%d%H%M%S}_{(secure_filename(base) or 'resume')[:60]}{ext.lower()}"
        path = os.path.join(app.config["UPLOAD_FOLDER"], stored)
        f.save(path)
        text = extract_text(path)
        if not text.strip():
            remove_file(path)
            flash("Could not read text from the resume. The file may be scanned, empty, damaged or password protected.")
            return redirect(url_for("index"))

        # Resume validation: a resume has a known skill or degree, or typical resume headings
        if not looks_like_resume(text):
            remove_file(path)
            flash("This doesn't look like a resume (it needs at least two of: e-mail address, phone number, degree, resume headings, skills). Please upload a valid resume.")
            return redirect(url_for("index"))

        res = match_score(text, jd)
        rid = save_result(session["user_id"], name, res["score"], res["matched"], res["missing"], stored, jd)
        # Redirect after POST: refreshing the result page does not save the analysis again
        return redirect(url_for("result", rid=rid))
    return render_template("index.html")


@app.route("/result/<int:rid>")
@login_required
def result(rid):
    if session["role"] == "Admin":
        return redirect(url_for("admin_dashboard"))
    rec = get_user_record(session["user_id"], rid) or abort(404)
    res, profile = analyze_record(rec)
    return render_template("result.html", filename=rec["filename"], res=res, profile=profile,
                           tips=get_suggestions(res["missing"], res["score"]))


@app.route("/history")
@login_required
def history():
    if session["role"] == "Admin":
        return redirect(url_for("admin_dashboard"))
    return render_template("history.html", rows=get_history(session["user_id"]))


# ---------------------------- Admin dashboard ----------------------------
@app.route("/admin")
@login_required
@admin_required
def admin_dashboard():
    return render_template("admin_dashboard.html", stats=get_stats(), users=get_users_with_stats())


@app.route("/admin/user/<int:uid>")
@login_required
@admin_required
def admin_user(uid):
    user = get_user(uid) or abort(404)
    records = get_user_records(uid)
    avg = round(sum(r["score"] for r in records) / len(records)) if records else 0
    return render_template("admin_user.html", user=user, records=records, avg=avg)


@app.route("/admin/result/<int:rid>")
@login_required
@admin_required
def admin_result(rid):
    rec = get_record(rid) or abort(404)
    res, profile = analyze_record(rec)
    return render_template("admin_result.html", rec=rec, res=res, profile=profile,
                           tips=get_suggestions(res["missing"], res["score"]))


@app.errorhandler(413)
def file_too_large(e):
    flash("The file is too large. Please upload a resume smaller than 5 MB.")
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(debug=True)
