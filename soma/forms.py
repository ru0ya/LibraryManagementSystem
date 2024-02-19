from django import forms
from django.db.models import Q
from .models import Book, Member, BookTransaction


# STATUS_FIELD = ['available', 'unavailable']


class BookForm(forms.ModelForm):
    class Meta:
        model = Book
        fields = [
                'title',
                'author',
                'isbn',
                'year',
                'genre',
                'summary',
                'cost',
                'borrower'
                ]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
                'name',
                'email',
                'phone',
                'cost_incurred'
                ]
 

class BookTransactionForm(forms.ModelForm):
    class Meta:
        model = BookTransaction
        fields = [
                'member',
                'book',
                'returned',
                'total_cost',
                'borrowed_days'
                ]


class IssueBookForm(forms.ModelForm):
    member = forms.ModelChoiceField(
            queryset=Member.objects.all(),
            widget=forms.Select,
            label='Members'
            )
    book = forms.ModelChoiceField(
            queryset=Book.objects.all(),
            widget=forms.Select,
            label='Books'
            )

    class Meta:
        model = BookTransaction
        fields = ['member', 'book']

        widgets = {
            'member': forms.Select(),
            'book': forms.Select(),
            }


class ReturnBookForm(forms.ModelForm):
    # use the book title and member name to get the transaction
    member = forms.ModelChoiceField(
            queryset=Member.objects.all(),
            label='Member'
            )
    book = forms.ModelChoiceField(
            queryset=Book.objects.all(),
            label='Book'
            )
    # transaction_id = forms.IntegerField(label='Transaction ID')

    def clean(self):
        cleaned_data = super().clean()
        member = cleaned_data.get('member')
        book = cleaned_data.get('book')
        # transaction_id = cleaned_data.get('transaction_id')

        if member and book:
            try:
                transaction = BookTransaction.objects.get(
                        member=member,
                        book=book,
                        # id=transaction_id
                        )
                cleaned_data['transaction'] = transaction
            except BookTransaction.DoesNotExist:
                raise forms.ValidationError('Invalid transaction.')

        return cleaned_data

    class Meta:
        model = BookTransaction
        fields = ['book', 'member', 'total_cost', 'borrowed_days']

        widgets = {
                'book': forms.Select(),
                'member': forms.Select(),
                }
