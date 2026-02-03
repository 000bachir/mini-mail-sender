from __future__ import annotations
import sys
import signal
import argparse
import logging
from datetime import datetime, timedelta
from pathlib import Path
from queue import Queue
from time import strftime

# class imports
from app.Mailer.sender import EmailSender
from app.scheduler.scheduler import EmailScheduler
from app.supabase.supabaseClient import DatabaseOperation


class EmailCampainManager:
    def __init__(
        self,
        enable_logging: bool = True,
        dry_run: bool = False,
        resume_from_failure: bool = True,
    ):
        self.dry_run = dry_run
        self.resume_from_failure = resume_from_failure

        if enable_logging:
            logging.basicConfig(
                level=logging.INFO,
                format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                handlers=[
                    logging.FileHandler(
                        f"email campain {datetime.now().strftime('%Y/%m/%d_%H:%M:S')}.log"
                    ),
                    logging.StreamHandler(),
                ],
            )
        self.logger = logging.getLogger(__name__)
        # main component init
        self.database = DatabaseOperation()
        self.sender = EmailSender()
        self.Scheduler = EmailScheduler()

        self.metric = {
            "start_time": None,
            "end_time": None,
            "total_sent": 0,
            "failed": 0,
            "skipped": 0,
            "sent": 0,
        }

        # graceful shutdown
        self.shutdown_request = False
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        self.logger.info("EMAIL CAMPAIGN INITIALIZED!!!!!")
