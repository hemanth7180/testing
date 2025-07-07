import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    import sqlite3
import datetime
from typing import List, Dict, Optional
import re
import json
import os

class Book:
    def __init__(self, isbn: str, title: str, author: str, year: int, copies: int = 1):
        self.isbn = isbn
        self.title = title
        self.author = author
        self.year = year
        self.copies = copies
        self.available_copies = copies

    def __str__(self) -> str:
        return f"{self.title} by {self.author} (ISBN: {self.isbn}, Year: {self.year}, Copies: {self.available_copies}/{self.copies})"

class Member:
    def __init__(self, member_id: str, name: str, email: str):
        self.member_id = member_id
        self.name = name
        self.email = email
        self.borrowed_books: List[str] = []  # List of ISBNs
        self.fines = 0.0

    def __str__(self) -> str:
        return f"{self.name} (ID: {self.member_id}, Email: {self.email}, Fines: ${self.fines:.2f})"

class Transaction:
    def __init__(self, transaction_id: str, book_isbn: str, member_id: str, borrow_date: str):
        self.transaction_id = transaction_id
        self.book_isbn = book_isbn
        self.member_id = member_id
        self.borrow_date = borrow_date
        self.return_date: Optional[str] = None
        self.fine: float = 0.0

    def __str__(self) -> str:
        status = "Returned" if self.return_date else "Borrowed"
        return f"Transaction {self.transaction_id}: Book {self.book_isbn} by Member {self.member_id} ({status})"

