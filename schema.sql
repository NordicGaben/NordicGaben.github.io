CREATE TABLE books (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    thumbnail TEXT NOT NULL,
    title TEXT NOT NULL,
    subtitle TEXT,
    publishing_date INTEGER NOT NULL,
    pages INTEGER NOT NULL,
    edition TEXT,
    isbn13 TEXT NOT NULL UNIQUE,
    isbn10 TEXT NOT NULL UNIQUE,
    read_pages INTEGER,
    publisher_id INTEGER NOT NULL,
    FOREIGN KEY (publisher_id) REFERENCES publishers (id)
);

CREATE TABLE authors (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE publishers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL
);

CREATE TABLE books_authors (
    book_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    PRIMARY KEY (book_id, author_id),
    FOREIGN KEY (book_id) REFERENCES books(id),
    FOREIGN KEY (author_id) REFERENCES authors(id)
);

CREATE TABLE copies (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    book_id INTEGER,
    location TEXT NOT NULL,
    FOREIGN KEY (id) REFERENCES books (id)
);

