from logging import log
import logging


class GmailAuth:
    def __init__(self, enable_loggin: bool = True) -> None:
        self.logger = logging.getLogger(__name__)
        if enable_loggin:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
            )
        else:
            self.logger.setLevel(Cr)
