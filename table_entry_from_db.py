import sqlite3

def main():
    f = open("entry.txt", "a")


    user_isbn = tidy_isbn(input("Enter ISBN: "))
    if validate_isbn(user_isbn):
        connection = sqlite3.connect('library.db')
        cursor = connection.cursor()
        book_info = cursor.execute("SELECT id, thumbnail, title, publishing_date, read_pages, pages, isbn13, isbn10 FROM books WHERE isbn10 = ? OR isbn13 = ?", (user_isbn, user_isbn)).fetchone()
        print(book_info)
        authors = cursor.execute("SELECT name FROM authors WHERE id IN (SELECT id FROM books WHERE isbn10 = ? OR isbn13 = ?)", (user_isbn, user_isbn)).fetchall()
        f.writelines([
            f"\n<tr>",
            f"\n    <th scope='row'>{book_info[0]}</th>",
            f"\n    <td><img src='{book_info[1]}'></td>",
            f"\n    <td>{book_info[2]}</td>",
            f"\n    <td>{str(authors).replace('[', '').replace(']', '').replace('(', '').replace(')', '')}</td>",
            f"\n    <td></td>",
            f"\n    <td>{book_info[3]}</td>",
            f"\n    <td>{book_info[4]}</td>",
            f"\n    <td>{book_info[5]}</td>",
            f"\n    <td>{book_info[6]}</td>",
            f"\n    <td>{book_info[7]}</td>",
            f"\n</tr>"
        ])

def tidy_isbn(isbn):
    if type(isbn) == int:
        isbn = str(isbn)
    isbn = isbn.replace("-", "")
    return isbn

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

main()