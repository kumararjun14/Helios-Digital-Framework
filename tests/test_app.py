import csv
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from app import app, CITY_PAGES

class SiteTests(unittest.TestCase):
    def setUp(self):
        app.config.update(TESTING=True)
        self.client = app.test_client()

    def test_routes(self):
        for path in ("/", "/services", "/service-area", "/request-service", "/seo/" + CITY_PAGES[0]["slug"]):
            self.assertEqual(self.client.get(path).status_code, 200, path)
        self.assertEqual(self.client.get("/seo/missing").status_code, 404)

    def test_demo_and_private_lead(self):
        with self.client.session_transaction() as session:
            session["csrf_token"] = "token"
        data = {"csrf_token": "token", "name": "Guest", "phone": "7175550100"}
        with patch.dict("app.os.environ", {"LEAD_STORAGE_PATH": "", "GOOGLE_SHEET_WEBHOOK_URL": ""}):
            response = self.client.post("/request-service", data=data, follow_redirects=True)
            self.assertIn(b"not sent or saved", response.data)
        with tempfile.TemporaryDirectory() as tmp, patch.dict("app.os.environ", {"LEAD_STORAGE_PATH": str(Path(tmp)/"leads.csv"), "GOOGLE_SHEET_WEBHOOK_URL": ""}):
            self.assertEqual(self.client.post("/request-service", data={"name":"Guest"}).status_code, 400)
            response = self.client.post("/request-service", data=data, follow_redirects=True)
            self.assertIn(b"request was recorded", response.data)
            with (Path(tmp)/"leads.csv").open(newline="") as file:
                self.assertEqual(list(csv.DictReader(file))[0]["name"], "Guest")
