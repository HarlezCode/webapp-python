from flask import *
import sys, sqlite3, pathlib

'''
Title: My novel list
Author: Chak Ho Huang
Date-created: 2021-06-21
'''


# Creating the app
APP = Flask(__name__)
APP.secret_key = "key"
# - Functions
# -- Flask functions
@APP.route("/new-book", methods=["POST","GET"])
def newBook():
    '''
    Python backend for new book
    :return: (html page)
    '''
    if "USER" not in session:
        # if not logged in
        return redirect(url_for("login"))
    if request.method == "POST":
        # if the submit button is pressed
        if request.form.get("Submit"):
            # Extracting info from the webpage
            TITLE = request.form["TITLE"].upper()
            AUTHOR = request.form["AUTHOR"].upper()
            DESC = request.form["DESC"]
            TAG = "".join(request.form["TAG"].split())
            CONNECTION = sqlite3.connect("database.db")
            CURSOR = CONNECTION.cursor()
            # Making sure that the book is not in the library already
            RESULTS = CURSOR.execute('''
                SELECT
                    *
                FROM
                    library
                WHERE
                    NAME = ?
            ;''',[TITLE]).fetchall()
            if len(RESULTS) > 0:
                return render_template("new-book.html",USER=session["USER"],MSG="This book already exists within the database.")
            # Add the book to the library
            CURSOR.execute('''
                INSERT INTO
                    library(
                        NAME,
                        AUTHOR,
                        DESC,
                        TAG 
                    )
                VALUES(
                    ?, ?, ?, ?
                )
            ;''',[TITLE,AUTHOR,DESC,TAG])
            CONNECTION.commit()
            CONNECTION.close()
            return redirect(url_for("addBook"))

    return render_template("new-book.html",USER=session["USER"])
@APP.route("/database/<ID>",methods=["POST","GET"])
def editDB(ID):
    '''
    Python backend for editing books in the database
    :param ID: (str) ID for the book
    :return: (html page)
    '''
    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()
    # Grab the data from the database
    RAWDATA = CURSOR.execute('''
        SELECT
            NAME,
            AUTHOR,
            DESC,
            TAG
        FROM   
            library
        WHERE
            ID = ? 
    ;''',[ID]).fetchall()
    # Convert the tuple into a list
    DATA = [x for x in RAWDATA[0]]
    if request.method == "POST":
        if request.form.get("Submit"):
            # Pull the data from the website
            NAME = request.form["TITLE"]
            AUTHOR = request.form["AUTHOR"]
            DESC = request.form["DESC"]
            TAGS = request.form["TAG"]

            # Clean up the tags by getting rid of extra spaces
            TAGS = "".join(TAGS.split())

            # update data
            CURSOR.execute('''
                UPDATE
                    library
                SET
                    NAME = ?,
                    AUTHOR = ?,
                    DESC = ?,
                    TAG = ?
                WHERE
                    ID = ?
            ;''',[NAME,AUTHOR,DESC,TAGS,ID])
            # Commit the data
            CONNECTION.commit()
            CONNECTION.close()
            return redirect(url_for("addBook"))
        elif request.form.get("Delete"):
            CONNECTION.close()
            # Make the confirm button visible
            return render_template("edit-database.html", USER=session["USER"], DATA=DATA, VISIBLE="visible")
        elif request.form.get("Back"):
            CONNECTION.close()
            return render_template("edit-database.html", USER=session["USER"], DATA=DATA, VISIBLE="hidden")
        elif request.form.get("Confirm"):
            # deleting the data from the database
            CURSOR.execute('''
                DELETE FROM
                    library
                WHERE
                    ID = ?
            ;''',[ID])
            CONNECTION.commit()
            CONNECTION.close()
            return redirect(url_for("addBook"))
    CONNECTION.close()
    return render_template("edit-database.html",USER=session["USER"],DATA=DATA,VISIBLE="hidden")

