from apscheduler.schedulers.blocking import BlockingScheduler
from bible_reader import TelegramBibleReading
from weekly_birthday_marriage import NamesDbUpdate
from sunday_link import SundLinkSender

sched = BlockingScheduler()


@sched.scheduled_job('cron', hour=10, minute=5, timezone='Europe/Kiev')
def update_reading():
    worker = TelegramBibleReading()
    worker.bot_send_message()


sched.start()

