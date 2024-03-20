# Library Management Web Application
-------------------------------------------
## Overview

This is a simple web application designed to manage the operations of a local library. The application allows librarians to track books, members, and transactions efficiently. It includes functionalities such as CRUD operations for books and members, issuing books to members, searching for books, and managing book fees.  

Live Link  
https://maktaba.onrender.com/  


## Functionality Checklist

- [x] Perform general CRUD operations on Books and Members
- [x] Issue a book to a member
- [x] Issue a book return from a member
- [x] Search for a book by name and author
- [x] Charge a rent fee on book returns
- [ ] Ensure a member’s outstanding debt is not more than KES.500

## Features  

## Models  
> Member  
- This is the Member model, creates library member using their name, email and
  phone with the member_id being generated automatically using uuid
```
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
           return reverse(
           'soma:member_detail',
           args=[str(self.member_id)]
           )
```  

> Book  
- The book model with multiple fields, the status field is set as available by
  default to signify the book is available for borrowing  
- The borrower is a foreign key of the Member model to show which member
  borrowed which book establishing a relationship between book and member  

```
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
    cost = models.DecimalField(max_digits=5, decimal_places=2)
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
```  

> BookTransaction  
- This model helps keep track of books issued and books returned  
- It based on the days a book was returned calculates how much the member owes
  the library
- It uses the Book and Member as foreign keys  

```  
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
    date_borrowed = models.DateTimeField(auto_now_add=True)
    date_returned = models.DateTimeField(auto_now_add=True, null=True)
    returned = models.BooleanField(default=False)
    total_cost = models.DecimalField(
            max_digits=5,
            decimal_places=2,
            blank=True,
            null=True
            )
    borrowed_days = models.IntegerField(blank=True, null=True)

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
        cost_per_day = self.book.cost
        return cost_per_day * borrowed_days

    def __str__(self):
        return f'{self.member.name} borrowed {self.book.title}'

    class Meta:
        ordering = ['date_borrowed']

    def get_absolute_url(self):
        return reverse('soma:transaction_detail', args=[str(self.id)])
```  


### Books Management

- **Add Book**: Allows librarians to add new books to the library inventory. Librarians can input book details such as title, author, genre, and quantity.  
<--Updating-->
---------------------------------------  

![add new book](screenshots/)  

-------------------------------------

- **Update Book**: Enables librarians to update the details of existing books, including title, author, genre, and quantity.  
---------------------------------------------------------------  

![update book details](screenshots/)  

------------------------------------------------------------  

- **Delete Book**: Allows librarians to remove books from the library inventory.  

- **Search Book**: Provides a search functionality for librarians to find books by title or author.  

------------------------------------  

 ![serch book](screenshots/)  

--------------------------------------  



### Members Management

- **Add Member**: Allows librarians to add new members to the library system. Librarians can input member details such as name, contact information, and membership ID.  
-----------------------------------------------------------  
![add member](screenshots/)  

----------------------------------------  

- **Update Member**: Enables librarians to update the details of existing members, including name, contact information, and membership ID.  
-----------------------  
![update member](screenshots/)  
------------------------------  

- **Delete Member**: Allows librarians to remove members from the library system.

### Transaction Management

- **Issue Book**: Allows librarians to issue a book to a member. This involves reducing the stock of the book in the inventory and recording the transaction details.  
---------------------------  
![issue book](screenshots/)  

-----------------------------  

- **Return Book**: Debugging  
----------------------------------  
![return book](screenshots/)  

------------------------------------
- **Manage Fees**: Work in Progress

## Technologies Used

- **Framework**: Django
- **Database**: SQLite  
- **Frontend**: HTML, CSS
- **Additional Libraries/Frameworks**: Bootstrap5

## Setup Instructions

1. Clone the repository from [GitHub](https://github.com/ru0ya/Maktaba).  

`git clone https://github.com/ru0ya/Maktaba`  

2. Install dependencies using `pip3 install -r requirements.txt`.
3. Run `python3 manage.py migrate` to apply migrations
4. Start development server using `python3 manage.py runserver`
5. Access the application through the provided URL.
