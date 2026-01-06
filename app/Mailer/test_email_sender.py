import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime
from queue import Queue
from app.Mailer.sender import EMAIL, EmailPriority, EmailSender, EmailStatus
from configuration.config import loading_env_variables

email_personal = loading_env_variables("EMAIL")
app_password_personal = loading_env_variables("GMAIL_APP_PASSWORD")


@pytest.fixture
def sample_email():
    return EMAIL(
        to="test_email@gmail.com",
        subject="subject of the email",
        body="this is the body of the email",
        email_id="test_1",
    )


@pytest.fixture
def sample_email_attachement(tmp_path):
    test_file = tmp_path / "test.pdf"
    test_file.write_bytes(b"%PDF fake content")

    return EMAIL(
        to="test_email@gmail.com",
        subject="subject of the email",
        body="this is the body of the email",
        email_id="test_1",
        attachments=[str(test_file)],
    )


@pytest.fixture
def mock_yagmail():
    with patch("app.Mailer.sender.yagmail.SMTP") as mock:
        yield mock


@pytest.fixture
def email_sender(mock_yagmail):
    with (
        patch("app.Mailer.sender.email", "test_email@gmail.com"),
        patch("app.Mailer.sender.app_password", "test_password"),
    ):
        sender = EmailSender(enable_loggin=False)
        return sender


class TestEmail:
    def test_email_creation(self):
        email = EMAIL(to="test_subject@gmail.com", subject="test", body="body")
        assert email.to == "test_subject@gmail.com"
        assert email.subject == "test"
        assert email.body == "body"
        assert email.status == EmailStatus.PENDING
        assert email.priority == EmailPriority.NORMAL
        assert email.retry_count == 0

    def test_email_to_dict(self):
        email = EMAIL(to="test_email@gmail.com", subject="test", body="body")
        email_to_dict = email.to_dict()
        assert email_to_dict["to"] == "test_email@gmail.com"
        assert email_to_dict["subject"] == "test"
        assert email_to_dict["body"] == "body"

    def test_email_from_dict(self):
        data = {
            "to": "test@example.com",
            "subject": "Test",
            "body": "Body",
            "priority": "high",
            "status": "sent",
            "attachments": None,
            "cc": None,
            "bcc": None,
            "created_at": None,
            "scheduled_for": None,
            "sent_at": None,
            "retry_count": 0,
            "max_retries": 3,
            "error_message": None,
            "email_id": None,
        }
        email = EMAIL.from_dict(data)
        assert email.to == "test@example.com"
        assert email.priority == EmailPriority.HIGH
        assert email.status == EmailStatus.SENT

    def test_email_with_multiple_recipient(self):
        email = EMAIL(
            to=["first_person@gmail.com", "second_person@gmail.com"],
            subject="test",
            body="body",
        )

        assert isinstance(email.to, list)
        assert len(email.to) == 2


class TestEmailSenderInit:
    def test_initialization_success(self, mock_yagmail):
        with (
            patch("app.Mailer.sender.email", "test_exemple@gmail.com"),
            patch("app.Mailer.sender.app_password", "test_password"),
        ):
            sender = EmailSender(enable_loggin=False)
            assert sender.email_user == email_personal
            assert sender.email_app_password == app_password_personal

    def test_initialization_failure(self, mock_yagmail):
        mock_yagmail.side_effect = Exception("Connection failed\n")
        with (
            patch("app.Mailer.sender.email", "test@exemple.com"),
            patch("app.Mailer.sender.app_password", "test_password"),
            pytest.raises(Exception),
        ):
            EmailSender(enable_loggin=False)


class TestLoadEmailFromDatabase:
    def test_load_email_from_database(self, email_sender):
        mock_emails = [
            {"to": "test1@example.com", "subject": "Test 1", "body": "Body 1"},
            {"to": "test2@example.com", "subject": "Test 2", "body": "Body 2"},
        ]
        with patch("app.supabase.supabaseClient.DatabaseOperation") as mock_db:
            mock_db.return_value.fetch_all_emails.return_value = mock_emails
            result = email_sender.fetch_all_emails()
            assert result == mock_emails
            assert len(result)
