"""
yagmail logic handler
"""

import yagmail
from typing import Optional, List
from config import loading_env_variables


email = loading_env_variables("EMAIL")
app_password = loading_env_variables("GMAIL_APP_PASSWORD")
