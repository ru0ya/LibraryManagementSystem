from django.views import View
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect, render
from django.db.models import Q
from django.contrib import messages
from django.views.generic import TemplateView
from django.http import HttpResponseRedirect, HttpResponseBadRequest


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

            if book.status == Book.BookStatus.AVAILABLE:
                book.status = Book.BookStatus.UNAVAILABLE
                book.borrower = member
                book.save()

                BookTransaction.objects.create(
                        member=member,
                        book=book,
                        # status=book.status,
                        date_borrowed=timezone.now()
                        )
                messages.success(self.request, 'Book issued successfully.')
                return HttpResponseRedirect(self.success_url)
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
    
    """
    # view for returning a book
    def return_book(request, book_title):
        #return a book
        if request.method == 'POST':
            form = ReturnBookForm(request.POST)
            if form.is_valid():
                member = form.cleaned_data['member']
                book = form.cleaned_data['book']

                transaction = BookTransaction.objects.get(
                        book_title,
                        returned=False
                        ).first()
                # book = get_object_or_404(Book, pk=book_id)
                member = book.borrower
            
                transaction = get_object_or_404(
                        BookTransaction,
                        member=member,
                        book=book
                        )

                if transaction.book == book:
                    transaction.date_returned = timezone.now()            

                    transaction.returned = True
                    # calculate borrowed days and update transaction cost
                    transaction.borrowed_days = self.calc_borrowed_days(transaction)
                    transaction.total_cost = self.calc_total_cost(transaction)
                    transaction.save()

                    member.cost_incurred += transaction.total_cost
                    member.save()

                    # update book status
                    book.status = Book.BookStatus.AVAILABLE
                    book.borrower = None
                    book.save()

                    return redirect('transaction_detail', transaction.id)
                else:
                    return HttpResponseBadRequest('Invalid Transaction.')
        else:
            form = ReturnBookForm()
            return render(request, self.template_name, {'form': form})
    """
    def get(self, request, *args, **kwargs):
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = self.form_class(request.POST)
        
        if form.is_valid():
            cleaned_data = form.cleaned_data
            member = cleaned_data.get('member')
            book = cleaned_data.get('book')
 
        transaction = BookTransaction.objects.get(
                book=book.title,
                returned=False
                ).first()
        # book = get_object_or_404(Book, pk=book_id)
        member = book.borrower
    
        transaction = get_object_or_404(
                BookTransaction,
                member=member,
                book=book
                )
        if transaction.book == book:
            transaction.date_returned = timezone.now()            

            transaction.returned = True
            # calculate borrowed days and update transaction cost
            transaction.borrowed_days = self.calc_borrowed_days(transaction)
            transaction.total_cost = self.calc_total_cost(transaction)
            transaction.save()

            member.cost_incurred += transaction.total_cost
            member.save()

            # update book status
            book.status = Book.BookStatus.AVAILABLE
            book.borrower = None
            book.save()

            return redirect('transaction_detail', transaction.id)
        else:
            return HttpResponseBadRequest('Invalid Transaction.')

    def calc_borrowed_days(self, transaction):
        """calculates the number of days a book was borrowed"""
        if transaction.date_returned:
            return (transaction.date_returned - transaction.date_borrowed).days
        else:
            return (timezone.now() - transaction.date_borrowed).days
    
    def calc_total_cost(self, transaction):
        """calculates total amount owed by a member"""
        cost_per_day = transaction.book.cost
        return cost_per_day * transaction.borrowed_days
    """
    def update_member_cost(self, transaction):
        update member amount owed
        if transaction.date_returned:
            member = member.member
            member.cost_incurred -= transaction.total_cost
            member.save()
        else: 'return_book/<str:book_title>/',
            pass
    """ 
