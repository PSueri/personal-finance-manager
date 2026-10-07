import unittest

from application import create_app
from application.extensions import db


class DatabaseTestCase(unittest.TestCase):
    APP_CONFIG = {}

    def setUp(self):
        config = {
            "TESTING": True,
            "SECRET_KEY": "test-only-secret",
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": True,
        }
        config.update(self.APP_CONFIG)

        self.app = create_app(config)

        self.context = self.app.app_context()
        self.context.push()

        self.addCleanup(self.context.pop)
        self.addCleanup(db.session.remove)

        db.create_all()
        self.addCleanup(db.drop_all)

        self.client = self.app.test_client()