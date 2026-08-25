import pytest
from unittest.mock import patch, MagicMock

# import your module (adjust path)
import app.src.main as main_module


# -----------------------------
# Helpers
# -----------------------------
class DummyEmail:
    def __init__(self, to="test@test.com"):
        self.to = to
        self.status = None
        self.sent_at = None


# -----------------------------
# 1. DB health fails
# -----------------------------
@patch("app.src.main.check_health")
def test_main_db_health_fail(mock_check_health):
    mock_check_health.return_value = None

    with pytest.raises(SystemExit) as e:
        main_module.main()

    assert e.value.code == 1


# -----------------------------
# 2. Scheduler fails
# -----------------------------
@patch("app.src.main.run_scheduler_check")
@patch("app.src.main.check_health")
def test_main_scheduler_fail(mock_check_health, mock_scheduler):
    mock_check_health.return_value = MagicMock()
    mock_scheduler.return_value = None

    with pytest.raises(SystemExit) as e:
        main_module.main()

    assert e.value.code == 1


# -----------------------------
# 3. No recipients
# -----------------------------
@patch("app.src.main.load_recipients")
@patch("app.src.main.run_scheduler_check")
@patch("app.src.main.check_health")
def test_main_no_recipients(mock_check_health, mock_scheduler, mock_load):
    mock_check_health.return_value = MagicMock()
    mock_scheduler.return_value = MagicMock()
    mock_load.return_value = []

    with pytest.raises(SystemExit) as e:
        main_module.main()

    assert e.value.code == 1


# -----------------------------
# 4. No valid emails
# -----------------------------
@patch("app.src.main.queue_and_validate")
@patch("app.src.main.EmailSender")
@patch("app.src.main.building_email_object")
@patch("app.src.main.load_recipients")
@patch("app.src.main.run_scheduler_check")
@patch("app.src.main.check_health")
def test_main_no_valid_emails(
    mock_check_health,
    mock_scheduler,
    mock_load,
    mock_build,
    mock_sender_cls,
    mock_queue,
):
    mock_check_health.return_value = MagicMock()
    mock_scheduler.return_value = MagicMock()
    mock_load.return_value = ["test@test.com"]

    mock_build.return_value = [DummyEmail()]

    mock_sender = MagicMock()
    mock_sender_cls.return_value = mock_sender

    mock_queue.return_value = ([], [DummyEmail()])  # no valid emails

    with pytest.raises(SystemExit) as e:
        main_module.main()

    assert e.value.code == 0


# -----------------------------
# 5. Happy path
# -----------------------------
@patch("app.src.main.print_summary")
@patch("app.src.main.send_mails")
@patch("app.src.main.queue_and_validate")
@patch("app.src.main.EmailSender")
@patch("app.src.main.building_email_object")
@patch("app.src.main.load_recipients")
@patch("app.src.main.run_scheduler_check")
@patch("app.src.main.check_health")
def test_main_success(
    mock_check_health,
    mock_scheduler,
    mock_load,
    mock_build,
    mock_sender_cls,
    mock_queue,
    mock_send,
    mock_summary,
):
    # mocks
    mock_db = MagicMock()
    mock_sched = MagicMock()

    mock_check_health.return_value = mock_db
    mock_scheduler.return_value = mock_sched
    mock_load.return_value = ["test@test.com"]

    emails = [DummyEmail()]
    mock_build.return_value = emails

    mock_sender = MagicMock()
    mock_sender_cls.return_value = mock_sender

    mock_queue.return_value = (emails, [])
    mock_send.return_value = (1, 0)

    # run
    main_module.main()

    # assertions
    mock_send.assert_called_once()
    mock_summary.assert_called_once()
