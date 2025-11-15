"""
yagmail logic handler
"""

"""
the mailer logic is gonna need those function : 
    1- create a class of email status 
"""


from config import loading_env_variables
import yagmail
from typing import Dict, Optional, List
from enum import Enum
from typing import Union, Optional, Tuple
from dataclasses import asdict, dataclass
from __future__ import annotations

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
    def __init__(self, enable_loggin: bool = True) -> None:
        pass
