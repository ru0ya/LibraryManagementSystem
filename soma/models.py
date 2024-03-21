from django.db import models
from django.urls import reverse
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
import uuid


class Member(models.Model):
    member_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=80) 
    
    def __str__(self):
        return f'{self.name}'
    
    class Meta:
        ordering = ['name']
      
    def get_absolute_url(self):
        return reverse('soma:member_detail', args=[str(self.member_id)])       


class Book(models.Model):
    class BookStatus(models.TextChoices):
        AVAILABLE = "AV", _("Available")
        UNAVAILABLE = "UN", _("Unavailable")

    book_id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=200)
    isbn = models.CharField(max_length=200)
    year = models.IntegerField()
    genre = models.CharField(max_length=80)
    summary = models.TextField()
    date_added = models.DateTimeField(auto_now_add=True)
    date_updated = models.DateTimeField(auto_now=True)
    status = models.CharField(
            max_length=2, 
            choices=BookStatus.choices,
            default=BookStatus.AVAILABLE,
            )
    cost = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    borrower = models.ForeignKey(
            Member,
            on_delete=models.SET_NULL,
            null=True,
            blank=True
            )

    def __str__(self):
        return f'{self.title}'

    class Meta:
        ordering = ['title']

    def get_absolute_url(self):
        return reverse('soma:book_detail', args=[str(self.book_id)])  


class BookTransaction(models.Model):
    member = models.ForeignKey(
            Member,
            on_delete=models.CASCADE,
            related_name='member_transaction'
            )
    book = models.ForeignKey(
            Book,
            on_delete=models.CASCADE,
            related_name='book_transaction'
            )
    date_borrowed = models.DateTimeField(auto_now_add=True, null=True)
    date_returned = models.DateTimeField(auto_now_add=False, null=True)
    returned = models.BooleanField(default=False)
    total_cost = models.DecimalField(
            max_digits=5,
            decimal_places=2,
            default=0.00
            )
    borrowed_days = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        self.borrowed_days = self.calc_borrowed_days()
        self.total_cost = self.calc_total_cost(self.borrowed_days)

        self.member.cost_incurred = self.total_cost

        super(BookTransaction, self).save(*args, **kwargs)

    def calc_borrowed_days(self):
        if self.date_borrowed is not None:
            if self.date_returned:
                return (self.date_returned - self.date_borrowed).days
            else:
                return (timezone.now() - self.date_borrowed).days
        else:
            return None

    def calc_total_cost(self, borrowed_days):
        cost_per_day = self.book.cost if self.book.cost else 0
        if borrowed_days is None:
            borrowed_days = 0
        total_cost = cost_per_day * borrowed_days
        # if total_cost > 500:
            # raise ValidationError("Cost exceeds the maximum limit of Kes.500.00")
        return total_cost
       
    def __str__(self):
        return f'{self.member.name} borrowed {self.book.title}'

    class Meta:
        ordering = ['date_borrowed']   
      
    def get_absolute_url(self):
        return reverse('soma:transaction_detail', args=[str(self.id)])
