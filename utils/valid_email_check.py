import re
import logging


class UserManager:
    @staticmethod
    def valid_email_pattern(email: str):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.fullmatch(pattern, email):
            logging.info("the email provided is valid")
        else:
            logging.warning("the email provided doesn't have a valid structure")
