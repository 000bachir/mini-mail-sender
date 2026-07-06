import logging
import sqlite3
import pytest
from app.LocalDatabase.database import LocalDatabase
import app.LocalDatabase.database as db_module

EXPECTED_TABLE = {
    "emails" , "scheduled_emails" , "sent_logs"
}


@pytest.fixture(autouse=True)

def fresh_db_path(tmp_path , monkeypatch) : 
    test_db = str(tmp_path / "test.db")
    monkeypatch.setattr(db_module , "DATABSE_PATH" , test_db)
    yield test_db


@pytest.fixture
def db() -> LocalDatabase : 
    return LocalDatabase(enable_loggin=False)
#constructor 
class TestConstructor:
    def test_logging_disabled_silences_logger(self):
        instance = LocalDatabase(enable_loggin=False)
        assert instance.logger.level == logging.CRITICAL + 1

    def test_logging_enabled_does_not_raise(self):
        LocalDatabase(enable_loggin=True)


class TestGetConn : 
    def test_row_factory_is_set(self , db) : 
        with db.get_conn() as conn : 
            assert conn.row_factory == sqlite3.Row

    def test_wal_mode_enabled(self , db) : 
        with db.get_conn() as conn : 
            mode = conn.execute("PRAGMA journal_mode").fetchone()[0]
        assert mode == "wal"


    def test_foreign_keys_enabled(self , db) : 
        with db.get_conn() as conn : 
            fk = conn.execute("PRAGMA foreign_keys").fetchone()[0]
        assert fk == 1
    def test_connection_closed(self , db) : 
        with db.get_conn() as conn : 
            captuerd = conn
        with pytest.raises(Exception) : 
            captuerd.execute("SELECT 1")


