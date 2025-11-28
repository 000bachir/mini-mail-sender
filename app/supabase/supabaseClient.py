"""
supabase integration
"""

from __future__ import annotations
from dataclasses import asdict
import datetime
import re
from postgrest import CountMethod
from realtime import dataclass
from supabase import Client, create_client
from configuration.config import loading_env_variables
from typing import Any, Dict, List, Optional, Union
import logging
from enum import Enum

#! env var keys
url = loading_env_variables("PROJECT_URL") or ""
key = loading_env_variables("ANON_PUBLIC_KEY") or ""


@dataclass
class EmailRecord:
    email: str
    added_at: Union[datetime.datetime, str, None] = None
    last_contacted_at: Union[datetime.datetime, str, None] = None
    status: str = ""  # en attente , en cours d'envoie , operation fini
    full_name: str = ""
    category: str = ""
    language: str = ""
    source: str = ""
    notes: str = ""

    def _to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> EmailRecord:
        return cls(**data)


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

    # ============================================================================
    # HEALTH CHECK METHODS
    # ============================================================================
    def check_health(self):
        timestamp = self.get_timestamps()
        try:
            self.client.table("healthcheck").insert(
                {"status": "connection confirmed", "timestamp": timestamp}
            ).execute()
            self.logger.info("health check passed correctly\n")
            return True
        except Exception as e:
            # self.client.table("healthcheck").insert(
            #     {
            #         "status": "failed to check the database health",
            #         "timestamp": timestamp,
            #     }
            # ).execute()
            self.logger.error(f"could not chekc the database health cause : {e}\n")
            return False

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

    # ============================================================================
    # VALIDATION METHODS
    # ============================================================================
    def valid_email_pattern(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.fullmatch(pattern, email):
            self.logger.info("the email provided is valid")
            return True
        else:
            self.logger.warning(
                f"the email provided doesn't have a valid structure : {email}"
            )
            return False

    def checking_for_dupalicates(self, email: str) -> bool:
        try:
            duplicate = (
                self.client.table(self.table_name)
                .select("email")
                .eq("email", email)
                .execute()
            )
            if duplicate.data:
                self.logger.warning(
                    f"the email provided already exist in the database : {email} skipping"
                )
                return True
            return False
        except Exception as e:
            self.logger.error(
                f"failed checking for duplicate in the database please check the error above : {e}"
            )
            raise RuntimeError

    """
        valid email record
    """

    def validate_record(self, record: EmailRecord):
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

    # ============================================================================
    # INSERT METHODS
    # ============================================================================
    def insert_email(self, record: EmailRecord):
        try:
            seeding = None
            valid_pattern = self.valid_email_pattern(record.email)
            # check for valid email pattern
            if not valid_pattern:
                self.logger.error(
                    "error the email format is invalid please check again\n"
                )
                return None
            # check if the required fields are available
            valid_record = self.validate_record(record)
            if not valid_record:
                self.logger.error("error missing required email record\n")

            duplicates = self.checking_for_dupalicates(record.email)
            if duplicates:
                self.logger.info(f"email already in the database {record.email}\n")
                return False

            logging.warning("the process of seeding the database is being initiated\n")
            # normalizing timestamp
            if isinstance(record.added_at, str):
                record.added_at = datetime.datetime.now().isoformat()
            if isinstance(record.last_contacted_at, str):
                record.last_contacted_at = record.added_at = (
                    datetime.datetime.now().isoformat()
                )
            # insertation
            seeding = (
                self.client.table(self.table_name).insert(record._to_dict()).execute()
            )
            if seeding and seeding.data is not None:
                self.logger.info("email inserted successfully\n")

        except Exception as e:
            self.logger.error(
                f"failed to insert the database with data please check the error :{e}\n"
            )
            raise RuntimeError

    # ============================================================================
    # COUNT METHODS
    # ============================================================================
    def count_rows_in_database(self):
        try:
            rows = (
                self.client.table("emails")
                .select("*", count=CountMethod.exact)
                .execute()
            )
            logging.info(f"the number of rows in the database are : {rows.count}\n")
            if rows.count == 0:
                self.logger.info("the database has no rows inside of it\n")
        except Exception as e:
            self.logger.error(
                f"error could not retreive how many rows are in the database for more info please check the error : {e}\n"
            )
            raise RuntimeError

    # ============================================================================
    # FETCH METHODS
    # ============================================================================
    def fetch_all_emails(self):
        try:
            email_request = self.client.table(self.table_name).select("email").execute()
            if not email_request.data:
                self.logger.error(
                    "failed to fetch all of the email from the database\n"
                )
                return []
            # transforming it into a list for ease of use :
            email_list = [row["email"] for row in email_request.data]
            self.logger.info(
                f"successfuly fetched the emails in a list format of lenght {len(email_list)}\n"
            )
            return email_list

        except Exception as e:
            self.logger.error(
                f"error operating the fetch request onto the database please check the error : {e}\n"
            )
            raise RuntimeError

    def fetch_email_by_status(self, status: str) -> List[EmailRecord]:
        try:
            request = (
                self.client.table(self.table_name)
                .select("*")
                .eq("status", status)
                .execute()
            )
            if not request.data:
                self.logger.error("could not return the status from the database\n")
                return []
            records = []
            for row in request.data:
                record = EmailRecord.from_dict(row)
                records.append(record)
            self.logger.info(f"found the {len(records)} with the status {status}\n")
            return records
        except Exception as e:
            self.logger.error(
                f"error could not fetch the emails based on status please check the logging info : {e}\n"
            )
            raise

    def fetch_by_category(self, category: str) -> List[EmailRecord]:
        try:
            category_request = (
                self.client.table(self.table_name)
                .select("category")
                .eq("category", category)
                .execute()
            )
            if not category_request:
                self.logger.error("no category to fetch\n")
                return []
            category_request_records = []
            for row in category_request_records:
                category_request_record = EmailRecord.from_dict(row)
                category_request_records.append(category_request_record)
            return category_request_records
        except Exception as e:
            self.logger.error(f"error the fetch request failed : {e}\n ")
            raise

    # ============================================================================
    # UPDATE METHODS
    # ============================================================================
    def update_email_status(
        self, new_status: str, email: str
    ) -> Optional[Dict[str, Any]]:
        try:
            update_request = (
                self.client.table(self.table_name)
                .update(
                    {"status": new_status, "last_contacted_at": self.get_timestamps()}
                )
                .eq("email", email)
                .execute()
            )
            if update_request.data:
                self.logger.info(f"status updated :  {new_status} for {email}\n")
                return update_request.data[0]
            self.logger.warning("no record found to update\n")
            return None
        except Exception as e:
            self.logger.error(
                f"failed to procced with the update of the status , error : {e}\n"
            )
            raise

    # ============================================================================
    # DELETE METHODS
    # ============================================================================
    def delete_email(self, email: str) -> bool:
        try:
            delete_email_request = (
                self.client.table(self.table_name).delete().eq("email", email).execute()
            )
            if delete_email_request:
                self.logger.warning(f"email deleted : {email}")
                return True
            else:
                self.logger.info("no record found to delete")
                return False
        except Exception as e:
            self.logger.error(
                f"the deletion process failed please check the error : {e}\n"
            )
            raise

    def delete_email_by_status(self, status: str) -> Optional[Union[int, Any]]:
        try:
            delete_email_by_status_request = (
                self.client.table(self.table_name)
                .delete()
                .eq("email", EmailRecord.email)
                .execute()
            )
            count = (
                len(delete_email_by_status_request.data)
                if delete_email_by_status_request.data
                else 0
            )
            self.logger.info(f"Deleted {count} emails with status '{status}'")
            return count
        except Exception as e:
            self.logger.error(
                f"the deletion process failed please check the error : {e}\n"
            )
            raise

    def delete_email_by_category(self, category: str) -> Optional[Union[int, Any]]:
        try:
            delete_email_by_category = (
                self.client.table(self.table_name)
                .delete()
                .eq("category", category)
                .execute()
            )
            count = (
                len(delete_email_by_category.data)
                if delete_email_by_category.data
                else 0
            )
            self.logger.warning(f"deleted {count} emails with category : {category} ")
            return count
        except Exception as e:
            self.logger.error(
                f"error could not proceede with the deletion by category see error : {e}"
            )
            raise
