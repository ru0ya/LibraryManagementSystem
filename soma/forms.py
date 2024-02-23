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
                'borrower'
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
                'borrowed_days'
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
    class Meta:
        model = BookTransaction
        fields = []

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'] = forms.ModelChoiceField(
                queryset=Member.objects.all(),
                )
        self.fields['book'] = forms.ModelChoiceField(
                queryset=Book.objects.filter(borrower__isnull=False),
                )

    def clean_member(self):
        member = self.cleaned_data.get('member')
        if member:
            self.fields['book'].queryset = Book.objects.filter(borrower=member)
        
        return member
