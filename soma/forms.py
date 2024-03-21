from django import forms
from django.db.models import Q
# from dal_select2.widgets import ModelSelect2Widget

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
                ]


class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = [
                'name',
                'email',
                'phone',
                ]
 

class BookTransactionForm(forms.ModelForm):
    class Meta:
        model = BookTransaction
        fields = [
                'member',
                'book',
                'returned',
                'total_cost',
                # 'borrowed_days'
                ]


class IssueBookForm(forms.ModelForm):
    member = forms.ModelChoiceField(
            queryset=Member.objects.all(),
            widget=forms.Select,
            label='Members'
            )
    book = forms.ModelChoiceField(
            queryset=Book.objects.filter(borrower__isnull=True),
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
    member = forms.ModelChoiceField(
            queryset=Member.objects.all(),
            widget=forms.Select,
            )
    book = forms.ModelChoiceField(
            queryset=Book.objects.filter(borrower__isnull=False),
            widget=forms.Select,
            )

    class Meta:
        model = BookTransaction
        fields = ['member', 'book']

        widgets = {
                'member': forms.Select(),
                'book': forms.Select(),
                }

    def clean(self):
        cleaned_data = super().clean()
        member = self.cleaned_data.get('member')
        book = self.cleaned_data.get('book')

        if member != book.borrower:
            raise forms.ValidationError("Selected member does not match\
                    person who borrowed the book.")

        return cleaned_data
