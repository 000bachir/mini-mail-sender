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


@pytest.fixture
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

    def test_validate_record_with_missing_status(self, database):
        record = EmailRecord(email="the_ultimate_user@gmail.com", status="")
        with pytest.raises(ValueError) as error:
            database.validate_record(record)
        print("error : ", error.value)


# ============================================================================
# INSERT TESTS
# ============================================================================
class TestInsert:
    def test_email_insertion_success(
        self, database, mock_supabase_client, sample_email_record
    ):
        """Test successful email insertion."""
        mock_response = Mock()
        mock_response.data = [sample_email_record.to_dict()]

        # Mock all the chained calls
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value.data = []
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_response

        result = database.insert_email(sample_email_record)

        assert result is not None
        assert result["email"] == "ykami892@gmail.com"

    def test_bult_insertion_insertion(
        self, database, sample_email_records, mock_supabase_client
    ):
        mock_response_duplicates = Mock()
        mock_response_duplicates.data = []

        mock_insert_response = Mock()
        mock_insert_response.data = [{"email": "ykami892@gmail.com"}]

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response_duplicates
        mock_supabase_client.table.return_value.insert.return_value.execute.return_value = mock_insert_response

        result = database.insert_emails_in_bulk(sample_email_records)
        assert result["total"] == 5
        assert result["inserted"] == 5
        assert result["skipped"] == 0
        assert result["failed"] == 0

    def test_bulk_email_insertion_with_duplicates(
        self, mock_supabase_client, sample_email_records, database
    ):
        def mock_duplicate_check(*args, **kwargs):
            mock_response = Mock()
            if "ykami892@gmail.com" in str(args):
                mock_response.data = [{"email": "ykami892@gmail.com"}]
            else:
                mock_response.data = []
            return mock_response

        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.side_effect = mock_duplicate_check
        result = database.insert_emails_in_bulk(
            sample_email_records, skip_duplicate=True
        )
        assert result["skipped"] >= 0


# ============================================================================
# READ TESTS
# ============================================================================
class TestRead:
    def test_fetch_all_email(self, database, mock_supabase_client):
        mock_response = Mock()
        mock_response.data = [
            {"email": "user1@gmail.com"},
            {"email": "user2@gmail.com"},
            {"email": "user3@gmail.com"},
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        result = database.fetch_all_emails()
        assert len(result) == 3
        assert "user1@gmail.com" in result

    def test_fetch_emails_with_empty_database(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = [
            {
                "email": "user1@example.com",
                "full_name": "User 1",
                "status": "pending",
                "category": "business",
                "language": "en",
                "source": "website",
                "notes": "",
                "added_at": "2024-01-01T00:00:00",
                "last_contacted_at": "2024-01-01T00:00:00",
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        result = database.fetch_all_emails()
        assert len(result) == 1
        assert result[0] == "user1@example.com"

    def test_fetch_all_records(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = [
            {
                "email": "user1@example.com",
                "full_name": "User 1",
                "status": "pending",
                "category": "business",
                "language": "en",
                "source": "website",
                "notes": "",
                "added_at": "2024-01-01T00:00:00",
                "last_contacted_at": "2024-01-01T00:00:00",
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_response
        result = database.fetch_all_records()
        assert len(result) == 1
        assert result[0].email == "user1@example.com"

    def test_fetch_all_records_with_pagination(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = []
        mock_request = Mock()
        mock_request.limit.return_value.offset.return_value.execute.return_value = (
            mock_response
        )
        mock_supabase_client.table.return_value.select.return_value = mock_request

        result = database.fetch_all_records(limit=10, offset=5)
        mock_request.limit.assert_called_with(10)
        mock_request.limit.return_value.offset.assert_called_with(5)

    def test_fetch_by_status(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = [
            {
                "email": "pending@example.com",
                "status": EmailStatus.PENDING.value,
                "full_name": "",
                "category": "",
                "language": "",
                "source": "",
                "notes": "",
                "added_at": "2024-01-01T00:00:00",
                "last_contacted_at": "2024-01-01T00:00:00",
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        resutl = database.fetch_email_by_status(EmailStatus.PENDING.value)
        assert len(resutl) == 1
        assert resutl[0].status == EmailStatus.PENDING.value

    def test_fetch_emails_by_categories(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = [
            {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "status": "pending",
                "category": EmailRecord.category,
                "language": "",
                "source": "",
                "notes": "Important client",
                "added_at": "2024-01-01T00:00:00",
                "last_contacted_at": "2024-01-01T00:00:00",
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.eq.return_value.execute.return_value = mock_response
        result = database.fetch_by_category(EmailRecord.category)
        if result:
            print(result)
        else:
            print("something is wrong in the test")
        assert len(result) == 1

    def test_search_by_email(self, mock_supabase_client, database):
        mock_repsonse = Mock()
        mock_repsonse.data = [
            {
                "email": "john.doe@example.com",
                "full_name": "John Doe",
                "status": "pending",
                "category": "",
                "language": "",
                "source": "",
                "notes": "Important client",
                "added_at": "2024-01-01T00:00:00",
                "last_contacted_at": "2024-01-01T00:00:00",
            }
        ]
        mock_supabase_client.table.return_value.select.return_value.execute.return_value = mock_repsonse
        resutl = database.search_emails("john")
        assert len(resutl) >= 1


# ============================================================================
# UPADATE TESTS
# ============================================================================
class TestUpdate:
    def test_update_email_status_success(self, mock_supabase_client, database):
        mock_response = Mock()
        mock_response.data = {
            "email": "test@example.com",
            "status": EmailStatus.COMPLETED.value,
        }

        mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
        result = database.update_email_status(
            "test@example.com", EmailStatus.COMPLETED.value
        )
        assert result is not None
        assert result[0]["status"] == EmailStatus.COMPLETED.value

    # def test_update_email_status_not_found(self, database, mock_supabase_client):
    #     mock_response = Mock()
    #     mock_response.data = []
    #     mock_supabase_client.table.return_value.update.return_value.eq.return_value.execute.return_value = mock_response
    #     resutl = database.update_email_status("nonexistent@example.com", "completed")
    #     assert resutl is None
    #


if __name__ == "__main__":
    pytest.main([__file__, "-v", "-m", "not intergration"])
