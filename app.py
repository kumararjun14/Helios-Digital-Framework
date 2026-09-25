"""Akai Mechanical portfolio site: pages, local landing pages, and optional lead intake."""
from flask import Flask, render_template, request, redirect, url_for, flash, session, abort
from datetime import datetime
from pathlib import Path
import csv, os, requests, secrets
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY") or secrets.token_hex(32)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024
app.config["SESSION_COOKIE_HTTPONLY"] = True
app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

COMPANY = {
    "name": "Akai Mechanical Services",
    "phone": "717-461-2075",
    "phone_href": "tel:+17174612075",
    "email": "info@akaimechanical.com",
    "location": "Harrisburg, PA",
    "hours": "Open 7:30 AM - 7:00 PM",
    "description": "Premium heating, cooling, refrigeration, and light commercial HVAC service across Central Pennsylvania.",
}

SERVICES = [
    {"slug":"ac-repair","title":"Air Conditioning Repair","eyebrow":"Cooling","summary":"Fast diagnostics, refrigerant checks, airflow fixes, and clean repair options.","details":"We service central AC systems, ductless units, heat pumps, coils, capacitors, thermostats, and airflow problems.","image":"https://images.unsplash.com/photo-1621905251189-08b45d6a269e?auto=format&fit=crop&w=1400&q=80"},
    {"slug":"heating","title":"Heating & Furnace Service","eyebrow":"Heating","summary":"Reliable heating repair, maintenance, and replacement for cold Pennsylvania winters.","details":"From no-heat calls to preventive tune-ups, we help keep homes and businesses warm and safe.","image":"https://images.unsplash.com/photo-1581094288338-2314dddb7ece?auto=format&fit=crop&w=1400&q=80"},
    {"slug":"refrigeration","title":"Refrigeration Service","eyebrow":"Commercial","summary":"Commercial refrigeration service for restaurants, markets, offices, and small businesses.","details":"Walk-in coolers, reach-ins, ice machines, temperature issues, and maintenance support.","image":"https://images.unsplash.com/photo-1581092335397-9583eb92d232?auto=format&fit=crop&w=1400&q=80"},
    {"slug":"maintenance","title":"Preventive Maintenance","eyebrow":"Plans","summary":"Seasonal maintenance plans built to reduce breakdowns and extend system life.","details":"Filter checks, coil cleaning, safety checks, airflow testing, and performance recommendations.","image":"https://images.unsplash.com/photo-1607472586893-edb57bdc0e39?auto=format&fit=crop&w=1400&q=80"},
]

CITY_PAGES = [
    {"slug":"hvac-harrisburg-pa","city":"Harrisburg", "service":"HVAC Service"},
    {"slug":"ac-repair-harrisburg-pa","city":"Harrisburg", "service":"AC Repair"},
    {"slug":"furnace-repair-harrisburg-pa","city":"Harrisburg", "service":"Furnace Repair"},
    {"slug":"commercial-hvac-harrisburg-pa","city":"Harrisburg", "service":"Commercial HVAC"},
    {"slug":"hvac-mechanicsburg-pa","city":"Mechanicsburg", "service":"HVAC Service"},
    {"slug":"hvac-hershey-pa","city":"Hershey", "service":"HVAC Service"},
]

PROJECTS = [
    {"title":"HVAC concept image", "location":"Illustrative stock photography", "image":"https://images.unsplash.com/photo-1621905252507-b35492cc74b4?auto=format&fit=crop&w=1200&q=80"},
    {"title":"Commercial concept image", "location":"Illustrative stock photography", "image":"https://images.unsplash.com/photo-1504917595217-d4dc5ebe6122?auto=format&fit=crop&w=1200&q=80"},
    {"title":"Heating concept image", "location":"Illustrative stock photography", "image":"https://images.unsplash.com/photo-1581092795360-fd1ca04f0952?auto=format&fit=crop&w=1200&q=80"},
]

def csrf_token():
    """Create a per-session token for the browser forms."""
    if "csrf_token" not in session:
        session["csrf_token"] = secrets.token_urlsafe(32)
    return session["csrf_token"]


@app.context_processor
def inject_globals():
    return {"company": COMPANY, "services": SERVICES, "city_pages": CITY_PAGES,
            "current_year": datetime.now().year, "csrf_token": csrf_token,
            "site_url": os.getenv("SITE_URL", "").rstrip("/"),
            "lead_enabled": bool(os.getenv("LEAD_STORAGE_PATH") or os.getenv("GOOGLE_SHEET_WEBHOOK_URL"))}


def parse_lead(form):
    """Pre: browser form data. Post: bounded, validated fields or ValueError."""
    name, phone = form.get("name", "").strip(), form.get("phone", "").strip()
    if not (1 <= len(name) <= 100 and 7 <= len(phone) <= 30):
        raise ValueError("Enter a name and a valid phone number.")
    row = {"created_at": datetime.now().isoformat(timespec="seconds"),
           "name": name, "phone": phone, "email": form.get("email", "").strip()[:254],
           "service": form.get("service", "").strip()[:60],
           "urgency": form.get("urgency", "").strip()[:30],
           "message": form.get("message", "").strip()[:2000],
           "source_page": form.get("source_page", "").strip()[:60]}
    return row


def deliver_lead(row):
    """Pre: validated lead. Post: True only after configured storage or webhook succeeds."""
    path = os.getenv("LEAD_STORAGE_PATH")
    hook = os.getenv("GOOGLE_SHEET_WEBHOOK_URL")
    delivered = False
    if path:
        lead_file = Path(path).expanduser().resolve()
        if lead_file.is_relative_to((Path(app.static_folder)).resolve()):
            raise ValueError("Lead storage cannot be inside the public static directory")
        lead_file.parent.mkdir(parents=True, exist_ok=True)
        new = not lead_file.exists()
        with lead_file.open("a", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=row.keys())
            if new:
                writer.writeheader()
            writer.writerow(row)
        delivered = True
    if hook:
        try:
            response = requests.post(hook, json=row, timeout=8)
            response.raise_for_status()
            delivered = True
        except requests.RequestException:
            app.logger.warning("Configured lead webhook failed")
    return delivered

@app.route("/")
def home():
    return render_template("index.html", projects=PROJECTS)

@app.route("/services")
def services_page():
    return render_template("services.html")

@app.route("/service-area")
def service_area():
    return render_template("service_area.html")

@app.route("/request-service", methods=["GET", "POST"])
def request_service():
    if request.method == "POST":
        if not secrets.compare_digest(session.get("csrf_token", ""), request.form.get("csrf_token", "")):
            abort(400)
        if not (os.getenv("LEAD_STORAGE_PATH") or os.getenv("GOOGLE_SHEET_WEBHOOK_URL")):
            flash("Demo only: your request was not sent or saved.", "notice")
            return redirect(url_for("request_service"))
        try:
            row = parse_lead(request.form)
            delivered = deliver_lead(row)
        except ValueError as exc:
            flash(str(exc), "notice")
            return render_template("request_service.html"), 400
        if delivered:
            flash("Your request was recorded. Please call for urgent service.", "success")
        else:
            flash("Your request could not be delivered. Please call the business.", "notice")
        return redirect(url_for("request_service"))
    return render_template("request_service.html")

@app.route("/seo/<slug>")
def seo_page(slug):
    page = next((p for p in CITY_PAGES if p["slug"] == slug), None)
    if not page:
        abort(404)
    return render_template("seo_page.html", page=page)

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG") == "1")
