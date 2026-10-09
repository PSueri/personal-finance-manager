import unittest
from datetime import datetime
from pathlib import Path
from tempfile import TemporaryDirectory
from threading import Thread

from playwright.sync_api import expect, sync_playwright
from werkzeug.serving import make_server

from application import create_app
from application.extensions import db
from application.models import TransactionHistory


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class TestFrontend(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.playwright = sync_playwright().start()
        cls.addClassCleanup(cls.playwright.stop)

        cls.browser = cls.playwright.chromium.launch()
        cls.addClassCleanup(cls.browser.close)

    def setUp(self):
        temporary_directory = TemporaryDirectory()
        self.addCleanup(temporary_directory.cleanup)
        database_path = Path(temporary_directory.name) / "browser.db"

        self.app = create_app(
            {
                "TESTING": True,
                "SECRET_KEY": "browser-test-only-secret",
                "SQLALCHEMY_DATABASE_URI": f"sqlite:///{database_path.as_posix()}",
                "WTF_CSRF_ENABLED": True,
            }
        )
        self.addCleanup(self.close_database)

        result = self.app.test_cli_runner().invoke(
            args=["db", "upgrade", "--directory", str(PROJECT_ROOT / "migrations")]
        )
        self.assertEqual(result.exit_code, 0, f"{result.output}\n{result.exception!r}")

        self.server = make_server("127.0.0.1", 0, self.app)
        self.server_thread = Thread(target=self.server.serve_forever, daemon=True)
        self.addCleanup(self.stop_server)
        self.server_thread.start()

        self.base_url = f"http://127.0.0.1:{self.server.server_port}"

        self.browser_context = self.browser.new_context()
        self.addCleanup(self.browser_context.close)
        self.page = self.browser_context.new_page()

        self.page_errors = []
        self.page.on("pageerror", lambda error: self.page_errors.append(str(error)))

    def tearDown(self):
        self.assertEqual(self.page_errors, [], "Unexpected JavaScript errors")

    def stop_server(self):
        self.server.shutdown()
        self.server_thread.join(timeout=5)
        self.server.server_close()

    def close_database(self):
        with self.app.app_context():
            db.session.remove()
            db.engine.dispose()

    def test_category_menus_follow_selected_type(self):
        self.page.goto(f"{self.base_url}/add")

        transaction_type = self.page.get_by_label("Type", exact=True)
        category = self.page.get_by_label("First Category", exact=True)
        subcategory = self.page.get_by_label("Second Category", exact=True)

        transaction_type.select_option("Income")
        category.select_option("Work")
        subcategory.select_option("Salary")
        self.assertEqual(category.locator("option[value='Home']").count(), 0)

        transaction_type.select_option("Expense")
        expect(category).to_have_value("")
        expect(subcategory).to_have_value("")
        self.assertEqual(category.locator("option[value='Work']").count(), 0)

        category.select_option("Food")
        subcategory.select_option("Grocery")
        expect(subcategory).to_have_value("Grocery")
        self.assertEqual(subcategory.locator("option[value='Salary']").count(), 0)

    def test_transaction_can_be_added_and_deleted(self):
        self.page.goto(f"{self.base_url}/add")

        self.page.get_by_label("Amount (€)", exact=True).fill("12,50")
        self.page.get_by_label("Type", exact=True).select_option("Expense")
        self.page.get_by_label("First Category", exact=True).select_option("Food")
        self.page.get_by_label("Second Category", exact=True).select_option("Grocery")
        self.page.get_by_label("Date", exact=True).fill("2024-03-15")
        self.page.get_by_role("button", name="Add Transaction", exact=True).click()

        expect(self.page).to_have_url(f"{self.base_url}/transactions")

        row = self.page.locator("table tbody tr")
        expect(row).to_have_count(1)
        expect(row).to_contain_text("12,50 €")

        row.get_by_role("button", name="Delete", exact=True).click()

        expect(
            self.page.get_by_text("No transactions yet.", exact=True)
        ).to_be_visible()
        expect(self.page.locator("table tbody tr")).to_have_count(0)

    def test_dashboard_renders_negative_cashflow(self):
        with self.app.app_context():
            for transaction_type, amount in [("Income", 500), ("Expense", 1250)]:
                is_income = transaction_type == "Income"

                db.session.add(
                    TransactionHistory(
                        type=transaction_type,
                        first_category="Work" if is_income else "Food",
                        second_category="Salary" if is_income else "Grocery",
                        date=datetime.now(),
                        amount_cents=amount,
                    )
                )

            db.session.commit()

        self.page.goto(f"{self.base_url}/dashboard")

        self.page.wait_for_function(
            "typeof Chart !== 'undefined' && Object.keys(Chart.instances).length === 10"
        )

        values = self.page.evaluate(
            """() => {
                const chart = Object.values(Chart.instances).find(
                    item => item.canvas.id === "netflow"
                );

                return {
                    amount: chart.data.datasets[0].data.slice(-1)[0],
                    minimum: chart.options.scales.yAxes[0].ticks.min
                };
            }"""
        )

        self.assertEqual(values, {"amount": -7.5, "minimum": -7.5})

    def test_mobile_navigation_can_be_opened(self):
        self.page.set_viewport_size({"width": 375, "height": 812})
        self.page.goto(self.base_url)

        navigation = self.page.locator("#navbarNavAltMarkup")
        expect(navigation).to_be_hidden()

        self.page.get_by_role("button", name="Toggle navigation", exact=True).click()
        expect(navigation).to_be_visible()

        navigation.get_by_role("link", name="Transactions", exact=True).click()
        expect(self.page).to_have_url(f"{self.base_url}/transactions")
