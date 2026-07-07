import logging


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

