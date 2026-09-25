# Akai Mechanical Services — local HVAC website

A Flask website concept for an HVAC business in Central Pennsylvania. I designed the responsive interface, built reusable page templates, and implemented service and location landing pages as part of my **Local Business Website & SEO Platform** project.

> Portfolio concept. The logo was supplied with the original project; photographs are illustrative remote stock images. Confirm company facts, contact details, rights to assets, and service coverage with the owner before publishing as an official business site. This repository does not claim search ranking or lead growth.

## Features

- Home, services, service area, six city/service landing pages, and request form.
- Responsive CSS, keyboard skip link and focus styles, mobile navigation, and reduced motion support.
- Page specific titles for service and city pages; meta description, optional canonical URL and `HVACBusiness` JSON-LD. Set `SITE_URL` before deployment.
- Optional lead delivery to a **private** CSV path and/or a trusted Google Sheets webhook. With neither configured, the form clearly reports that nothing was sent or stored.
- Input bounds, per-session CSRF token, 16 KB request limit, and a 404 for unknown landing page slugs.

## Run locally

Python 3.10 or later:

```bash
python -m venv .venv
# Windows PowerShell: .venv\Scripts\Activate.ps1
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Open http://127.0.0.1:5000. Tests: `python -m unittest discover -s tests -v`.

## Configure lead handling

Copy `.env.example` to `.env` and set a long random `SECRET_KEY` for a deployed instance. `python-dotenv` loads `.env` locally. By default, submissions are **demo only**. To record leads, set `LEAD_STORAGE_PATH=instance/leads.csv` (a private directory outside `static/`) or `GOOGLE_SHEET_WEBHOOK_URL` to a trusted endpoint. Never commit `.env` or actual lead data. The CSV includes contact details, so restrict access and decide on a retention policy before accepting real leads. If both destinations are configured, the CSV remains a local copy even if the webhook fails. A successful response means at least one destination accepted the lead; it does not promise a staff response.

## SEO implementation

| Element | Implementation | Purpose |
| --- | --- | --- |
| Descriptive local URLs | `/seo/<slug>` from `CITY_PAGES` | Service and city specific entry points |
| Page titles | `seo_page.html` block | Relevant page labels in browser and search previews |
| Canonical URL | `base.html` + `SITE_URL` | Identifies the chosen public URL |
| Structured data | `base.html` via JSON serialization | Supplies basic business details to crawlers |
| Internal navigation | Service area links and footer | Connects related location pages |

The location pages currently reuse short generic copy. Before public indexing, add approved location specific details, verify each covered area, and consider merging thin pages. Also add a sitemap and Search Console verification after the final domain is known. Technical SEO setup alone does not establish ranking or measurable conversion.

## Architecture

- `app.py`: business data, view routes, lead validation, and optional delivery. `parse_lead` and `deliver_lead` document their preconditions and outcomes.
- `templates/`: Jinja page templates with a shared layout.
- `static/css/styles.css`, `static/js/main.js`: layout, motion, and navigation.
- `static/img/akai-logo.jpg`: supplied branding asset.
- `tests/`: request behavior and intake checks.

## Next steps

Confirm the business details, replace illustrative images with licensed company photos, make the six location pages genuinely useful, connect a production lead workflow, audit accessibility, and track contact actions. The site is a Flask application and needs a Python capable host; GitHub Pages alone will not run it.
