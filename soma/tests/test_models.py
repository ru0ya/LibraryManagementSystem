from django.test import TestCase
from django.urls import reverse
import datetime

from soma.models import Member, Book, BookTransaction


class MemberModelTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
                name="John Doe",
                email="john@doe.com",
                phone="+254014567890"
                )

    def test_member_creation(self):
        self.assertTrue(isinstance(self.member, Member))
        self.assertEqual(self.member.__str__(), self.member.name)
        self.assertEqual(
                self.member.get_absolute_url(),
                reverse(
                    'soma:member_detail',
                    args=[str(self.member.member_id)]
                    )
                )


class BookModelTest(TestCase):
    def setUp(self):
        self.book = Book.objects.create(
                title="Test Book",
                author="Test Author",
                isbn="1234567890",
                year=2021,
                genre="Test Genre",
                summary="Test Summary",
                cost=60
                )

    def test_book_creation(self):
        self.assertTrue(isinstance(self.book, Book))
        self.assertEqual(self.book.__str__(), self.book.title)
        self.assertEqual(
                self.book.get_absolute_url(),
                reverse(
                    'soma:book_detail',
                    args=[str(self.book.book_id)]
                    )
                )


class BookTransactionTest(TestCase):
    def setUp(self):
        self.member = member = Member.objects.create(
                name="John Doe",
                email="john@doe.com",
                phone="+254014567890"
                )
        self.book = book = Book.objects.create(
                title="Test Book",
                author="Test Author",
                isbn="123456790",
                year=2021,
                genre="Test Genre",
                summary="Test Summary",
                cost=60
                )
        self.transaction = BookTransaction.objects.create(
                member=member,
                book=book,
                date_borrowed=datetime.datetime.now(),
                date_returned=datetime.datetime.now() + datetime.timedelta(days=7),
                returned=True
                )

        def test_transaction_creation(self):
            self.assertTrue(isinstance(self.transaction, BookTransaction))
            self.assertEqual(
                    self.transaction.__str__(),
                    f'{self.member.name} borrowed {self.book.title}'
                    )
            self.assertEqual(self.transaction.borrowed_days, 7)
            self.assertEqual(self.transaction.total_cost, 420)
            self.assertEqual(
                    self.transaction.get_absolute_url(),
                    reverse(
                        'soma:transaction_detail',
                        args=[str(self.transaction.id)]
                        )
                    )
