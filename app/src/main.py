from __future__ import annotations
import time as time_module
from typing import List


# TODO : instead of using asyncio i could uvloop it faster and handle connections better
from app.scheduler.scheduler import EmailScheduler
from app.Mailer.sender import EMAIL, EmailSender, EmailStatus


def main():
    print("test mail worker init\n")

    email_scheduler = EmailScheduler()
    email_sender = EmailSender()

    # startup_delay = email_scheduler.add_random_delay_after_init()
    # print(f"fire up delay : {startup_delay}\n")
    # time_module.sleep(startup_delay.total_seconds())
    #
    while True:
        now = email_scheduler.get_current_time()
        print(f"the current time is : {now.strftime('%H:%M:%S')}")

        if not email_scheduler.checking_buisness_hours(now):
            return
        # load the emails :
        raw_emails = email_sender.load_emails_from_database()
        print(type(raw_emails), raw_emails[:3])

        if not raw_emails:
            return False
        # emails = [EMAIL.from_dict(email) for email in raw_emails]
        emails: list[EMAIL] = []
        for row in raw_emails:
            emails.append(
                EMAIL(
                    to=row,
                    subject="my subject",
                    body="my body",
                )
            )
        queue_line = email_sender.saving_emails_in_queue(raw_emails)
        while not queue_line.empty():
            email = queue_line.get()
            allowed, msg = email_scheduler.check_hourly_email_rate_limit()
            if not allowed:
                print(msg)
                break

            allowed_daily, message = email_scheduler.check_daily_email_rate_limit()
            if not allowed_daily:
                print(message)
                break
            if not email_sender.validate_email_structure(email):
                email.status = EmailStatus.FAILED
                continue
            try:
                print("sending to someone")
                success = email_sender.send_single_email(email)
                if success:
                    email_scheduler.email_sent_during_an_hour += 1
                    email_scheduler.email_sent_during_a_day += 1
                    print(
                        f"✓ Sent successfully ({email_scheduler.email_sent_during_an_hour}/hour)"
                    )
                else:
                    print("✗ Send failed (validation)")
            except Exception as e:
                print("error", e)
                raise


if __name__ == "__main__":
    main()
