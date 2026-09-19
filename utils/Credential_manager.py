import os
from pathlib import Path
import magic as m 
import json
CREDENTIALS_FILE = Path("app/Credentials/Credentials.json")
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive"
]

REQUIRED_FILE_TYPE = "JSON text data"
def _check_exists(path):
    if not path.exists():
        raise FileNotFoundError(f"Google credential file not found: {path}")

def _check_is_file(path):
    if not path.is_file():
        raise ValueError(f"{path} is not a file")

def _check_not_empty(path):
    if os.path.getsize(path) == 0:
        raise ValueError(f"{path} is an empty file")

def _check_is_json(path):
    file_type = m.from_file(path)
    if file_type != REQUIRED_FILE_TYPE:
        raise TypeError(f"{path} is not of type json (detected: {file_type})")

def _load_json(path) -> dict:
    try:
        with path.open("r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        raise ValueError(f"Credentials file contains invalid JSON: {path}") from e

def _check_required_fields(data: dict):
    required_fields = {"type", "project_id", "private_key", "client_email", "token_uri"}
    missing = required_fields - data.keys()
    if missing:
        raise ValueError(f"Credentials file missing required fields: {sorted(missing)}")


def Credentials_manager(credentials_file=CREDENTIALS_FILE) -> dict:
    _check_exists(credentials_file)
    _check_is_file(credentials_file)
    _check_not_empty(credentials_file)
    _check_is_json(credentials_file)
    data = _load_json(credentials_file)
    _check_required_fields(data)
    return data    
