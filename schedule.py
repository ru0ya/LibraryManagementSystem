from celery import shared_task
from datetime import timedelta
from .management.commands.daily_update import Command


@shared_task
def update_cost():
    command = Command()
    command.handle()


# schedule task to run once a day
update_cost.apply_async(countdown=timedelta(days=1))
