# ========================
# Variables
# ========================
PYTHON=python
PYTEST=pytest
APP_MODULE=app.src.main
APP_FILE=app/src/main.py

# ========================
# Run commands
# ========================

run:
	PYTHONPATH=. $(PYTHON) -m $(APP_MODULE)

flet:
	PYTHONPATH=. flet run --recursive $(APP_FILE)

server:
	PYTHONPATH=. fastapi dev $(APP_FILE)

# ========================
# Tests
# ========================

test:
	PYTHONPATH=. $(PYTEST)

test-main:
	PYTHONPATH=. $(PYTEST) app/src/test_main.py

test-mailer:
	PYTHONPATH=. $(PYTEST) app/Mailer/test_email_sender.py

test-supabase:
	PYTHONPATH=. $(PYTEST) app/supabase/test_supabase_client.py

test-scheduler:
	PYTHONPATH=. $(PYTEST) app/scheduler/test_scheduler.py

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
	pip install -r requirements.txt

format:
	black .

lint:
	ruff .
