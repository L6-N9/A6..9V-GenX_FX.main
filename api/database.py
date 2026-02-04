import sqlite3


def get_db():
    """
    FastAPI dependency to get a database connection for each request.
    """
    db = sqlite3.connect("genxdb_fx.db", check_same_thread=False)
    db.row_factory = sqlite3.Row
    try:
        yield db
    finally:
        db.close()
