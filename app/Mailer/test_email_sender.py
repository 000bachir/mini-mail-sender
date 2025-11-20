import unittest
from unittest.mock import patch, MagicMock

# from Mailer.sender import EMAIL, EmailStatus,  EmailSender
from .sender import EMAIL, EmailStatus, EmailSender


class TestEmailSender(unittest.TestCase):
    @patch("app.Mailer.sender.yagmail.SMTP")
    def setUp(self, mock_smtp):
        # Initialize EmailSender with logging disabled to keep test output clean
        self.sender = EmailSender()
        # Mock the yagmail instance attached to the class
        self.sender.yagmail = mock_smtp.return_value

    @patch("app.Mailer.sender.DatabaseOperation")
    def test_load_emails_from_database(self, MockDB):
        # Setup mock return
        mock_db_instance = MockDB.return_value
        expected_emails = ["test1@example.com", "test2@example.com"]
        mock_db_instance.FetchEmails.return_value = expected_emails

        # Execute
        result = self.sender.load_emails_from_database()

        # Assert
        self.assertEqual(result, expected_emails)
        mock_db_instance.FetchEmails.assert_called_once()

    def test_saving_emails_in_queue(self):
        email_list = ["email1", "email2"]

        # Execute
        queue_result = self.sender.saving_emails_in_queue(email_list)

        # Assert
        self.assertFalse(queue_result.empty())
        self.assertEqual(queue_result.qsize(), 2)

    @patch("app.Mailer.sender.EmailManager")
    def test_send_single_email_success(self, MockEmailManager):
        # Setup
        email_obj = EMAIL(to="user@test.com", subject="Hi", body="Body")

        # Mock Validation to return False (meaning NO invalid pattern found based on your logic)
        # Logic source: checks if pattern(email) is True, then fails.
        MockEmailManager.return_value.valid_email_pattern.return_value = False

        # Execute
        result = self.sender.send_single_email(email_obj)

        # Assert
        self.assertTrue(result)
        self.assertEqual(email_obj.status, EmailStatus.SUCCESS)
        self.sender.yagmail.send.assert_called_once()

    # @patch("tests.Path")
    # def test_validate_email_with_attachment(self, MockPath):
    #     # Setup
    #     email_obj = EMAIL(to="u", subject="s", body="b", attachments=["resume.pdf"])
    #
    #     # Case: Attachment exists
    #     MockPath.return_value.exists.return_value = True
    #     self.assertTrue(self.sender.validate_email(email_obj))
    #
    #     # Case: Attachment missing
    #     MockPath.return_value.exists.return_value = False
    #     self.assertFalse(self.sender.validate_email(email_obj))
    #


if __name__ == "__main__":
    unittest.main()