@APP.route("/user/<ID>", methods=["POST","GET"])
def editBook(ID):
    '''
    Python backend for edit book
    :param ID: (str) ID for the book
    :return: (html page)
    '''
    if "USER" not in session:
        return redirect(url_for("login"))
    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()
    # Fetching info from the general database
    DATA_1 = CURSOR.execute('''
        SELECT
            NAME,
            AUTHOR,
            DESC,
            TAG
        FROM
            library
        WHERE
            ID = ?
    ;''',[ID]).fetchall()
    # Fetching info from the user list
    DATA_2 = CURSOR.execute(f'''
        SELECT
            RATING,
            REVIEW,
            TAGS
        FROM
            {session['USER']}
        WHERE
            ID = ?
    ;''',[ID]).fetchall()

    # Converting the tuples into a lists for access and
    # making the tags look nice to display on the website
    LIST = [x for x in DATA_1[0]]
    LIST[3] = ", ".join(LIST[3].split(","))
    LIST[3] = LIST[3].replace("_"," ")

    if len(DATA_2) > 0:
        LIST_2 = [x for x in DATA_2[0]]
        LIST_2[2] = ", ".join(LIST_2[2].split(","))
        # Joining the two lists
        LIST = LIST + LIST_2
    else:
        for x in range(3):
            LIST.append("")

    # if the submit button is pressed
    if request.method == "POST" and request.form.get("Submit"):
        # Get form information
        RATING = request.form["RATING"]
        REVIEW = request.form["REVIEW"]
        TAGS = "".join(request.form["NEWTAG"].split())
        NAME = CURSOR.execute('''
            SELECT
                NAME
            FROM
                library
            WHERE
                ID = ?
        ;''',[ID]).fetchone()
        NAME = NAME[0]

        # check if the book is already in the database
        RESULTS = CURSOR.execute(f'''
            SELECT
                *
            FROM
                {session['USER']}
            WHERE
                ID = ?
        ;''',[ID]).fetchall()


        if len(RESULTS) > 0:
            # update the table
            CURSOR.execute(f'''
                UPDATE
                    {session['USER']}
                SET
                    REVIEW = ?,
                    RATING = ?,
                    TAGS = ?
                WHERE
                    ID = ?
            ;''',[REVIEW,RATING,TAGS,ID])
            CONNECTION.commit()
        else:
            # insert into user list database
            CURSOR.execute(f'''
                INSERT INTO
                    {session['USER']}(
                        ID,
                        NAME,
                        REVIEW,
                        RATING,
                        TAGS
                    )
                VALUES(
                    ?, ?, ?, ?, ?
                )
            ;''',[ID,NAME,REVIEW,RATING,TAGS])
        CONNECTION.commit()
        CONNECTION.close()
        return redirect(url_for("home"))
    elif request.method == "POST":
        if request.form.get("Delete"):
            # If delete is pressed
            # updating the displayed info
            LIST[4] = request.form["RATING"]
            LIST[5] = request.form["REVIEW"]
            LIST[6] = request.form["NEWTAG"]
            # toggle on the confirm box
            CONNECTION.close()
            return render_template("edit-book.html",DATA=LIST,USER=session["USER"],VISIBLE="visible")
        elif request.form.get("Back"):
            # updating the displayed info
            LIST[4] = request.form["RATING"]
            LIST[5] = request.form["REVIEW"]
            LIST[6] = request.form["NEWTAG"]
            CONNECTION.close()
            # toggle off the confirm box
            return render_template("edit-book.html", DATA=LIST, USER=session["USER"], VISIBLE="hidden")
        elif request.form.get("Confirm"):
            # delete the data from the database
            CURSOR.execute(f'''
                DELETE FROM
                    {session['USER']}
                WHERE
                    id = ?
            ;''',[ID])
            CONNECTION.commit()
            CONNECTION.close()
            return redirect(url_for("home"))

    CONNECTION.close()
    return render_template("edit-book.html",DATA=LIST,USER=session["USER"],VISIBLE="hidden")


