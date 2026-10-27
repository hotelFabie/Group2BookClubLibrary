-- Book Club Library - database schema
-- Module 6 team project

PRAGMA foreign_keys = ON;

CREATE TABLE authors (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 open_library_key TEXT UNIQUE,
 birth_date TEXT,
 death_date TEXT
);

CREATE TABLE books (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 title TEXT NOT NULL,
 first_publish_year INTEGER,
 open_library_key TEXT UNIQUE,
 cover_id INTEGER,
 isbn TEXT,
 subject TEXT
);

CREATE TABLE book_authors (
 book_id INTEGER NOT NULL,
 author_id INTEGER NOT NULL,
 PRIMARY KEY (book_id, author_id),
 FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE,
 FOREIGN KEY (author_id) REFERENCES authors(id) ON DELETE CASCADE
);

CREATE TABLE members (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 name TEXT NOT NULL,
 email TEXT NOT NULL UNIQUE,
 phone TEXT,
 joined_date DATE NOT NULL DEFAULT CURRENT_DATE
);

CREATE TABLE loans (
 id INTEGER PRIMARY KEY AUTOINCREMENT,
 book_id INTEGER NOT NULL,
 member_id INTEGER NOT NULL,
 loan_date DATE NOT NULL DEFAULT CURRENT_DATE,
 due_date DATE NOT NULL,
 return_date DATE,
 FOREIGN KEY (book_id) REFERENCES books(id),
 FOREIGN KEY (member_id) REFERENCES members(id),
 CHECK (return_date IS NULL OR return_date >= loan_date)
);

CREATE INDEX idx_book_authors_author ON book_authors(author_id);
CREATE INDEX idx_loans_book_id ON loans(book_id);
CREATE INDEX idx_loans_member_id ON loans(member_id);
CREATE INDEX idx_loans_book_return ON loans(book_id, return_date);