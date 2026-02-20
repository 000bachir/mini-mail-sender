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
from app.Mailer.sender import EMAIL, EmailPriority, EmailSender, EmailStatus
from app.scheduler.scheduler import EmailScheduler
from app.supabase.supabaseClient import DatabaseOperation, EmailRecord


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

    def signal_handler(self, signum, fname):
        self.logger.warning(f"\nReceived signal {signum} , starting graceful shutdown")
        self.shutdown_request = True

    def helth_check_the_database(self) -> bool:
        self.logger.info("Performing a health check test")
        if not self.database.check_health():
            self.logger.error("ERROR : the database health check failed")
            return False
        if not self.Scheduler.checking_buisness_hours():
            self.logger.error("outside buisness hours all emails will be delayed\n")
            return False
        self.logger.info("ALL health check passed")
        return True

    def load_email_from_database(self):
        self.logger.info("loading emails from databese\n")
        pending_email = self.database.fetch_email_by_status(EmailStatus.PENDING.value)
        if self.resume_from_failure:
            failed_record = self.database.fetch_email_by_status(
                EmailStatus.FAILED.value
            )
            pending_email.extend(failed_record)
            self.logger.info(f"loaded {len(failed_record)} failed emails to retry ")

    def convert_record_to_emails(self, record: EmailRecord) -> EMAIL:
        return EMAIL(
            to=record.email,
            subject=f"application for {record.category} position",
            body=self._generate_body_email(record),
            attachments=["../assets/global english.pdf"],
            priority=EmailPriority.NORMAL,
            status=EmailStatus.PENDING,
            email_id=record.email,
        )

    def _generate_body_email(self, record: EmailRecord) -> str:
        """Generate personalized email body based on recipient data"""
        # Customize this based on your needs
        greeting = (
            f"Dear {record.full_name}" if record.full_name else "Dear Hiring Manager"
        )
        body = f"""
        {greeting},
        I hope this email finds you well. I am writing to express my interest in opportunities 
        within your {record.category} department.

        [Your personalized message here based on category: {record.category}]

        Please find my resume attached for your review.

        Best regards,
        [Your Name]
                """
        return body.strip()

    def process_email_in_queue(self, email_queue: Queue) -> None:
        self.metric["start_time"] = datetime.now()
        self.metric["total_emails"] = email_queue.qsize()
        self.logger.info(f"starting to process {self.metric['total_emails']} emails\n")
        if not self.Scheduler.checking_buisness_hours():
            delay = self.Scheduler.add_random_delay_after_init()
            self.logger.info(
                f"adding random delay {delay} (outside of buisness hours) "
            )
            if not self.dry_run:
                import time

                time.sleep(delay.total_seconds())
        while not email_queue.empty() and not self.shutdown_request:
            hourly_ok, hourly_msg = self.Scheduler.check_hourly_email_rate_limit()
            daily_ok, daily_msg = self.Scheduler.check_daily_email_rate_limit()
            if not hourly_ok:
                self.logger.warning(hourly_msg)
                self.logger.info("hourly limit reached waiting 1 hour")
                if not self.dry_run:
                    import time

                    time.sleep(3600)
                continue
            if not daily_ok:
                self.logger.warning(daily_msg)
                self.logger.info("daily email limit reached program will stop ")
                break
            email = email_queue.get()
            try:
                if not self.sender.validate_email_structure(email):
                    self.logger.error(f"invalid email structure for {email.email.id}")
                    self.metric["skipped"] = +1
                    self._upadate_database_status(
                        email.email_id, EmailStatus.FAILED, "invalid structure"
                    )
                    continue

                if self.dry_run:
                    self.logger.info(f"email sent to {email.to}")
                    success = True
                else:
                    success = self.sender.send_single_email(email)

                if success:
                    self.metric["sent"] += 1
                    self.Scheduler.email_sent_during_an_hour += 1
                    self.Scheduler.email_sent_during_a_day += 1
                    self._upadate_database_status(email.email.id, EmailStatus.SENT)
                    self.logger.info(
                        f"email sent to {email.to} ({self.metric['sent']} / {self.metric['total_emails']}) "
                    )
                else:
                    self.metric["failed"] += 1

            except Exception as e:
                print(f"error {e}")
