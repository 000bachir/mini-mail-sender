from __future__ import annotations
import datetime
from datetime import datetime
import logging
from pathlib import Path
from re import sub
from configuration.config import loading_env_variables
import yagmail
from typing import Any, Dict, Never, Optional, List, Union
from enum import Enum
from dataclasses import asdict, dataclass
from app.supabase.supabaseClient import DatabaseOperation
from queue import Queue
from utils.valid_email_check import EmailManager
from utils.normalize_recipients import normalize_recipients


"""
yagmail logic handler
"""

# credentials
email = loading_env_variables("EMAIL")
app_password = loading_env_variables("GMAIL_APP_PASSWORD")

# TODO : ADD STRING PATH FOR THE RESUME TO BE SENT
attachement = "../assets/global english.pdf"


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

    to: Optional[Union[str, List[str]]]
    subject: str
    body: str
    cc: Optional[Union[str, List[str]]] = None
    bcc: Optional[Union[str, List[str]]] = None
    priority: EmailPriority = EmailPriority.NORMAL
    status: EmailStatus = EmailStatus.PENDING
    created_at: Optional[str] = None
    scheduled_for: Optional[str] = None
    sent_at: Optional[Union[str, datetime]] = None
    retry_count: int = 0
    max_retries: int = 4
    error_message: Optional[str] = None
    email_id: Optional[str] = None
    attachments: Optional[str] = None

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
        self.logger = logging.getLogger(__name__)
        if enable_loggin:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        else:
            self.logger.setLevel(logging.CRITICAL + 1)

        """
            yagmail init process 
        """
        try:
            self.yagmail = yagmail.SMTP(email_user, email_app_password)
            self.logger.info("the initiation was correctly done\n")
        except Exception as e:
            self.logger.error(
                f"error the initiation could not proccede correctly : {e}\n"
            )
            raise

    def load_emails_from_database(self):
        db_operations = DatabaseOperation()
        try:
            loading_email_from_supabse = db_operations.fetch_all_emails()
            if not loading_email_from_supabse:
                self.logger.warning("couldn't load emails form the database\n")
                return []
            return loading_email_from_supabse
        except Exception as e:
            self.logger.error(f"Databse load failed : {e}\n")
            raise RuntimeError(f"failed to load from the database {e}") from e

    def validate_email_structure(self, email: EMAIL) -> bool:
        try:
            if not isinstance(email, EMAIL):
                return False
            email_to = normalize_recipients(email.to)
            if not email_to:
                self.logger.warning(f"missing the 'to' field on {email.email_id}\n ")
                return False
            if not email.subject or not email.subject.strip():
                self.logger.warning(f"missing the 'subject' in {email.email_id}\n")
                return False

            if not email.body or not email.body.strip():
                self.logger.warning(f"missing 'body' field {email.email_id}\n")
                return False
            if email.attachments:
                for attachement in email.attachments:
                    if not Path(attachement).exists():
                        self.logger.warning(
                            "no attachement has been added by the user\n"
                        )
                        return False
                    else:
                        self.logger.info("found email attachement\n")
            return True

        except Exception as e:
            self.logger.error(
                f"the validate_email_structure funcition crashed please check the error : {e}\n"
            )
            raise

    def saving_emails_in_queue(self, emails: List[EMAIL]):
        try:
            queue_init = Queue()
            if queue_init.empty():
                self.logger.info("the queue is empty and ready to receive emails\n")
            for email in emails:
                queue_init.put(email)
            return queue_init
        except Exception as e:
            self.logger.error(
                f"error could not save emails to the database check error: {e}\n"
            )
            raise RuntimeError

    def send_single_email(self, email: EMAIL) -> bool:
        # normalize first so email.to can be str or List[str]
        recipient_list = normalize_recipients(email.to)

        if not recipient_list:
            self.logger.error("no recipient provided\n")
            email.status = EmailStatus.FAILED
            email.error_message = "no recipient"
            return False

        # validate each address once
        email_manager = EmailManager()
        # for r in recipient_list:
        # if not email_manager.valid_email_pattern(r):
        #     self.logger.error(f"invalid email address: {r}\n")
        #     email.status = EmailStatus.FAILED
        #     email.error_message = f"invalid address: {r}"
        #     return False
        #
        self.logger.info(
            f"starting send to {email.to} — max retries: {email.max_retries}\n"
        )

        while email.retry_count < email.max_retries:
            try:
                self.yagmail.send(
                    to=email.to,
                    subject=email.subject,
                    contents=email.body,
                    attachments=email.attachments if email.attachments else None,
                    cc=email.cc,
                    bcc=email.bcc,
                )
                email.status = EmailStatus.SUCCESS
                email.priority = EmailPriority.NORMAL
                email.sent_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.logger.info(f"email sent successfully to {email.to}\n")
                return True

            except Exception as e:
                email.retry_count += 1
                email.status = EmailStatus.RETRYING
                email.error_message = str(e)
                self.logger.warning(
                    f"attempt {email.retry_count}/{email.max_retries} failed for {email.to}: {e}\n"
                )

        email.status = EmailStatus.FAILED
        self.logger.error(
            f"all {email.max_retries} attempts exhausted for {email.to}\n"
        )
        return False
