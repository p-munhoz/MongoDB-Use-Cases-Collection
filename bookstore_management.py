from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

# Connect to MongoDB
client = MongoClient('mongodb://admin:password@localhost:27017/')
db = client['bookstore']
collection = db['books']

# Function to insert a book
def insert_book(title, author, genre, published_date, price):
    """
    Inserts a book into the bookstore collection.

    Parameters:
    title (str): the title of the book
    author (str): the author of the book
    genre (str): the genre of the book
    published_date (datetime.datetime): the date the book was published
    price (float): the price of the book

    Returns:
    InsertOneResult: a pymongo InsertOneResult object
    """
    book = {
        "title": title,
        "author": author,
        "genre": genre,
        "published_date": published_date,
        "price": price
    }
    return collection.insert_one(book)

# Function to find books by genre
def find_books_by_genre(genre):
    """
    Finds books by genre.

    Parameters:
    genre (str): the genre of the book

    Returns:
    pymongo.cursor.Cursor: a pymongo cursor object with the books matching the given genre
    """
    return collection.find({"genre": genre})

# Function to update book price
def update_book_price(book_id, new_price):
    """
    Updates the price of a book in the bookstore collection.

    Parameters:
    book_id (str): the ObjectId of the book to update
    new_price (float): the new price of the book

    Returns:
    pymongo.results.UpdateResult: a pymongo UpdateResult object
    """
    return collection.update_one(
        {"_id": ObjectId(book_id)},
        {"$set": {"price": new_price}}
    )

# Function to delete a book
def delete_book(book_id):
    """
    Deletes a book from the bookstore collection.

    Parameters:
    book_id (str): the ObjectId of the book to delete

    Returns:
    pymongo.results.DeleteResult: a pymongo DeleteResult object
    """
    return collection.delete_one({"_id": ObjectId(book_id)})

# Main execution
if __name__ == "__main__":
    # Insert some sample books
    insert_book("The Great Gatsby", "F. Scott Fitzgerald", "Classic", datetime.datetime(1925, 4, 10), 12.99)
    insert_book("To Kill a Mockingbird", "Harper Lee", "Fiction", datetime.datetime(1960, 7, 11), 14.99)
    insert_book("1984", "George Orwell", "Science Fiction", datetime.datetime(1949, 6, 8), 11.99)
    
    print("Books inserted successfully.")

    # Find books by genre
    print("\nScience Fiction books:")
    for book in find_books_by_genre("Science Fiction"):
        print(f"{book['title']} by {book['author']}")

    # Update a book's price
    book_to_update = collection.find_one({"title": "1984"})
    if book_to_update:
        update_result = update_book_price(book_to_update['_id'], 13.99)
        print(f"\nUpdated '1984' price. Modified count: {update_result.modified_count}")

    # Delete a book
    book_to_delete = collection.find_one({"title": "The Great Gatsby"})
    if book_to_delete:
        delete_result = delete_book(book_to_delete['_id'])
        print(f"\nDeleted 'The Great Gatsby'. Deleted count: {delete_result.deleted_count}")

    # Show all remaining books
    print("\nRemaining books:")
    for book in collection.find():
        print(f"{book['title']} by {book['author']} - ${book['price']}")

    # Close the connection
    client.close()