class Library:
    def __init__(self, db_name: str = "library.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initialize_database()
        self.books: Dict[str, Book] = {}
        self.members: Dict[str, Member] = {}
        self.transactions: Dict[str, Transaction] = {}
        self.load_data()

    def initialize_database(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS books (
                isbn TEXT PRIMARY KEY,
                title TEXT,
                author TEXT,
                year INTEGER,
                copies INTEGER,
                available_copies INTEGER
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS members (
                member_id TEXT PRIMARY KEY,
                name TEXT,
                email TEXT,
                fines REAL
            )
        ''')
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS transactions (
                transaction_id TEXT PRIMARY KEY,
                book_isbn TEXT,
                member_id TEXT,
                borrow_date TEXT,
                return_date TEXT,
                fine REAL,
                FOREIGN KEY(book_isbn) REFERENCES books(isbn),
                FOREIGN KEY(member_id) REFERENCES members(member_id)
            )
        ''')
        self.conn.commit()

    def load_data(self):
        # Load books
        self.cursor.execute("SELECT * FROM books")
        for row in self.cursor.fetchall():
            book = Book(row[0], row[1], row[2], row[3], row[4], row[5])
            self.books[row[0]] = book

        # Load members
        self.cursor.execute("SELECT * FROM members")
        for row in self.cursor.fetchall():
            member = Member(row[0], row[1], row[2])
            member.fines = row[3]
            self.members[row[0]] = member

        # Load transactions
        self.cursor.execute("SELECT * FROM transactions")
        for row in self.cursor.fetchall():
            transaction = Transaction(row[0], row[1], row[2], row[3])
            transaction.return_date = row[4]
            transaction.fine = row[5]
            self.transactions[row[0]] = transaction
            if not transaction.return_date:
                if row[1] in self.books:
                    self.books[row[1]].available_copies -= 1
                if row[2] in self.members:
                    self.members[row[2]].borrowed_books.append(row[1])

    def save_data(self):
        # Save books
        self.cursor.execute("DELETE FROM books")
        for book in self.books.values():
            self.cursor.execute('''
                INSERT INTO books (isbn, title, author, year, copies, available_copies)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (book.isbn, book.title, book.author, book.year, book.copies, book.available_copies))

        # Save members
        self.cursor.execute("DELETE FROM members")
        for member in self.members.values():
            self.cursor.execute('''
                INSERT INTO members (member_id, name, ascended, fines)
                VALUES (?, ?, ?, ?)
            ''', (member.member_id, member.name, member.email, member.fines))

        # Save transactions
        self.cursor.execute("DELETE FROM transactions")
        for transaction in self.transactions.values():
            self.cursor.execute('''
                INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (transaction.transaction_id, transaction.book_isbn, transaction.member_id,
                  transaction.borrow_date, transaction.return_date, transaction.fine))
        self.conn.commit()

    def add_book(self, isbn: str, title: str, author: str, year: int, copies: int):
        if not self.validate_isbn(isbn):
            print("\nInvalid ISBN format!")
            return False
        if isbn in self.books:
            print("\nBook with this ISBN already exists!")
            return False
        book = Book(isbn, title, author, year, copies)
        self.books[isbn] = book
        self.cursor.execute('''
            INSERT INTO books (isbn, title, author, year, copies, available_copies)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (isbn, title, author, year, copies, copies))
        self.conn.commit()
        print(f"\nBook '{title}' added successfully!")
        return True

    def add_member(self, member_id: str, name: str, email: str):
        if not self.validate_email(email):
            print("\nInvalid email format!")
            return False
        if member_id in self.members:
            print("\nMember ID already exists!")
            return False
        member = Member(member_id, name, email)
        self.members[member_id] = member
        self.cursor.execute('''
            INSERT INTO members (member_id, name, email, fines)
            VALUES (?, ?, ?, ?)
        ''', (member_id, name, email, 0.0))
        self.conn.commit()
        print(f"\nMember '{name}' added successfully!")
        return True

    def borrow_book(self, member_id: str, isbn: str):
        if member_id not in self.members:
            print("\nMember not found!")
            return False
        if isbn not in self.books:
            print("\nBook not found!")
            return False
        if self.books[isbn].available_copies <= 0:
            print("\nNo copies available!")
            return False
        if len(self.members[member_id].borrowed_books) >= 3:
            print("\nMember has reached borrowing limit (3 books)!")
            return False

        transaction_id = f"T{len(self.transactions) + 1:05d}"
        borrow_date = datetime.datetime.now().strftime("%Y-%m-%d")
        transaction = Transaction(transaction_id, isbn, member_id, borrow_date)
        self.transactions[transaction_id] = transaction
        self.books[isbn].available_copies -= 1
        self.members[member_id].borrowed_books.append(isbn)
        self.cursor.execute('''
            INSERT INTO transactions (transaction_id, book_isbn, member_id, borrow_date, return_date, fine)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (transaction_id, isbn, member_id, borrow_date, None, 0.0))
        self.conn.commit()
        print(f"\nBook '{self.books[isbn].title}' borrowed by {self.members[member_id].name}!")
        return True

    def return_book(self, transaction_id: str):
        if transaction_id not in self.transactions:
            print("\nTransaction not found!")
            return False
        transaction = self.transactions[transaction_id]
        if transaction.return_date:
            print("\nBook already returned!")
            return False

        borrow_date = datetime.datetime.strptime(transaction.borrow_date, "%Y-%m-%d")
        return_date = datetime.datetime.now()
        days_borrowed = (return_date - borrow_date).days
        fine = max(0, (days_borrowed - 14) * 1.0)  # $1 per day after 14 days
        transaction.return_date = return_date.strftime("%Y-%m-%d")
        transaction.fine = fine
        book_isbn = transaction.book_isbn
        member_id = transaction.member_id
        self.books[book_isbn].available_copies += 1
        self.members[member_id].borrowed_books.remove(book_isbn)
        self.members[member_id].fines += fine
        self.cursor.execute('''
            UPDATE transactions SET return_date = ?, fine = ? WHERE transaction_id = ?
        ''', (transaction.return_date, fine, transaction_id))
        self.cursor.execute('''
            UPDATE books SET available_copies = ? WHERE isbn = ?
        ''', (self.books[book_isbn].available_copies, book_isbn))
        self.cursor.execute('''
            UPDATE members SET fines = ? WHERE member_id = ?
        ''', (self.members[member_id].fines, member_id))
        self.conn.commit()
        print(f"\nBook returned! Fine: ${fine:.2f}")
        return True

    def validate_isbn(self, isbn: str) -> bool:
        pattern = r"^\d{10}$|^\d{13}$"
        return bool(re.match(pattern, isbn))

    def validate_email(self, email: str) -> bool:
        pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        return bool(re.match(pattern, email))

    def list_books(self):
        print("\nBooks in Library:")
        for book in self.books.values():
            print(book)

    def list_members(self):
        print("\nMembers:")
        for member in self.members.values():
            print(member)

    def list_transactions(self):
        print("\nTransactions:")
        for transaction in self.transactions.values():
            print(transaction)

    def generate_report(self):
        print("\nLibrary Report:")
        print(f"Total Books: {len(self.books)}")
        total_copies = sum(book.copies for book in self.books.values())
        available_copies = sum(book.available_copies for book in self.books.values())
        print(f"Total Copies: {total_copies}")
        print(f"Available Copies: {available_copies}")
        print(f"Total Members: {len(self.members)}")
        total_fines = sum(member.fines for member in self.members.values())
        print(f"Total Fines Outstanding: ${total_fines:.2f}")
        active_transactions = sum(1 for t in self.transactions.values() if not t.return_date)
        print(f"Active Borrows: {active_transactions}")

    def close(self):
        self.save_data()
        self.conn.close()

def main():
    library = Library()
    
    # Sample data
    library.add_book("1234567890", "Python Programming", "John Smith", 2020, 3)
    library.add_book("0987654321", "Data Structures", "Jane Doe", 2018, 2)
    library.add_member("M001", "Alice Johnson", "alice@example.com")
    library.add_member("M002", "Bob Smith", "bob@example.com")

    while True:
        print("\nLibrary Management System")
        print("1. Add Book")
        print("2. Add Member")
        print("3. Borrow Book")
        print("4. Return Book")
        print("5. List Books")
        print("6. List Members")
        print("7. List Transactions")
        print("8. Generate Report")
        print("9. Exit")
        
        choice = input("Enter choice (1-9): ").strip()
        
        if choice == "1":
            isbn = input("Enter ISBN: ")
            title = input("Enter title: ")
            author = input("Enter author: ")
            try:
                year = int(input("Enter year: "))
                copies = int(input("Enter number of copies: "))
                library.add_book(isbn, title, author, year, copies)
            except ValueError:
                print("\nInvalid year or copies number!")
        
        elif choice == "2":
            member_id = input("Enter member ID: ")
            name = input("Enter name: ")
            email = input("Enter email: ")
            library.add_member(member_id, name, email)
        
        elif choice == "3":
            member_id = input("Enter member ID: ")
            isbn = input("Enter book ISBN: ")
            library.borrow_book(member_id, isbn)
        
        elif choice == "4":
            transaction_id = input("Enter transaction ID: ")
            library.return_book(transaction_id)
        
        elif choice == "5":
            library.list_books()
        
        elif choice == "6":
            library.list_members()
        
        elif choice == "7":
            library.list_transactions()
        
        elif choice == "8":
            library.generate_report()
        
        elif choice == "9":
            library.close()
            print("\nGoodbye!")
            break
        
        else:
            print("\nInvalid choice!")

if __name__ == "__main__":
    main()

    