from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.db import transaction
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest
from django.core.exceptions import ValidationError


from .models import Book, Member, BookTransaction
from .forms import (
        BookForm,
        MemberForm,
        BookTransactionForm,
        IssueBookForm,
        ReturnBookForm
        )


class HomePageView(TemplateView):
    """Homepage"""
    template_name = 'soma/home.html'

    def get_context_data(self, **kwargs):
        """computes data for displaying"""
        context = super().get_context_data(**kwargs)
        context['books'] = Book.objects.count()
        context['total_members'] = Member.objects.count()
        context['total_transactions'] = BookTransaction.objects.count()

        return context


class SearchResultsView(TemplateView):
    """display search results"""
    template_name = 'soma/search.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        q = self.request.GET.get('q')
        if q:
            context['results'] = Book.objects.filter(
                    Q(title__icontains=q) | Q(author__icontains=q)
                    )

        return context


class BookListView(ListView):
    """
    list all books
    """
    model = Book
    template_name = 'soma/book_list.html'


class BookDetailView(DetailView):
    """
    list details of a book
    """
    model = Book
    template_name = 'soma/book_detail.html'
    

class BookCreateView(CreateView):
    """upload a book"""
    model = Book
    template_name = 'soma/book_form.html'
    form_class = BookForm
    success_url = reverse_lazy('soma:home')


class BookUpdateView(UpdateView):
    """update details of a book"""
    model = Book
    template_name = 'soma/book_form.html'
    form_class = BookForm
    success_url = reverse_lazy('soma:home')


class BookDeleteView(DeleteView):
    "deletes a book"
    model = Book
    template_name = 'soma/confirm_delete.html'
    success_url = reverse_lazy('soma:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'book'
        return context


class MemberListView(ListView):
    """list all members"""
    model = Member
    template_name = 'soma/member_list.html'
    context_object_name = 'members_list'


class MemberDetailView(DetailView):
    """list details of a member"""
    model = Member
    template_name = 'soma/member_detail.html'


class MemberCreateView(CreateView):
    """add a new member"""
    model = Member
    form_class = MemberForm
    template_name = 'soma/member_form.html'
    success_url = reverse_lazy('soma:home')


class MemberUpdateView(UpdateView):
    """update details of a member"""
    model = Member
    form_class = MemberForm
    template_name = 'soma/member_form.html'
    success_url = reverse_lazy('soma:home')


class MemberDeleteView(DeleteView):
    """deletes a member"""
    model = Member
    template_name = 'soma/confirm_delete.html'
    success_url = reverse_lazy('soma:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['object_type'] = 'member'
        return context


class TransactionListView(ListView):
    """list all transactions"""
    model = BookTransaction
    form_class = BookTransactionForm
    template_name = 'soma/transaction_list.html'


class IssueBookView(View):
    model = BookTransaction
    form_class = IssueBookForm
    template_name = 'soma/issue_book.html'
    success_url = reverse_lazy('soma:home')

    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        """saves form data to db"""
        form = self.form_class(request.POST)
        if form.is_valid():
            member = form.cleaned_data['member']
            book = form.cleaned_data['book']
        
            # check if member has any pending book returns
            pending_returns = BookTransaction.objects.filter(
                member=member,
                date_returned=None
            ).exists()

            print(pending_returns)

            if pending_returns:
                messages.error(request, 'Member has pending book returns.')
                return render(request, self.template_name, {'form': form})

            if book.status == Book.BookStatus.AVAILABLE:
                book.status = Book.BookStatus.UNAVAILABLE
                book.borrower = member
                book.save()

                date_borrowed = timezone.now()

                BookTransaction.objects.create(
                            member=member,
                            book=book,
                            # status=book.status,
                            date_borrowed=date_borrowed,
                            )

                messages.success(self.request, 'Book issued successfully.')
                return render(self.request, self.template_name, {'form': form})
            else:
                messages.error(self.request, 'Book is already borrowed.')
                return render(self.request, self.template_name, {'form': form})
        
        else:
            messages.error(
                    self.request,
                    'There was an error processing your request'
                    )
        return render(self.request, self.template_name, {'form': form})


class ReturnBookView(View):
    """return a book"""
    model = BookTransaction
    form_class = ReturnBookForm
    template_name = 'soma/return_book.html'
    success_url = reverse_lazy('soma:home')
    
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    @transaction.atomic
    def post(self, request):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            member = form.cleaned_data['member']
            book = form.cleaned_data['book']
            transaction = get_object_or_404(
                    BookTransaction,
                    member=member,
                    book=book
                    )
            transaction.date_returned = timezone.now()
            transaction.returned = True
            transaction.borrowed_days = transaction.calc_borrowed_days()

            if transaction.borrowed_days is None:
                messages.error(request, "No data found for date borrowed")
                return render(request, self.template_name, {'form': form})

            try:
                transaction.total_cost = transaction.calc_total_cost(
                    transaction.borrowed_days
                    )
            except ValidationError as e:
                messages.error(self.request, str(e))
                return render(self.request, self.template_name, {'form': form})

            book.status = Book.BookStatus.AVAILABLE
            book.borrower = None
            book.save()

            member.cost_incurred = transaction.total_cost
            member.save()

            transaction.delete()

            sentence = f"{member.name} owes a total of\
                    Kes.{member.cost_incurred}"

            return render(
                    request,
                    self.template_name,
                    {'form': form, 'sentence': sentence}
                    )
        else:
            messages.error(
                    self.request,
                    'There was an error processing your request'
                    )
            return render(request, self.template_name, {'form': form, 'errors': form.errors})

        return render(request, self.template_name, {'form': form})