@APP.route("/addbook", methods=["POST","GET"])
def addBook():
    '''

    Python backend for add book
    :return: (html page)
    '''
    if "USER" not in session:
        return redirect(url_for("login"))
    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()

    if request.method == "POST" and request.form.get("SUBMIT"):
        # Search the library for matching results
        INFO = "%" + request.form["SEARCH"].upper() + "%"
        LIBRARY = CURSOR.execute('''
            SELECT
                *
            FROM
                library
            WHERE
                NAME
            LIKE
                ?
            OR 
                AUTHOR
            LIKE
                ?
                
        ;''',[INFO,INFO]).fetchall()
    else:
        LIBRARY = CURSOR.execute('''
            SELECT
                *
            FROM
                library
        ;''').fetchall()
    # Converting the tuple into a list for access
    LIST = [[i for i in x] for x in LIBRARY]
    CONNECTION.close()
    # Cleaning up the data
    for i in range(len(LIST)):
        LIST[i][4] = ", ".join(LIST[i][4].split(","))
        LIST[i][4] = LIST[i][4].replace("_", " ")
    return render_template("add-book.html", DATA=LIST, USER=session["USER"])

@APP.route("/", methods=["POST","GET"])
def home():
    '''
    Renders the home page
    :return: (html page)
    '''

    if "FIRSTTIME" in session:
        session.pop("FIRSTTIME",None)
        return redirect(url_for("guide"))


    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()



    if "USER" not in session:
        CONNECTION.close()
        return redirect(url_for("login"))
    else:
        # Verify all data from the main database (checking for any deleted entries and deleting them in the user table)
        EMPTY = list()
        # Fetch all IDS from the main database to check with the user table
        IDS_LIBRARY = CURSOR.execute('''
            SELECT
                ID
            FROM
                library
        ;''').fetchall()
        # Fetch all IDS from the user table to check with the main database
        IDS_USER = CURSOR.execute(f'''
            SELECT
                ID
            FROM
                {session['USER']}
        ;''').fetchall()
        # Cleaning up the data for the check
        IDS_LIBRARY = [x[0] for x in IDS_LIBRARY]
        IDS_USER = [x[0] for x in IDS_USER]


        # do the check and if it only exists in the user table add it to EMPTY for later deletion
        for i in IDS_USER:
            if i not in IDS_LIBRARY:
                EMPTY.append(i)

        # If there is stuff to be deleted
        if len(EMPTY) > 0:
            # loop through the stuff and delete them one by one
            for x in EMPTY:
                CURSOR.execute(f'''
                    DELETE FROM
                        {session['USER']}
                    WHERE
                        ID = ?
                ;''',[x])
                CONNECTION.commit()

        # Find the user list data
        RESULTS = CURSOR.execute(f'''
            SELECT
                *
            FROM
                {session['USER']}
        ;''').fetchall()

        # Getting the predefined tags from the database by joining the library table with the user table
        PERMTAGS = CURSOR.execute(f'''
            SELECT
                TAG
            FROM
                library
            JOIN
                {session['USER']}
            ON
                library.ID = {session['USER']}.ID
        ;''').fetchall()
        CONNECTION.close()
        # Clean up data
        DATA = list()
        for i,x in enumerate(RESULTS):
            VALUES = list()
            for y in x:
                VALUES.append(y)
            # Changing the tags format to make it display nicely on website
            VALUES[4] = ", ".join(VALUES[4].split(","))
            VALUES[4] = VALUES[4].replace("_", " ")
            LIBRARYTAGS = PERMTAGS[i][0]
            LIBRARYTAGS = ", ".join(LIBRARYTAGS.split(","))
            LIBRARYTAGS = LIBRARYTAGS.replace("_"," ")

            VALUES[4] = LIBRARYTAGS + ", " + VALUES[4]
            # Appends the data
            DATA.append(VALUES)

        # If a button is pressed
        if request.method == "POST":
            # Buttons
            if request.form.get("ADDBOOK"):
                return redirect(url_for("addBook"))
            elif request.form.get("FILTER"):
                if "FILTERS" in session:
                    if "CURRDATA" in session:
                        return render_template("index.html",USER=session["USER"],DATA=session["CURRDATA"],FILTER="visible",FILTERDATA=session["FILTERS"])
                    return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="visible",FILTERDATA=session["FILTERS"])
                else:
                    return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="visible",FILTERDATA=None)
            elif request.form.get("FILTER_SUBMIT"):
                # Pull the data and store it in the session variable
                RATING = request.form["FILTER_RATING"]
                TAGS = request.form["FILTER_TAGS"]
                REVIEW = request.form["FILTER_REVIEW"]
                session["FILTERS"] = [RATING,TAGS,REVIEW]
                if "CURRDATA" in session:
                    return render_template("index.html", USER=session["USER"], DATA=session["CURRDATA"], FILTER="hidden")
                return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="hidden")
            elif request.form.get("SUBMIT"):
                # Pull the data from the session variable
                if "FILTERS" in session:
                    # [RATING, TAGS, REVIEW]
                    FILTERS = session["FILTERS"].copy()
                    # Clean up the tags for search
                    FILTERS[1] = "".join(FILTERS[1].split())
                    FILTERS[1] = FILTERS[1].split(",")
                else:
                    FILTERS = None
                NAME = request.form["SEARCH"]
                # Perform the search
                NEW_DATA = list()

                for i in DATA:
                    MATCH = 0
                    if FILTERS != None:
                        # Match the tags
                        for x in FILTERS[1]:

                            CURRENT_TAG = "".join(i[4].split())
                            CURRENT_TAG = CURRENT_TAG.lower()
                            CURRENT_TAG = CURRENT_TAG.split(",")
                            if x.lower() in CURRENT_TAG:
                                MATCH += 1
                        if i[3] == FILTERS[0]:
                            # Match the rating
                            print(f"Rating match for {i[1]}")
                            MATCH += 1
                        elif FILTERS[2].lower() in i[2].lower():
                            # Match the review
                            if FILTERS[2] != "":
                                print(f"Review match for {i[1]}")
                                MATCH += 1
                        # Match the name
                        if NAME in i[1] and NAME != "":
                            print(f"Name match for {i[1]}")
                            MATCH += 1
                    else:
                        # Match the name
                        if NAME in i[1]:
                            print(f"Name match for {i[1]} with no filters")
                            MATCH += 1

                    if MATCH > 0:
                        # if tags or name matches then append the data
                        NEW_DATA.append([MATCH,i])
                # Sort the list by the best matches and get rid of the first value
                DATA = [x[1] for x in sorted(NEW_DATA,key=lambda x:x[0],reverse=True)]
                session["CURRDATA"] = DATA.copy()

                return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="hidden")
            elif request.form.get("VIEWALL"):
                if "CURRDATA" in session:
                    session.pop("CURRDATA",None)
                if "FILTERS" in session:
                    session.pop("FILTERS", None)
                return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="hidden")
            else:
                return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="hidden")
        else:
            return render_template("index.html",USER=session["USER"],DATA=DATA,FILTER="hidden")

