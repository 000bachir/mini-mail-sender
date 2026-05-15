# ========================
# Variables
# ========================

VENV=.venv
PYTHON=$(VENV)/bin/python
PIP=$(VENV)/bin/pip

PYTEST=pytest
APP_MODULE=app.src.main
APP_FILE=app/src/main.py

# ========================
# Run commands
# ========================

run:
	PYTHONPATH=. $(PYTHON) -m $(APP_MODULE)

# ========================
# Hot Reload (Qt-safe)
# ========================
# Uses full process restart instead of in-process reload (IMPORTANT for PySide6)

hot:
	PYTHONPATH=. $(PYTHON) -m watchfiles "$(PYTHON) -m $(APP_MODULE)" app

# ========================
# Alternative manual run (no reload)
# ========================

run-file:
	PYTHONPATH=. $(PYTHON) $(APP_FILE)

# ========================
# Server (FastAPI)
# ========================

server:
	PYTHONPATH=. $(PYTHON) -m fastapi dev $(APP_FILE)

# ========================
# Tests
# ========================

test:
	PYTHONPATH=. $(PYTHON) -m pytest

test-main:
	PYTHONPATH=. $(PYTHON) -m pytest app/src/test_main.py

test-mailer:
	PYTHONPATH=. $(PYTHON) -m pytest app/Mailer/test_email_sender.py

test-supabase:
	PYTHONPATH=. $(PYTHON) -m pytest app/supabase/test_supabase_client.py

test-scheduler:
	PYTHONPATH=. $(PYTHON) -m pytest app/scheduler/test_scheduler.py

# ========================
# Cleanup
# ========================

clean:
	find . -type d -name "__pycache__" -exec rm -r {} +
	find . -type f -name "*.pyc" -delete

# ========================
# Helpers
# ========================

install:
	$(PIP) install -r requirements.txt

format:
	$(PYTHON) -m black .

lint:
	$(PYTHON) -m ruff .
