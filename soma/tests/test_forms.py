from django.test import TestCase

from soma.forms import(
        BookForm,
        MemberForm,
        BookTransactionForm,
        IssueBookForm,
        ReturnBookForm
        )
from soma.models import Book, Member, BookTransaction


class BooKformTest(TestCase):
    def test_book_form_valid(self):
        form = BookForm(data={
            'title': 'Test Book',
            'author': 'Test Author',
            'isbn': '123456789',
            'year': 2018,
            'genre': 'Test Genre',
            'summary': 'Test Summary',
            'cost': 60,
            })
        self.assertTrue(form.is_valid())


class MemberFormTest(TestCase):
    def test_member_form_valid(self):
        form = MemberForm(data={
            'name': 'Test Member',
            'email': 'test@example.com',
            'phone': '+2547890453',
            })
        self.assertTrue(form.is_valid())


class BookTransactionFormTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
                name='Test Member',
                email='test@example.com',
                phone='+25473456732'
                )
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='123456789',
                year=2018,
                genre='Test Genre',
                summary='Test Summary',
                cost=60.00
                )

    def test_book_transaction_form_valid(self):
        form = BookTransactionForm(
                data={
                    'member': self.member.member_id,
                    'book': self.book.book_id,
                    'returned': False,
                    'total_cost': 60.00
                    }
                )
        self.assertTrue(form.is_valid())


class IssueBookFormTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
                name='Test Member',
                email='test@member.com',
                phone='+255789054321'
                )
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='+25472309876',
                year=2018,
                genre='Test Genre',
                summary='Test Summary',
                cost=60.00
                )

        def test_issue_book_form_valid(self):
            form = IssueBookForm(
                    data={
                        'member': self.member.member_id,
                        'book': self.book.book_id,
                        }
                    )
            self.assertTrue(form.is_valid())


class ReturnBookFormTest(TestCase):
    def setUp(self):
        self.member = Member.objects.create(
                name='Test Member',
                email='test@member.com',
                phone='+254754321'
                )
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='+25472309876',
                year=2018,
                genre='Test Genre',
                summary='Test Summary',
                cost=60.00,
                borrower=self.member
                )

        def test_return_book_form_valid(self):
            form = ReturnBookForm(
                    data={
                        'member': self.member.member_id,
                        'book': self.book.book_id,
                        }
                    )
            self.assertTrue(form.is_valid())

        def test_return_book_form_invalid(self):
            other_member = Member.objects.create(
                name='Other Member',
                email='other@member.com',
                phone='+254754321'
                )
            form = ReturnBookForm(
                    data={
                        'member': other_member.member_id,
                        'book': self.book.book_id,
                        }
                    )
            self.assertFalse(form.is_valid())
