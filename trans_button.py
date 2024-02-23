from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from ../../models import BookTransaction


class Command(BaseCommand):
    help = 'Update total cost for all open transactions, if greater\
            than kes.500 sends member an email'

    def handle(self, *args, **options):
        """update member amount owed daily"""
        now = timezone.now()
        MAX_COST = 500

        # iterate over open transactions
        for transaction in BookTransaction\
                .objects.filter(date_returned_isnull=True):
                # calculate number of days since book was borrowed
                days_borrowed = (now - transaction.date_borrowed).days

                # calculate cost for the past day
                daily_cost = transaction.book.cost

                # update total cost
                transaction.total_cost += daily_cost * days_borrowed
                transaction.save()

                if transaction.total_cost > MAX_COST:
                    transaction.total_cost = MAX_COST
                    send_email(
                            'Your total cost has reached kes.500',
                            f'You currently owe ${MAX_COST} for borrowed
                            books.Kindly settle your debts soon.',
                            settings.DEFAULT_FROM_EMAIL,
                            [transaction.member.email],
                            fail_silently=False,
                            )
