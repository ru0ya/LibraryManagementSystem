from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from django.db.models import Q
# from django.contrib.auth.models import User

from soma.models import Book, Member, BookTransaction
from soma.views import (
        HomePageView,
        SearchResultsView,
        BookListView,
        BookDetailView,
        BookCreateView,
        BookUpdateView,
        BookDeleteView,
        MemberListView,
        MemberDetailView,
        TransactionListView,
        IssueBookView,
        ReturnBookView,
        )


class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()

    def test_home_page_status_code(self):
        response = self.client.get(reverse('soma:home'))
        self.assertEqual(response.status_code, 200)


class SearchResultsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Book.objects.create(
                title='Test Book',
                author='Test author',
                isbn='1234567890',
                year=2020,
                genre='Test Genre',
                summary='Does this work?',
                status=Book.BookStatus.AVAILABLE,
                cost=60
                )

    def test_search_results_view(self):
        response = self.client.get(
                reverse('soma:search_results'),
                {
                    'q': 'Test'
                    }
                )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')


class BookListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='1234567890',
                year=2020,
                genre='Test Genre',
                summary='Does this work?',
                status=Book.BookStatus.AVAILABLE,
                cost=60
                )

    def test__view(self):
        response = self.client.get(reverse('soma:all_books'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')


class BookDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='1234567890',
                year=2020,
                genre='Test Genre',
                summary='Does this work?',
                status=Book.BookStatus.AVAILABLE,
                cost=60
                )

    def test_book_detail_view(self):
        response = self.client.get(
                reverse(
                    'soma:book_detail',
                    args=[self.book.book_id]
                    )
                )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Book')


class BookCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_book_create_view(self):
        response = self.client.post(
                reverse('soma:book_upload'),
                {
                    'title': 'Test Book',
                    'author': 'Test Author',
                    'isbn': '1234567890',
                    'year': 2020,
                    'genre': 'Test Genre',
                    'summary': 'Does this work?',
                    'status': Book.BookStatus.AVAILABLE,
                    'cost': 60
                    }
                )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Book.objects.last().title, 'Test Book')


class MemberListViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        Member.objects.create(
                name='Test Member',
                email='test@member.com',
                phone='+2547689065'
                )

    def test_member_list_view(self):
        response = self.client.get(reverse('soma:all_members'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Member')


class MemberDetailViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(
                name='Test Member',
                email='test@member.com',
                phone='+2547689065'
                )

    def test_member_detail_view(self):
        response = self.client.get(
                reverse(
                    'soma:member_detail',
                    args=[self.member.member_id]
                    )
                )
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Member')


class MemberCreateViewTest(TestCase):
    def setUp(self):
        self.client = Client()

    def test_member_create_view(self):
        response = self.client.post(
                reverse('soma:member_add'),
                {
                    'name': 'Test User',
                    'email': 'test@member.com',
                    'phone': '+2547689065'
                    }
                )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Member.objects.last().name, 'Test User')


class IssueBookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(name='Test Member')
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='1234567890',
                year=2020,
                genre='Test Genre',
                summary='Does this work?',
                status=Book.BookStatus.AVAILABLE,
                cost=60
                )

    def test_issue_book_view_post(self):
        response = self.client.post(
                reverse('soma:issue_book'),
                {
                    'member': self.member.member_id,
                    'book': self.book.book_id,
                    }
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                Book.objects.get(book_id=self.book.book_id).status,
                Book.BookStatus.UNAVAILABLE
                )


class ReturnBookViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.member = Member.objects.create(name='Test Member')
        self.book = Book.objects.create(
                title='Test Book',
                author='Test Author',
                isbn='1234567890',
                year=2020,
                genre='Test Genre',
                summary='Does this work?',
                cost=60,
                status=Book.BookStatus.UNAVAILABLE,
                borrower=self.member
                )
        self.transaction = BookTransaction.objects.create(
                member=self.member,
                book=self.book,
                date_borrowed=timezone.now()
                )

    def test_return_book_view_get(self):
        response = self.client.get(reverse('soma:return_book'))
        self.assertEqual(response.status_code, 200)

    def test_return_book_view_post(self):
        response = self.client.post(
                reverse('soma:return_book'),
                {
                    'member': self.member.member_id,
                    'book': self.book.book_id,
                    }
                )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
                Book.objects.get(book_id=self.book.book_id).status,
                Book.BookStatus.AVAILABLE
                )
