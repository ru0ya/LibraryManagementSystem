from django.urls import path, include
from . import views


app_name = 'soma'

urlpatterns = [
        path('', views.HomePageView.as_view(), name='home'),
        path(
            'search_results/',
            views.SearchResultsView.as_view(),
            name='search_results'
            ),
        path(
            'all_books/',
            views.BookListView.as_view(),
            name='all_books'
            ),
        path(
            'book/<uuid:pk>/detail',
            views.BookDetailView.as_view(),
            name='book_detail'
            ),
        path(
            'book/upload/',
            views.BookCreateView.as_view(),
            name='book_upload'
            ),
        path(
            'book/<uuid:pk>/update',
            views.BookUpdateView.as_view(),
            name='book_update'
            ),
        path(
            'book/<uuid:pk>/delete/',
            views.BookDeleteView.as_view(),
            name='book_delete'
            ),
        path(
            'all_members/',
            views.MemberListView.as_view(),
            name='all_members'
            ),
        path(
            'member/<uuid:pk>/detail',
            views.MemberDetailView.as_view(),
            name='member_detail'
            ),
        path(
            'member/add/',
            views.MemberCreateView.as_view(),
            name='member_add'
            ),
        path(
            'member/<uuid:pk>/update',
            views.MemberUpdateView.as_view(),
            name='member_update'
            ),
        path(
            'member/<uuid:pk>/delete/',
            views.MemberDeleteView.as_view(),
            name='member_delete'
            ),
        path(
            'transactions/',
            views.TransactionListView.as_view(),
            name='all'
            ),
        path(
            'issue_book/',
            views.IssueBookView.as_view(),
            name='issue_book'
            ),
        path(
            'return_book',
            views.ReturnBookView.as_view(),
            name='return_book',
            ),
        ]
