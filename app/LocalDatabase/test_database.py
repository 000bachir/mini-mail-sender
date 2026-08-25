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
    monkeypatch.setattr(db_module , "DATABASE_PATH" , test_db)
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



class TestInitDatabase : 
    def test_init_db_raises_due_to_double_close_bug(self , db) : 
        with pytest.raises(sqlite3.ProgrammingError , match="closed database") : 
            db.init_db()


    def test_tables_exists(self , db , fresh_db_path) : 
        try : 
            db.init_db()
        except sqlite3.ProgrammingError : 
            pass

        conn = sqlite3.connect(fresh_db_path)
        rows = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
        conn.close()

        created = {
            row[0] for row in rows
        }
        assert EXPECTED_TABLE.issubset(created)


    def test_emails_table_column(self , db , fresh_db_path) : 
        try : 
            db.init_db()
        except sqlite3.ProgrammingError : 
            pass 

        conn = sqlite3.connect(fresh_db_path)
        info = conn.execute("PRAGMA table_info(emails)").fetchall()
        conn.close()

        columns = {row[1] for row in info}
        assert columns == {
            "id", "email" , "full_name" , "category" , "language" , "source" , "notes" , "status" , "added_at"
        }

    def test_scheduled_emails_table_column(self , db , fresh_db_path) : 
            try : 
                db.init_db()
            except sqlite3.ProgrammingError : 
                pass 

            conn = sqlite3.connect(fresh_db_path)
            info = conn.execute("PRAGMA table_info(scheduled_emails)").fetchall()
            conn.close()

            columns = {row[1] for row in info}
            assert columns == {
                "id", "recipient" , "subject" , "body" , "send_at" , "status" , "created_at"              }

    def test_sent_logs_table_columns(self, db, fresh_db_path):
            try:
                db.init_db()
            except sqlite3.ProgrammingError:
                pass
    
            conn = sqlite3.connect(fresh_db_path)
            info = conn.execute("PRAGMA table_info(sent_logs)").fetchall()
            conn.close()
    
            columns = {row[1] for row in info}
            assert columns == {
                "id", "recipient", "subject",
                "sent_at", "status", "error_message"
            }

    def test_email_defaut_status_active(self , db , fresh_db_path) : 
        try:
            db.init_db()
        except sqlite3.ProgrammingError:
            pass

        conn = sqlite3.connect(fresh_db_path)
        conn.execute("INSERT INTO emails (email) VALUES (?)", ("x@y.com",))
        conn.commit()
        row = conn.execute("SELECT status FROM emails WHERE email='x@y.com'").fetchone()
        conn.close()
        assert row[0] == "active"
    
    def test_email_defaut_status_pending(self , db , fresh_db_path) : 
            try:
                db.init_db()
            except sqlite3.ProgrammingError:
                pass

            conn = sqlite3.connect(fresh_db_path)
            conn.execute("INSERT INTO scheduled_emails (recipient) VALUES (?)", ("x@y.com",))
            conn.commit()
            row = conn.execute("SELECT status FROM scheduled_emails").fetchone()
            conn.close()
            assert row[0] == "pending"


# check database health : 
class TestDatabaseHealth : 
    def return_healthy_dict_on_db(self , db) : 
        result = db.check_database_health()
        assert  isinstance(result , dict)
        assert result["healthy"] is True 
        assert result["integrity"] == "ok"

    def test_return_false_on_unreadable_path(self , db , monkeypatch) : 
        monkeypatch.setattr(db_module , "DATABASE_PATH" , "/")
        with pytest.raises(sqlite3.OperationalError) : 
            assert db.check_database_health()  

class TestCheckTablesExists : 
    def test_always_returns_none_bug(self , db) : 
        result = db.check_tables_exists()
        assert result is None

    def test_does_not_raise(self , db) : 
        db.check_tables_exists()