@APP.route("/guide")
def guide():
    '''
    Python backend for guide page
    :return: (html page)
    '''
    if "USER" not in session:
        return redirect(url_for("login"))

    return render_template("guide.html")



@APP.route("/logout")
def logout():
    # pop all the session data
    session.pop("USER",None)
    if "FILTERS" in session:
        session.pop("FILTERS",None)
    if "CURRDATA" in session:
        session.pop("CURRDATA",None)

    return redirect(url_for("login"))

@APP.route("/login/", methods=["POST", "GET"])
def login():
    '''
    Renders the login page
    :return: (html page)
    '''
    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()

    if "USER" in session:
        return redirect(url_for("home"))
    elif request.method == "POST":
        # requesting all the login info and checks with the database
        USERNAME = request.form["USER"]
        PASSWORD = request.form["PASSWORD"]
        FOUND = CURSOR.execute('''
                    SELECT
                        *
                    FROM
                        login
                    WHERE
                        USERNAME = ?
                    AND        
                        PASSWORD = ?
                ;''', [USERNAME, PASSWORD]).fetchall()

        if len(FOUND) > 0:
            # logged in successfully
            session["USER"] = USERNAME
            CONNECTION.close()
            return redirect(url_for("home"))
        else:
            # unsuccessful login attempt
            USER = CURSOR.execute('''
                SELECT
                    *
                FROM
                    login
                WHERE
                    USERNAME = ?
            ;''',[USERNAME]).fetchall()
            CONNECTION.close()
            if len(USER) > 0:
                return render_template("login.html",msg="Password incorrect.")
            else:
                return render_template("login.html",msg="This account does not exist.")
    elif "MSG" in session:
        MSG = session["MSG"]
        session.pop("MSG",None)
        # Display the successfully created account msg
        return render_template("login.html",msg=MSG)
    else:
        return render_template("login.html")
