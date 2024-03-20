from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.auth.models import User

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
        self.factory = RequestFactory()
        self.user = User.objects.create_user(
                username='testuser',
                password='1234567'
                )
        
