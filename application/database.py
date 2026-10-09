from sqlalchemy import event

from application.extensions import db


class _ExactCentsSum:
    def __init__(self):
        self.total = 0

    def step(self, amount_cents):
        if amount_cents is not None:
            self.total += amount_cents

    def finalize(self):
        # Text preserves totals beyond SQLite's integer limit.
        return str(self.total)


def _register_sqlite_aggregates(connection, connection_record):
    connection.create_aggregate("sum_cents", 1, _ExactCentsSum)


def init_database_functions(app):
    with app.app_context():
        engine = db.engine

        if engine.dialect.name == "sqlite":
            event.listen(engine, "connect", _register_sqlite_aggregates)
