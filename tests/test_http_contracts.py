import unittest
from pathlib import Path


class HttpContractsTests(unittest.TestCase):
    def test_put_delete_route_declarations_present(self):
        profile = Path("routes/profile.py").read_text(encoding="utf-8")
        requests_routes = Path("routes/requests.py").read_text(encoding="utf-8")
        admin = Path("routes/admin.py").read_text(encoding="utf-8")

        self.assertIn('@profile_bp.put("/edit")', profile)
        self.assertIn('@profile_bp.put("/change-password")', profile)
        self.assertIn('@requests_bp.delete("/<int:request_id>")', requests_routes)
        self.assertIn('@admin_bp.delete("/users/<int:user_id>")', admin)

    def test_frontend_uses_real_put_delete_fetch(self):
        base = Path("templates/base.html").read_text(encoding="utf-8")
        self.assertRegex(base, r"method:\s*'PUT'")
        self.assertRegex(base, r"method:\s*'DELETE'")

    def test_buy_consultation_form_is_actionable(self):
        buy = Path("templates/buy.html").read_text(encoding="utf-8")
        self.assertIn("id=\"consultation-form\"", buy)
        self.assertIn("action=\"{{ url_for('public.consultation_submit') }}\"", buy)
        self.assertIn("prepareConsultation", buy)
        self.assertIn("consultation-car-model", buy)

    def test_public_consultation_route_has_safe_redirect_and_model_feedback(self):
        public_routes = Path("routes/public.py").read_text(encoding="utf-8")
        self.assertIn("def _safe_next_url", public_routes)
        self.assertIn("car_model = request.form.get(\"car_model\"", public_routes)
        self.assertIn("model_suffix", public_routes)


if __name__ == "__main__":
    unittest.main()
