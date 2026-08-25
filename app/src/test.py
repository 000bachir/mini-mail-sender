from __future__ import annotations
import datetime
import logging
import sys
from typing import List


# class imports
from app.Mailer.sender import EMAIL, EmailPriority, EmailSender, EmailStatus
from app.scheduler.scheduler import EmailScheduler
from app.supabase.supabaseClient import DatabaseOperation, EmailRecord

"""
LOGGIN SETUP
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


# health check
def check_health() -> DatabaseOperation | None:
    logger.info("=" * 60)
    logger.info("step 1 : checking database health")
    logger.info("=" * 60)
    try:
        database = DatabaseOperation()
        health = database.check_health()
        if not health:
            logger.error("Database health check failed - aborting the pipeline\n")
            return None
        latest = database.get_latest_health_status()
        if latest:
            logger.info(f"latest database health status : {latest}")

        rows = database.count_rows_in_database()
        if rows is not None:
            if len(rows) > 0:
                logger.info(f"the number of rows are {rows}")
            else:
                logger.warning("NO ROWS HAVE BEEN FOUND")
                return None
        return database
    except Exception as e:
        logger.error(f"error checking the health of the database : {e}")
        raise


def run_scheduler_check() -> EmailScheduler | None:
    logger.info("=" * 60)
    logger.info("step two : scheduer readiness check")
    logger.info("=" * 60)
    try:
        scheduler = EmailScheduler()
        # checking buisness hours :
        is_buisness_hours = scheduler.checking_buisness_hours()
        if is_buisness_hours:
            logger.info(f"Inside of buisness hours : {is_buisness_hours}")
        else:
            logger.warning(
                "Outside business hours — emails will be queued but not sent in production. "
                "Continuing in test mode anyway.\n"
            )
        hourly_ok, hourly_msg = scheduler.check_hourly_email_rate_limit()
        daily_ok, daily_msg = scheduler.check_daily_email_rate_limit()

        logger.info(f"hourly rate limit Ok {hourly_ok} | {hourly_msg.strip()}")
        logger.info(f"hourly rate limit Ok {daily_ok} | {daily_msg.strip()}")
        # the waiting delay :
        # delay = scheduler.add_random_delay_after_init()
        # logger.info(f"the program have to wait {delay} before firing up")
        return scheduler
    except Exception as e:
        logger.error(f"Scheduler initalisation failed see cause : {e}")
        return None


# load recipents from database
def load_recipients(database: DatabaseOperation) -> List[str]:
    logger.info("=" * 60)
    logger.info("step three : loading emails")
    logger.info("=" * 60)
    try:
        recipients = database.fetch_all_emails()
        if len(recipients) == 0:
            logger.error("No recipents found in the database")
            return []
        logger.info(f"Loaded {len(recipients)} recipient(s): {recipients}\n")
        return recipients
    except Exception as e:
        logger.error(f"ERROR : failed to load the recipients : {e}")
        return []


# building the email object :
def building_email_object(recipients: list[str]) -> list[EMAIL]:
    logger.info("=" * 60)
    logger.info("step three : loading emails")
    logger.info("=" * 60)

    emails: list[EMAIL] = []
    for recipent in recipients:
        email_object = EMAIL(
            to=recipent,
            subject="test email forwarder",
            body=(
                "Hello,\n\n"
                "This is an automated integration test from the mail forwarder pipeline.\n"
                "If you received this, all three components (DB / Scheduler / Mailer) "
                "are communicating correctly.\n\n"
                "Best regards."
            ),
            priority=EmailPriority.NORMAL,
            status=EmailStatus.PENDING,
            created_at=datetime.datetime.now().isoformat(),
        )
        emails.append(email_object)
        logger.info(f"Built email object for {recipent}")
    logger.info(f"\n total emails built : {len(emails)} \n")
    return emails


# queue and validate :
def queue_and_validate(sender: EmailSender, emails: list[EMAIL]):
    logger.info("=" * 60)
    logger.info("step three : queue and validate")
    logger.info("=" * 60)
    queue = sender.saving_emails_in_queue(emails)
    logger.info(f"queue size {queue.qsize()}")

    valid_emails: list[EMAIL] = []
    invalid_emails: list[EMAIL] = []

    temporary_list = list(queue.queue)
    for email_obj in temporary_list:
        is_valid = sender.validate_email_structure(email_obj)
        if is_valid:
            valid_emails.append(email_obj)
        else:
            invalid_emails.append(email_obj)

    logger.info(f"Valid : {len(valid_emails)}")
    logger.info(f"Invalid emails : {len(invalid_emails)}")
    return valid_emails, invalid_emails


# sending the mail :
def send_mails(
    sender: EmailSender,
    scheduler: EmailScheduler,
    valid_emails: list[EMAIL],
    database: DatabaseOperation,
    dry_run,
):
    logger.info("=" * 60)
    logger.info("step three : queue and validate")
    logger.info("=" * 60)

    sent_count: int = 0
    failed_count: int = 0
    for email_obj in valid_emails:
        # first guard : the hours :
        hourly_ok, hourly_msg = scheduler.check_hourly_email_rate_limit()
        if not hourly_ok:
            logger.warning(f"Hourly limit hit - stopping the program {hourly_msg}")
            break
        # second guard the daily quota
        daily_ok, daily_msg = scheduler.check_daily_email_rate_limit()
        if not daily_ok:
            logger.warning(f"Daily limit hit - exiting the program : {daily_msg}")
            break
        if dry_run:
            logger.info(f"dry run : would send to {email_obj.to}")
            email_obj.status = EmailStatus.SUCCESS
            email_obj.sent_at = datetime.datetime.now().strftime("%H:%M:%S")
            sent_count += 1

            database.update_email_status(email_obj.to, EmailStatus.SUCCESS.value)
            scheduler.email_sent_during_a_day += 1
            scheduler.email_sent_during_an_hour += 1
        else:
            success = sender.send_single_email(email_obj)
            if success:
                sent_count += 1
                scheduler.email_sent_during_an_hour += 1
                scheduler.email_sent_during_a_day += 1
                database.update_email_status(email_obj.to, EmailStatus.SUCCESS.value)
            else:
                failed_count += 1
                database.update_email_status(email_obj.to, EmailStatus.FAILED.value)
            if len(valid_emails) > 1:
                scheduler.random_email_interval_between_delivery()
    logger.info(f"\n sent : {sent_count} | failed : {failed_count} \n")
    return sent_count, failed_count


def print_summary(
    total_recipients: int,
    total_valid: int,
    total_invalid: int,
    sent: int,
    failed: int,
):
    logger.info("=" * 60)
    logger.info("PIPELINE SUMMARY")
    logger.info("=" * 60)
    logger.info(f"  Recipients loaded : {total_recipients}")
    logger.info(f"  Valid emails      : {total_valid}")
    logger.info(f"  Invalid emails    : {total_invalid}")
    logger.info(f"  Sent              : {sent}")
    logger.info(f"  Failed            : {failed}")
    logger.info("=" * 60 + "\n")


# main entry point
def main(dry_run: bool = True):
    logger.info("MAIL forwarder - stress testing")
    # database :
    db = check_health()
    if db is None:
        logger.critical("Cannot proceede without health check of the database")
        sys.exit(1)

    scheduler = run_scheduler_check()
    if scheduler is None:
        logger.critical("No working scheduler - terminating")
        sys.exit(1)

    recipients = load_recipients(db)
    if not recipients:
        logger.warning("No recipients to process - exiting")
        sys.exit(1)

    Emails = building_email_object(recipients)

    try:
        sender = EmailSender()
    except Exception as e:
        logger.critical(f"sender could not be initialized : {e}\n")
        sys.exit(1)
    valid_emails, invalid_emails = queue_and_validate(sender, Emails)
    if not valid_emails:
        logger.warning("No valid email have been found")
        sys.exit(0)

    sent, failed = send_mails(
        sender=sender,
        scheduler=scheduler,
        valid_emails=valid_emails,
        database=db,
        dry_run=dry_run,
    )
    # Summary
    print_summary(
        total_recipients=len(recipients),
        total_valid=len(valid_emails),
        total_invalid=len(invalid_emails),
        sent=sent,
        failed=failed,
    )


if __name__ == "__main__":
    main(dry_run=False)
