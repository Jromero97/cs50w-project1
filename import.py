'''
import.py
This file has been created to import a set of objects (Books) into the database.

:param No params need
'''
import os, csv

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Creating engine with SQLAlchemy

engine = create_engine("postgresql://tgrhvaxpufzqan:ad2747794edcfc2a0e5f3e462fb4546d20a526170a3c8f1a11c52b10e571b7a4@ec2-18-233-83-165.compute-1.amazonaws.com:5432/ddtk3c6dt4ecct")

# Create session to allow request of different users be separated

db_session = scoped_session(sessionmaker(bind=engine))

# Getting CSV seed
file = open('books.csv')

# Running the reader
books = csv.reader(file)

next(books)

# Looping through the file read
for isbn, title, author, year in books:
    print(isbn, title, author, year)
    db_session.execute("""
    INSERT INTO books (isbn, title, author, year) VALUES (:book_isbn, :book_title, :book_author, :book_year)
    """, {
        'book_isbn': isbn,
        'book_title': title,
        'book_author': author,
        'book_year': year
    })
    db_session.commit()

print('Books added correctly')