@APP.route("/create-account/", methods=["POST", "GET"])
def createAccount():
    '''
    Renders the create account page
    :return: (html page)
    '''

    CONNECTION = sqlite3.connect("database.db")
    CURSOR = CONNECTION.cursor()
    if request.method == "POST":
        # Checking if the username is within the database
        USERNAME = request.form["USER"]
        PASSWORD = request.form["PASSWORD"]
        FOUND = CURSOR.execute('''
            SELECT
                *
            FROM
                login
            WHERE
                USERNAME = ?        
        ;''',[USERNAME]).fetchall()

        if len(FOUND) > 0:
            # if it exists then ask again
            return render_template("create-account.html",msg="This username is already in use.")
        else:
            # check if the name is valid (preventing accidental sql injections)
            ALPHABET = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'
            NUMBERS = '1234567890'

            for x in USERNAME:
                if x not in ALPHABET and x not in NUMBERS:
                    return render_template("create-account.html",msg="Invalid characters in name. Please ensure your username only have alphanumeric characters.")
            if len(PASSWORD) < 4:
                return render_template("create-account.html",msg="Your password must be at least 4 characters.")

            # otherwise add to the database and redirect to the login page
            CURSOR.execute('''
            INSERT INTO
                login(
                    USERNAME,
                    PASSWORD
                )
            VALUES(
                ?, ?
            )
            ;''',[USERNAME, PASSWORD])
            CONNECTION.commit()
            # create the list for that user
            CURSOR.execute(f'''
                    CREATE TABLE
                    {USERNAME}(
                        ID INTEGER PRIMARY KEY,
                        NAME TEXT NOT NULL,
                        REVIEW TEXT,
                        RATING TEXT,
                        TAGS TEXT            
                    )
                ;''')
            CONNECTION.commit()
            CONNECTION.close()
            session["MSG"] = "Successfully created your account!"
            session["FIRSTTIME"] = True
            return redirect(url_for("login"))
    else:
        return render_template("create-account.html")


# -- Sqlite functions
# -- Processing
def basicDBSetup():
    '''
    Create the login database table
    :return: (none)
    '''
    # Setup login table
    CURSOR.execute('''
        CREATE TABLE
            login(
                USERNAME TEXT PRIMARY KEY,
                PASSWORD TEXT NOT NULL
            )
    ;''')
    CONNECTION.commit()
    # Setup the global book table
    CURSOR.execute('''
        CREATE TABLE
            library(
                ID INTEGER PRIMARY KEY,
                NAME TEXT NOT NULL,
                AUTHOR TEXT NOT NULL,
                DESC TEXT NOT NULL,
                TAG TEXT NOT NULL
            )
    ;''')
    CONNECTION.commit()
def preload(FILE):
    '''
    Preload some books into the database to use.
    :param FILE: (txt)
    :return: (none)
    '''
    RAW_DATA = open(FILE)
    RAW_DATA = RAW_DATA.readlines()

    for x in RAW_DATA:
        DATA = x.split(";")
        DATA[3] = "".join(DATA[3].rstrip().split())
        # add the book into database
        CURSOR.execute('''
            INSERT INTO
                library(
                    NAME,
                    AUTHOR,
                    DESC,
                    TAG
                )
            VALUES(
                ?, ?, ?, ?
            )
        ;''',DATA)
        CONNECTION.commit()

# - Variables
FIRST_RUN = True
DATABASE_NAME = "database.db"

if (pathlib.Path.cwd() / DATABASE_NAME).exists():
    FIRST_RUN = False

CONNECTION = sqlite3.connect(DATABASE_NAME)
CURSOR = CONNECTION.cursor()


# - Main Program Code
if FIRST_RUN:
    # Setup database
    basicDBSetup()
    preload("preload.txt")



if __name__ == "__main__":
    APP.run(debug=True)
