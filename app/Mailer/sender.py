from __future__ import annotations
import logging

from yagmail import password
from config import loading_env_variables
import yagmail
from typing import Dict, Optional, List, Union
from enum import Enum
from dataclasses import asdict, dataclass
from supabase.supabaseClient import UserManager, DatabaseOperation
from queue import Queue

"""
yagmail logic handler
"""

"""
the mailer logic is gonna need those function : 
    1- create a class of email status ==== done 
    2- create a class that will hold the state of the emails if done correctly or not ==== done 
    3- create a function that will load emails from the database ( for this i gotta use function from other classes )
"""


# credentials
email = loading_env_variables("EMAIL")
app_password = loading_env_variables("GMAIL_APP_PASSWORD")


class EmailStatus(Enum):
    PENDING = "pending"
    SENT = "sent"
    FAILED = "failed"
    SUCCESS = "success"
    SCHEDULED = "scheduled"
    RETRYING = "retrying"


class EmailPriority(Enum):
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"


@dataclass
class EMAIL:
    """EMAIL STRUCTURE"""

    to: Union[str, List[str]]
    subject: str
    body: str
    attachments: Optional[List[str]] = None
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.PENDING
    created_at: Optional[str] = None
    scheduled_for: Optional[str] = None
    sent_at: Optional[str] = None
    retry_count: int = 0
    max_retries: int = 3
    error_message: Optional[str] = None
    email_id: Optional[str] = None

    def to_dict(self) -> Dict:
        # convert for dict for json serialization
        data = asdict(self)
        # dict indexing
        data["priority"] = self.priority.value
        # dict indexing
        data["status"] = self.status.value
        return data

    @classmethod
    def from_dict(cls, data: Dict) -> EMAIL:
        data["priority"] = EmailPriority(data["priority"])
        data["status"] = EmailStatus(data["status"])
        return cls(**data)


class EmailSender:
    def __init__(
        self,
        email_user: Union[str, None] = email,
        email_app_password: Union[str, None] = app_password,
        enable_loggin: bool = True,
    ) -> None:
        self.email_user = email_user
        self.email_app_password = email_app_password

        if enable_loggin:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
            self.logger = logging.getLogger(__name__)

        """
            yagmail init process 
        """
        try:
            self.yagmail = yagmail.SMTP(email_user, email_app_password)
            self.logger.info("the initiation was correctly done")
        except Exception as e:
            self.logger.error(
                f"error yagmail and user email and password did not initiated correctly : {e}"
            )

    def load_emails_from_database(self):
        db_operations = DatabaseOperation()
        try:
            loading_email_from_supabse = db_operations.FetchEmails()
            if not loading_email_from_supabse:
                self.logger.warning("couldn't load emails form the database")
                return []
            return loading_email_from_supabse
        except Exception as e:
            self.logger.error(
                f"error during the operation of loading emails from the database : {e}"
            )
            raise RuntimeError

    def saving_emails_in_queue(self, emails: List[str]):
        try:
            queue_init = Queue()
            if queue_init.empty():
                self.logger.info("the queue is empty and ready to receive emails")
            for email in emails:
                queue_init.put(email)
            return queue_init
        except Exception as e:
            self.logger.error(f"error something bad happened : {e}")
            raise RuntimeError
