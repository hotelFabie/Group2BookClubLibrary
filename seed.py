import sqlite3
import os

"""
Creates a database file, unless there is one already, in which case the old file is deleted and 
a new one is created. Populates the database with dummy data for testing.
"""
def connect():
    conn = sqlite3.connect("library.db")
    conn.execute("PRAGMA foreign_keys = ON")
    return conn

def seed_db():
    # --- The Reset Mechanic ---
    if os.path.exists("library.db"):
        os.remove("library.db")
        print("Old database detected and removed. Building a fresh one...")
    # --------------------------
    
    conn = connect()
    
    # Builds the tables from the SQL blueprint
    file = open("schema.sql", "r")
    schema_script = file.read()
    file.close()
    
    conn.executescript(schema_script)
    
    #Injects hardcoded test data automatically
    conn.execute("""
        INSERT INTO authors (name, birth_date) 
        VALUES 
        ('J.R.R. Tolkien', '1892-01-03'),
        ('Neil Gaiman', '1960-11-10'),
        ('Terry Pratchett', '1948-04-28'),
        ('Astrid Lindgren', '1907-11-14')
    """)
    
    conn.execute("""
        INSERT INTO books (title, first_publish_year, subject) 
        VALUES 
        ('The Fellowship of the Ring', 1954, 'Fantasy'),
        ('Good Omens', 1990, 'Fantasy'),
        ('American Gods', 2001, 'Fantasy'),
        ('Emil i Lönneberga', 1963, 'Childrens Fiction'),
        ('Pippi Långstrump', 1945, 'Childrens Fiction')
    """)
    
    conn.execute("""
        INSERT INTO members (name, email) 
        VALUES 
        ('Alan Normal', 'alan.normal@example.com'),
        ('Anna Black', 'anna.blackl@example.com'),
        ('John Doe', 'john.doel@example.com'),
        ('Jane Doe', 'jane.doel@example.com')
    """)
    
    conn.execute("""
        INSERT INTO book_authors (book_id, author_id) 
        VALUES 
        (1, 1), -- The Fellowship of the Ring by J.R.R. Tolkien
        (2, 2), -- Good Omens by Neil Gaiman
        (2, 3), -- Good Omens by Terry Pratchett
        (3, 2), -- American Gods by Neil Gaiman
        (4, 4), -- Emil i Lönneberga by Astrid Lindgren
        (5, 4)  -- Pippi Långstrump by Astrid Lindgren
    """)

    conn.execute("""
        INSERT INTO loans (book_id, member_id, loan_date, due_date, return_date) 
        VALUES 
        (2, 1, '2026-10-27', '2026-11-27', NULL),         -- Active loan (Alan borrowed Good Omens)
        (4, 2, '2026-10-01', '2026-11-01', '2026-10-15'), -- Returned loan (Anna borrowed Emil)
        (3, 3, '2026-09-01', '2026-10-01', NULL)          -- Overdue loan (John borrowed American Gods)
    """)
    
    # Saves the injected data and closes the connection
    conn.commit()
    print("Database successfully built and seeded!")
    conn.close()

def main():
    seed_db()

if __name__ == "__main__":
    main()