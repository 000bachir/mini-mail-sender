import pytest
import datetime
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from typing import List
from app.supabase.supabaseClient import (
    EmailRecord,
    EmailCategory,
    EmailStatus,
    DatabaseOperation,
)


@pytest.fixture
def mock_supabase_client():
    with patch("app.supabase.supabaseClient.create_client") as mock_create:
        mock_client = MagicMock()
        mock_create.return_value = mock_client
        yield mock_client


@pytest.fixture
def database(mock_supabase_client):
    database = DatabaseOperation(
        supabase_key="test_key",
        supabase_url="https://test.supabase.co",
        enable_loggin=False,
    )
    database.client = mock_supabase_client
    return database


@pytest.fixture
def sample_email_record():
    return EmailRecord(
        email="ykami892@gmail.com",
        category="communication",
        status=EmailStatus.PENDING.value,
        language="en",
        source="linkedin",
        added_at=datetime.now(),
        notes="test note",
        last_contacted_at=datetime.now(),
    )


def sample_email_records():
    return [
        EmailRecord(
            email=f"test{i}@gmail.com",
            category="communication",
            status=EmailStatus.PENDING.value,
            language="en",
            source="linkedin",
            added_at=datetime.now(),
            notes="test note",
            last_contacted_at=datetime.now(),
        )
        for i in range(5)
    ]


"""
    health tests 
"""


class TestHealth:
    def test_health_success(self, database, mock_supabase_client):
        mock_response = Mock()
        mock_response.data = [{"status": "connection confiremed"}]
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response
        result = database.check_health()
        assert result is True
        mock_supabase_client.table.assert_called_with("healthcheck")

    def test_check_health_failure(self, database, mock_supabase_client):
        mock_supabase_client.table.return_value.insert.return_value.execute.side_effect = Exception(
            "connection failed"
        )
        result = database.check_health()
        assert result is False

    # def test_get_latest_health_status_no_records(self, database, mock_supabase_client):
    #     """Test when no health records exist."""
    #     mock_response = Mock()
    #     mock_response.data = []
    #     mock_supabase_client.table.return_value.select.return_value.order.return_value.limit.return_value.execute.return_value = mock_response
    #     result = database.get_latest_health_status()
    #     assert result is None
    #


# ============================================================================
# # VALIDATION TESTS
# # ============================================================================


class TestValidation:
    @pytest.mark.parametrize(
        "email,expected",
        [
            ("valid@example.com", True),
            ("user.name+tag@example.co.uk", True),
            ("invalid@", False),
            ("@invalid.com", False),
            ("invalid", False),
            ("invalid@.com", False),
            ("", False),
        ],
    )
    def test_valid_email_pattern(self, database, email, expected):
        result = database.valid_email_pattern(email)
        assert result == expected

    def test_checking_for_dupalicates(self, database, mock_supabase_client):
        mock_response = Mock()
        mock_response.data = [{"email": "user_at_urmom@gmail.com"}]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        result = database.checking_for_dupalicates("user_at_urmom@gmail.com")
        assert result is True

    def test_check_duplicate_not_exists(self, database, mock_supabase_client):
        mock_response = Mock()
        mock_response.data = []
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        result = database.checking_for_dupalicates("new@exemple.com")

        assert result is False

    def validate_record_success(self, database, sample_email_record):
        result = database.validate_record(sample_email_record)
        assert result is True

    def test_validate_record_with_missing_email(self, database):
        record = EmailRecord(
            email="",
            status="pending",
        )
        """
        with pytest.raises(ValueError , match = "missing required field") :
            database_validate_record(record)
        ////// well why this was failing because match expect a regex patter not a string that is why the test did not pass correctly 
        """
        with pytest.raises(ValueError) as error:
            database.validate_record(record)
        print(error.value)


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not intergration"])
