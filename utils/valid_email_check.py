import re
import logging


class EmailManager:
    def __init__(self, enable_loggin_info: bool = True) -> None:
        pass

    @staticmethod
    def valid_email_pattern(email):
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if re.fullmatch(pattern, email):
            logging.info("the email provided is valid")
        else:
            logging.warning("the email provided doesn't have a valid structure")
