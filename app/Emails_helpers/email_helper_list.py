"""
TODO : 
    add_email()

    delete_email()

    update_email()

    get_email()

    get_all_emails()

    schedule_email()

    mark_sent()

    get_pending_emails()

    log_sent_email()
"""



import logging
import magic # this library will auto detect fhe file type no need to manual check for it's header

class EmailHelperMethods : 
    def __init__(self , enable_loggin : bool) -> None:
        self.logger = logging.getLogger(__name__)
        if enable_loggin : 
            logging.basicConfig(
                level=logging.INFO , 
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            self.logger.info("THE HELPER CLASS HAS BEEN INIT")
        else : 
            self.logger.setLevel(logging.CRITICAL + 1)
    def add_email(self) : 
        return
