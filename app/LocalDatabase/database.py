#TODO : CHANGE OF PLANS NOW I NEED TO MAKE THE DATABASE LOCAL IN ORDER FOR TO BE MORE USEFUL
from __future__ import print_function
import logging
import os
import sqlite3
from contextlib import contextmanager
DATABASE_PATH = os.path.join(os.path.dirname(__file__) , "database.db")


class LocalDatabase : 
    def __init__(self , enable_loggin : bool ) -> None:
        self.logger = logging.getLogger(__name__)
        if enable_loggin : 
            logging.basicConfig(
                level= logging.INFO , 
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.logger.info("LOCAL DATABASE CLASS INIT")
        else : 
            self.logger.setLevel(logging.CRITICAL + 1)
    @contextmanager
    def get_conn(self)  : 
        connection = sqlite3.connect(DATABASE_PATH)
        connection.row_factory = sqlite3.Row
        connection.execute("PRAGMA journal_mode=WAL")
        connection.execute("PRAGMA foreign_keys=ON")
        try : 
            yield connection
            connection.commit()
        except Exception : 
            connection.rollback()
            raise
        finally :
            connection.close()

    def init_db(self) : 
        with self.get_conn() as conn :
            #cursor act as messenger between the python code and the database
            cursor = conn.cursor()
            cursor.executescript("""
                CREATE TABLE IF NOT EXISTS emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    email TEXT UNIQUE NOT NULL, 
                    full_name TEXT, 
                    category TEXT, 
                    language TEXT, 
                    source TEXT, 
                    notes TEXT ,
                    status TEXT DEFAULT 'active',
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS scheduled_emails (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    recipient TEXT NOT NULL, 
                    subject TEXT, 
                    body TEXT, 
                    send_at TIMESTAMP, 
                    status TEXT DEFAULT 'pending',
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );

                CREATE TABLE IF NOT EXISTS sent_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT, 
                    recipient TEXT NOT NULL , 
                    subject TEXT , 
                    sent_at TIMESTAMP , 
                    status TEXT , 
                    error_message TEXT
                );
            """)
            conn.commit()
            conn.close()
            self.logger.info("DATABASE ready")


    def check_database_health(self) :
            try : 
                
                with self.get_conn() as connection :
                    connection.execute("SELECT 1")
                    result = connection.execute("PRAGMA integrity_check").fetchone()[0]
                    if result != "ok" : 
                        raise RuntimeError(result)
                    else : 
                        return {
                            "healthy" : True,
                            "tables" : 3 ,
                            "wal_mode" : True,
                            "foreign_keys" : True,
                            "integrity" : "ok",
                        }
            except sqlite3.OperationalError as error : 
                self.logger.error(f"Error the database health has failed : {error}\n")
                raise
    def check_tables_exists(self) : 
        with self.get_conn() as connection : 
            try : 
                tables = ["emails" , "scheduled_emails" , "sent_logs"]
                cursor = connection.cursor()
                cursor.execute("""
                    SELECT name 
                    FROM sqlite_master 
                    WHERE type="table" AND name in ({})
                """.format(','.join('?' * len(tables))) , tables)
            except RuntimeError as e : 
                self.logger.error(f"Error checking if tables exist : {e}\n")



