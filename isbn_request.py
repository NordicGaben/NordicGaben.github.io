import requests
import sqlite3


def tidy_isbn(isbn):
    if type(isbn) == int:
        isbn = str(isbn)
    isbn = isbn.replace("-", "")
    return isbn

def isbn10_to_isbn13(isbn10):
    isbn13 = "978" + isbn10[:-1]
    check_digit = 0
    for i, c in enumerate(isbn13):
        weight = 1 if i % 2 == 0 else 3
        check_digit += int(c) * weight
    check_digit = 10 - (check_digit % 10)
    if check_digit == 10:
        check_digit = 0
    isbn13 += str(check_digit)
    return isbn13

def validate_isbn(isbn):
    isbn = str(isbn)
    if len(isbn) == 10:
        # ISBN-10
        sum = 0
        for i in range(len(isbn) - 1):
            sum += int(isbn[i]) * (i + 1)
        check = sum % 11
        return check == 10 and isbn[-1] == 'X' or check == int(isbn[-1])
    elif len(isbn) == 13:
        # ISBN-13
        sum = 0
        for i in range(len(isbn) - 1):
            if i % 2 == 0:
                sum += int(isbn[i])
            else:
                sum += int(isbn[i]) * 3
        check = 10 - (sum % 10)
        return check == int(isbn[-1])
    else:
        return False


def get_relevant_info(isbn):
    isbn = tidy_isbn(str(isbn)) # in case it's an integer
    if len(isbn) == 10:
        isbn = isbn10_to_isbn13(isbn)

    url = "https://www.googleapis.com/books/v1/volumes?q=isbn:" + isbn

    response = requests.get(url)

    if response.status_code == 200:
        data = response.json()

        # The data on the book from the json query.
        volume_info = data['items'][0]['volumeInfo']

        # The value pairs we want to access.
        info_values = ['title', 'subtitle', 'authors', 'publisher', 'publishedDate', 'industryIdentifiers', 'pageCount', 'imageLinks']
        relevant_info = {}
        for value in info_values:
            if value in volume_info:
                relevant_info[value] = volume_info[value]
        return relevant_info
    else:
        print("Request failed with status code:", response.status_code)
        return None



def log_info(isbn, conn, cursor):
    book_info = get_relevant_info(isbn)

    # little bit redudant ?? -----------
    if book_info is None:
        return None

    # Log authors
    authors = book_info['authors']
    author_ids = []
    for author in authors:
        cursor.execute("SELECT id FROM authors WHERE name = ?", (author,))
        author_row = cursor.fetchone() # (tehcincally could be improved with two with same name)
        # if none with that name.
        if author_row is None:
            cursor.execute("INSERT INTO authors (name) VALUES (?)", (author,))
            conn.commit()
            cursor.execute("SELECT id FROM authors WHERE name = ?", (author,))
            author_row = cursor.fetchone()
        author_ids.append(author_row[0]) # gets the id.

    # Log publisher
    publisher = book_info['publisher']
    cursor.execute("SELECT id FROM publishers WHERE name = ?", (publisher,))
    publisher_row = cursor.fetchone()
    if publisher_row is None:
        cursor.execute("INSERT INTO publishers (name) VALUES (?)", (publisher,))
        conn.commit()
        cursor.execute("SELECT id FROM publishers WHERE name = ?", (publisher,))
        publisher_row = cursor.fetchone()
    publisher_id = publisher_row[0]

    # Log book
    title = book_info['title']
    if 'subtitle' in book_info:
        subtitle = book_info['subtitle']
    else:
        subtitle = None

    publishing_date = book_info['publishedDate']
    isbn10 = book_info['industryIdentifiers'][1]['identifier']
    isbn13 = book_info['industryIdentifiers'][0]['identifier']
    pages = book_info['pageCount']
    if 'imageLinks' in book_info:
        thumbnail_link = book_info['imageLinks']['thumbnail']
    else:
        thumbnail_link = 'https://books.google.se/googlebooks/images/no_cover_thumb.gif'

    cursor.execute("SELECT id FROM books WHERE isbn13 = ?", (isbn13,))
    book_row = cursor.fetchone()
    if book_row is None:
        cursor.execute("INSERT INTO books (thumbnail, title, subtitle, publishing_date, pages, isbn13, isbn10, publisher_id) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                                          (thumbnail_link, title, subtitle, publishing_date, pages, isbn13, isbn10, publisher_id))
        conn.commit()
        cursor.execute("SELECT id FROM books WHERE isbn13 = ?", (isbn13,))
        book_row = cursor.fetchone()

    book_id = book_row[0]


    # Log book-author relationship
    for author_id in author_ids:
        cursor.execute("SELECT * FROM books_authors WHERE book_id = ? AND author_id = ?", (book_id, author_id))
        result = cursor.fetchone()
        if not result:
            cursor.execute("INSERT INTO books_authors (book_id, author_id) VALUES (?, ?)", (book_id, author_id))
            conn.commit()


    # Log new copy of the book
    prompt = input(f"Do you wish to log a new copy of '{title}' [y/n]: ")
    if (prompt != 'y'):
        return

    location = input(f"Where is the copy currently located: ")
    cursor.execute("INSERT INTO copies (book_id, location) VALUES (?, ?)", (book_id, location))
    conn.commit()


def main():
    try:
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        print("Database created and successfully connected to SQLite3")

        user_isbn = tidy_isbn(input("Enter ISBN: "))
        if validate_isbn(user_isbn):
                log_info(user_isbn, connection, cursor)

        cursor.close()

    except sqlite3.Error as error:
        print("Error while connecting to sqlite", error)
    finally:


        if connection:
            connection.close()
            print("The SQLite connection is closed.")


main()