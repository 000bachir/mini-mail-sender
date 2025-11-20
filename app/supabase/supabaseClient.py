"""
supabase integration
"""

from dataclasses import asdict
import datetime
from postgrest import CountMethod
from realtime import dataclass
from supabase import Client, create_client
from configuration.config import loading_env_variables
from typing import Any, Dict, Union
import logging
from utils.valid_email_check import EmailManager
from enum import Enum

#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""


@dataclass
class EmailRecord:
    email: str
    added_at: Union[datetime.datetime, str]
    last_contacted_at: Union[datetime.datetime, str]
    status: str = ""  # en attente , en cours d'envoie , operation fini
    full_name: str = ""
    category: str = ""
    language: str = ""
    source: str = ""
    notes: str = ""

    def _to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class EmailCategory:
    TEACHING = "teaching"
    TECH = "tech"
    COMMUNICATION = "communication"
    SUPPORT = "support"
    OTHER = "other"


class EmailStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SUCCESS = "success"
    SCHEDULED = "scheduled"
    RETRYING = "retrying"


class DatabaseOperation:
    def __init__(
        self,
        table_name: str = "emails",
        supabase_url: str = url,
        supabase_key: str = key,
        enable_loggin: bool = True,
    ):
        self.client: Client = create_client(supabase_url, supabase_key)
        self.table_name = table_name
        # logging setup
        if enable_loggin:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        self.logger = logging.getLogger(__name__)
        self.logger.info("database operation class initiated with success\n")

    """
        checking the health of the database
    """

    def get_timestamps(self):
        return datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%S")

    def check_health(self):
        timestamp = self.get_timestamps()
        try:
            self.client.table("healthcheck").insert(
                {"status": "connection confirmed", "timestamp": timestamp}
            ).execute()
            self.logger.info("health check passed correctly\n")
            return True
        except Exception as e:
            self.client.table("healthcheck").insert(
                {
                    "status": "failed to check the database health",
                    "timestamp": timestamp,
                }
            ).execute()
            self.logger.error(f"could not chekc the database health cause : {e}\n")
            return False

    """

    checking the connection

    """

    def get_latest_health_status(self):
        try:
            response_check = (
                self.client.table("healthcheck")
                .select("*")
                .order("timestamp", desc=True)
                .limit(1)
                .execute()
            )
            if response_check.data:
                latest = response_check.data[0]
                self.logger.info(f"status: {latest['status']} at {latest['timestamp']}")
                return latest
            self.logger.warning("no health check found in the database")
            return False
        except Exception as e:
            self.logger.error(
                f"check failed , the database is not working correctly please check the cause : {e}\n"
            )
            raise RuntimeError

    """
        valid email patterns
    """

    # def valid_email_pattern(self, email: str):
    #     pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
    #     if re.fullmatch(pattern, email):
    #         logging.info("the email provided is valid")
    #     else:
    #         logging.warning("the email provided doesn't have a valid structure")
    #
    def checking_for_dupalicates(self, record: EmailRecord) -> bool:
        try:
            duplicate = (
                self.client.table(self.table_name)
                .select("email")
                .eq("email", record.email)
                .execute()
            )
            if duplicate.data:
                self.logger.warning(
                    f"the email provided already exist in the database : {record.email} skipping"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(
                f"failed checking for duplicate in the database please check the error above : {e}"
            )
            raise

    """
        valid email record
    """

    def valid_record_needed(self, record: EmailRecord):
        required_fields = {
            "email": record.email,
            "language": record.language,
            "source": record.source,
            "status": record.status,
        }
        for field_name, value in required_fields.items():
            if not value:
                self.logger.error(f"error the field {field_name} is required")
                raise ValueError
        return True

    """
        seeding the database with test emails 
    """

    def insert_email(self, record: EmailRecord):
        try:
            seeding = None
            valid_pattern = EmailManager.valid_email_pattern(
                record.email
            )  # check for valid email pattern
            if not valid_pattern:
                self.logger.error(
                    "error the email format is invalid please check again"
                )
            # check if the required fields are available
            valid_record = self.valid_record_needed(record)
            if not valid_record:
                self.logger.error("error missing required email record")

            duplicates = self.checking_for_dupalicates(record)
            if duplicates:
                self.logger.info(f"email already in the database {record.email}")
                return False

            logging.warning("the process of seeding the database is being initiated")
            # normalizing timestamp
            if isinstance(record.added_at, str):
                record.added_at = datetime.datetime.now().isoformat()
            if isinstance(record.last_contacted_at, str):
                record.last_contacted_at = record.added_at = (
                    datetime.datetime.now().isoformat()
                )
            # seeding = (
            #     self.client.table(self.table_name)
            #     .insert(
            #         {
            #             "email": record.email,
            #             "full_name": record.full_name,
            #             "category": record.category,
            #             "language": record.language,
            #             "source": record.source,
            #             "added_at": record.added_at,
            #             "status": record.status,
            #             "notes": record.notes,
            #             "last_contacted_at": record.last_contacted_at,
            #         }
            #     )
            #     .execute()
            # )
            seeding = (
                self.client.table(self.table_name).insert(record._to_dict()).execute()
            )
            if seeding and seeding.data is not None:
                self.logger.info("email inserted successfully\n")

        except Exception as e:
            self.logger.error(
                f"failed to seed the database with data please check the error :{e}\n"
            )
            raise RuntimeError

    """
        function that will count the number of rows in a database
    """

    def countRows(self):
        try:
            rows = (
                self.client.table("emails")
                .select("*", count=CountMethod.exact)
                .execute()
            )
            logging.info(f"the number of rows in the database are : {rows.count}")
            if rows.count == 0:
                self.logger.info("the database has no rows inside of it")
        except Exception as e:
            self.logger.error(
                f"error could not retreive how many rows are in the database for more info please check the error : {e}"
            )
            raise RuntimeError

    """
        to fetch the emails stored in the database 
    """

    def FetchEmails(self):
        try:
            email_request = self.client.table("emails").select("email").execute()
            if not email_request.data:
                self.logger.error("failed to fetch all of the email from the database")
                return []
            # transforming it into a list for ease of use :
            email_list = [row["email"] for row in email_request.data]
            self.logger.info(
                f"successfuly fetched the emails in a list format of lenght {len(email_list)}\n"
            )
            return email_list

        except Exception as e:
            self.logger.error(
                f"error operating the fetch request onto the database please check the error : {e}"
            )
            raise RuntimeError
