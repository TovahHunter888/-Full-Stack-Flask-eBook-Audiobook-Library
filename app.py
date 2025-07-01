# Bringing in the libraries we need for this app
# Flask is the lightweight web framework we're using to build our app
from flask import Flask, render_template, request, redirect, url_for
# This lets us talk to our MySQL database
import mysql.connector
# We'll use this to capture the exact date and time when a user signs up
from datetime import datetime

# Start up our Flask app
app = Flask(__name__)

# Let's set up the details we need to connect to our MySQL database
MY_SERVER = 'localhost'  # This is where our database server lives (not the database name)
MY_PORT = '3306'  # Default port for MySQL
# The user name that has access to the database server and the database
# This may also include a password, but does not for us
MY_USERNAME = 'root'  # This is the user that can access the database
MY_PASSWORD = 'J#32@db8' # Our database password
 # This is the actual database we’ll be working with
MY_DATABASE = 'database_the_reading_nookie_new'

# Function to create the 'user' table if it doesn't already exist
def create_table():
     # Connect to the database using the details above
    conn = mysql.connector.connect(
        host=MY_SERVER,
        port=MY_PORT,
        user=MY_USERNAME,
        password=MY_PASSWORD,
        database=MY_DATABASE
    )
    cursor = conn.cursor () # The database is created here
    # MYSQL command to create the table
    cursor.execute ('''
        CREATE TABLE IF NOT EXISTS user(
            id INT AUTO_INCREMENT PRIMARY KEY,
            col_first_name VARCHAR(256) NOT NULL,
            col_last_name VARCHAR(256) NOT NULL,
            col_username VARCHAR(256),
            col_email VARCHAR(255),
            col_date_created DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Save changes and close the connection
    conn.commit()
    conn.close()

# Route for our home page
@app.route('/')
# When someone visits the home page, this function loads the template
def index():
    return render_template('index.html')

# Route to handle adding a new user from the form submission
@app.route('/add_user', methods=['POST'])
# Add a new user to the dataabase
def add_user():
     # Grab the form data submitted by the user
    first_name = request.form['col_first_name']
    last_name = request.form['col_last_name']
    username = request.form['col_username']
    email = request.form['col_email']
    date_created = datetime.now() # # Get the current date and time for when the user signed up

    # Connect to our database
    conn = mysql.connector.connect(
        host=MY_SERVER,
        port=MY_PORT,
        user=MY_USERNAME,
        password=MY_PASSWORD,
        database=MY_DATABASE
    )
    cursor = conn.cursor()

     # Insert the new user's info into the 'user' table
    cursor.execute ('''INSERT INTO user (col_first_name,col_last_name,col_username,col_email,col_date_created) VALUES 
                    (%s,%s,%s,%s,%s)''', 
                    (first_name, last_name,username,email,date_created))

    # Save the new entry and close the database connection
    conn.commit()
    conn.close()

    return redirect(url_for('library'))

# Route to show our library of ebooks and audiobooks
@app.route('/library')
def library():
    connection = None 
    try:
        # Connect to the database
        connection = mysql.connector.connect(
            host=MY_SERVER,
            port=MY_PORT,
            user=MY_USERNAME,
            password=MY_PASSWORD,
            database=MY_DATABASE
        )
        # We use a cursor to run MYSQL commands
        cursor = connection.cursor()

        # MYSQL command to grab book data from the 'book' table
        query ="SELECT col_title, col_genre,col_author,col_ebook_format,col_audiobook_format, col_date_created FROM book ORDER BY col_title"

        #Execute the query
        cursor.execute(query)

        # Pull all the results from the query
        cursor_books = cursor.fetchall()

        # Close the connection so we don’t overload the server with open connections
        connection.close()
        print("*"*50)
        print(cursor_books)
        print("*"*50)
        book_names= [row[0] for row in cursor_books]

        # Send the book data to the library.html page to display it
        return render_template('library.html', cursor_books = cursor_books)
    
   # If something goes wrong, show an error page with details
    except Exception as error:
        return f'''<h1> Error</h1>
            <p>Sorry, there was an error connecting to the database</p>
            <p>CHECH THE SERVER and make sure it is running.</p>
            <p>CHECK THE CONNECTION STRING and make sure it is correct.</p>
            <p>ERROR message: {error}</p> 
            ''' 
# Route to display user reviews from the reading nookie database
# This is like a special doorway on our website. When someone types /reviews,
# this code gets activated to show them all the book reviews!
@app.route('/reviews')
def reviews_book():
    connection = None # We start by saying we don't have a database connection yet.
    try:
        # Connect to the database
        # This is where we try to open our database
        # to get all the book and review information.
        connection = mysql.connector.connect(
            host=MY_SERVER,
            port=MY_PORT,
            user=MY_USERNAME,
            password=MY_PASSWORD,
            database=MY_DATABASE

        )

       # We use a cursor to run MYSQL commands
        # A cursor  points to what we want to do
        # in the database,  "get this information" or "put this information here."
        cursor = connection.cursor()
        
        # SQL query to get reviews and book titles
        # We're asking for the review's ID, the review's title, comments, rating,
        # when it was reviewed, the username of the person who wrote it,
        # and most importantly, the REAL book title from the 'book' table.
        query = '''
            SELECT
                r.pk_review_id, r.col_rev_title, r.col_comments, r.col_rating_stars, col_review_date,
                u.col_username, b.col_title, b.col_cover_image
            FROM review r
            JOIN book b ON r.fk_book_id = b.col_id_pk
            JOIN user u ON r.fk_user_id = u.col_user_id
            ORDER BY b.col_title ASC, r.col_review_date DESC 
        '''

        # Execute the review query
        # We tell our (cursor) to ask the database the (query)!
        cursor.execute(query)
        # Pull all the results from the query
        # After asking, we get all the answers back from the database.
        # This 'cursor_reviews' will be a list of all the review details.
        cursor_reviews = cursor.fetchall()  

        # Close the connection
        # so we don't overload the server with too many open connections.
        connection.close()


        ## Now, let's group our reviews by book title!
        # We'll use a container called 'grouped_reviews_by_book'.
        # It's like a big box, and inside it, we'll have smaller boxes for each book title.
        grouped_reviews_by_book = {}

        # We're going to look at each review one by one from the list we got from the database.
        for row in cursor_reviews:
           # Each 'row' is one review from our database. Let's give names to its pieces:
            pk_review_id = row[0]
            col_rev_title = row[1] # This is the title *of the review*, not the book
            col_comments = row[2]
            col_rating_stars = row[3]
            col_review_date = row[4]
            col_username = row[5]
            col_title = row[6] # This is the title of the book
            col_cover_image = row[7]
            
            # Check if we've seen this book title before.
            # If we haven't seen this book title before, let's create a new little box for it.
            if col_title not in grouped_reviews_by_book:
                grouped_reviews_by_book[col_title] = {
                    'book_cover': col_cover_image,
                    'review': []  # This  box will hold a list of reviews
                 }

            # Now, let's put the details of this review into the right book's box.
            # Now, we take the details of THIS review and add them to the correct book's basket.
            # We put them in as a small dictionary so each piece has a clear label.
            grouped_reviews_by_book[col_title]['review'].append({
                "id": pk_review_id,
                "review_title": col_rev_title,
                "comments": col_comments,
                "rating": col_rating_stars,
                "review_date": col_review_date,
                "username": col_username
            })

        # Send the grouped review data to the 'reviews.html' page to show it.
        # We're sending our 'grouped_reviews_by_book' special container.
        return render_template('review.html', grouped_reviews = grouped_reviews_by_book )

    # If something goes wrong show an error message
    except Exception as error:
        # We catch the problem (the 'error') and show a friendly message
        # so we know what went wrong.
        return f'''<h1>Error</h1>
            <p>Oops! Something went wrong when trying to get the reviews.</p>
            <p>ERROR message: {error}</p>'''


# This is the entry point for running the app
if __name__ == '__main__':
    print("Trying to start the web app")

     # Make sure the user table exists
    create_table()
    print("starting debug mode")
    # Start the Flask app with debug mode on (so we can see helpful error messages)
    app.run(debug=True)
    print("web app started succesfully")
    print("Go to http://127.0.0.1:5000/ to see the web app.")


