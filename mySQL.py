from datetime import datetime
import sqlite3
from SQL.Activity import Activity
from SQL.Comment import Comment
from SQL.Experience import Experience
from SQL.Organization import Organization
from SQL.Post import Post
from SQL.User import User
from SQL.Education import Education

class dataSQL:
    def __init__(self, dbfile = "database.db"):
        """
        Initialize a DatabaseManager with the specified SQLite database file.

        Parameters:
        - dbfile (str): The path to the SQLite database file.
        """
        self.dbfile = dbfile
        self.connection = sqlite3.connect(self.dbfile)
        self.cursor = self.connection.cursor()

        self.create_tables()

    def create_tables(self):
        #0 -> DEFAULT; FALSE
        #1 -> NOT DEFAULT; TRUE
        self.cursor.executescript('''
            CREATE TABLE IF NOT EXISTS users (
                "id"	INTEGER PRIMARY KEY AUTOINCREMENT,
                "token"	TEXT UNIQUE,
                "username"	TEXT DEFAULT NULL,
                "email"	INTEGER,
                "is_verified" INTEGER NOT NULL DEFAULT 0,
                "is_staff"	INTEGER NOT NULL DEFAULT 0,
                "linkedin_url" TEXT DEFAULT NULL,
                "github_url" TEXT DEFAULT NULL,
                "description" TEXT DEFAULT NULL,
                "logo_url" TEXT NOT NULL
            );
                                  
            CREATE TABLE IF NOT EXISTS posts (
                "id"	INTEGER NOT NULL UNIQUE,
                "owner_id"	INTEGER NOT NULL,
                "title"	TEXT NOT NULL,
                "content"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
                                  
            CREATE TABLE IF NOT EXISTS "experiences" (
                "id"	INTEGER,
                "owner_id"	INTEGER NOT NULL,
                "company_name"	TEXT NOT NULL,
                "company_logo_url"	TEXT NOT NULL,
                "position_title"	TEXT NOT NULL,
                "position_description"	TEXT,
                "dates" TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
                                  
            CREATE TABLE IF NOT EXISTS "educations" (
                "id"	INTEGER,
                "owner_id"	INTEGER NOT NULL,
                "tuition_name"	TEXT NOT NULL,
                "tuition_logo_url"	TEXT NOT NULL,
                "position_description"	TEXT,
                "dates" TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
                                  
            CREATE TABLE IF NOT EXISTS "organizations" (
                "id"	INTEGER NOT NULL UNIQUE,
                "owner_id"	INTEGER NOT NULL,
                "name"	TEXT NOT NULL,
                "industry"	TEXT NOT NULL,
                "tagline"	TEXT,
                "website"	TEXT,
                "github_link"	TEXT,
                "size" TEXT,
                "logo_url" TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
                                  
            CREATE TABLE IF NOT EXISTS "activity" (
                "id"	INTEGER NOT NULL UNIQUE,
                "owner_id"	INTEGER NOT NULL,
                "type"	TEXT NOT NULL,
                "date"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
                                  
            CREATE TABLE IF NOT EXISTS "comments" (
                "id"	INTEGER NOT NULL UNIQUE,
                "owner_id"	INTEGER NOT NULL,
                "post_owner_id"	INTEGER NOT NULL,
                "content"	TEXT NOT NULL,
                PRIMARY KEY("id" AUTOINCREMENT)
            );
            ''')
        
        # users
        # id -> unique id (each user assigned one)
        # token -> user's github id or OAUTH token (should be unique)
        # username -> user's github name
        # email -> user's github email

        # posts
        # id -> unique id (each post assigned one)
        # owner_id -> unique id of user
        # TODO! 

        # experiences - (CONNECTED TO USERS EXPERIENCE)
        # id -> Each experience unique id
        # associated_user_id -> FOREIGN KEY OF user "id"
        # company_name -> Name of Company
        # company_logo_url -> URL of Company
        # position_title -> Position Title
        # position_description -> Position Description (Optionally Null)
        # dates -> Date of work
    
    def execute_script(self, target):
        self.cursor.executescript(f'''{target}''')

    def connect(self) -> sqlite3.Connection:
        """
        Establish a connection to the SQLite database.

        Returns:
        - sqlite3.Connection: A database connection object.
        """
        return sqlite3.connect(self.dbfile)

    def close(self):
        """Commit any pending changes and close the database connection."""
        self.connection.commit()
        self.connection.close()

    

    def get_count(self, target):
        self.connection = sqlite3.connect(self.dbfile)
        self.cursor = self.connection.cursor()


        self.cursor.execute("SELECT COUNT(*) FROM users WHERE token = ?", (target,))
        count = self.cursor.fetchone()[0]
        

        self.close()
        return count
    
    def user_exists(self, token):
        count = self.get_count(token)
        return int(count) >= 1


    def use_database(self, query: str, values: tuple = None, easySelect:bool=True):
        """
        Execute a database query and return the result.

        Parameters:
        - query (str): The SQL query to execute.
        - values (tuple, optional): A tuple of parameter values to bind to the query.

        Returns:
        - result: The result of the query execution. If it's a SELECT query, it returns the first row as a tuple; otherwise, it returns None.
        """
        self.connection = self.connect()

        res = self.connection.execute(query, values)
        returned_value = None
        if "select" in query.lower() and easySelect:
            returned_value = res.fetchone()
        else:
            returned_value = res.fetchall()

        self.close()

        return returned_value
    
    def record_to_activity(self, id, type):
        #id -> ID of item; USER ID (or BUSINESS ID) is connected to it
        #type -> Post; Account Creation; Etc.
        self.use_database(
            'INSERT INTO activity (owner_id, type, date) VALUES (?, ?, ?)',
            (
                id, type, datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            ),
        )
    
    def get_experiences(self, users_id):
        list = self.use_database(
            "SELECT * from experiences where owner_id = ?", (users_id,), easySelect=False
        )

        experience_list = [Experience(*row) for row in list]

        return experience_list
    
    def get_educations(self, users_id):
        list = self.use_database(
            "SELECT * from educations where owner_id = ?", (users_id,), easySelect=False
        )

        experience_list = [Education(*row) for row in list]
        return experience_list

    def get_user(self, users_id):
        user_raw = self.use_database(
            "SELECT * from users where id = ?", (users_id,), easySelect=False
        )
        #print(user_raw)
        user = [User(*row) for row in user_raw]

        return user[0]
    
    def get_post_by_id(self, id):
        raw = self.use_database(
            "SELECT * from posts where id = ?", (id,), easySelect=False
        )
        return [Post(*row) for row in raw][0] #only one
    
    def get_post_by_user_id(self, users_id):
        raw = self.use_database(
            "SELECT * from posts where owner_id = ?", (users_id,), easySelect=False
        )
        #print(user_raw)
        return [Post(*row) for row in raw]

    def get_all_posts(self):
        raw = self.use_database(
            "SELECT * from posts", (), easySelect=False
        )
        #print(user_raw)
        return [Post(*row) for row in raw]

    
    def get_all_activity(self):
        raw = self.use_database(
            "SELECT * from activity;", (),  easySelect=False
        )
        return tuple(Activity(*row) for row in raw)

    
    def owner_of(self, activity:Activity):
        #activity -> Activity class
        raw = self.use_database(
            f"SELECT * FROM {activity.type} WHERE id = {activity.id} AND owner_id = {activity.owner_id}",
            (),
            easySelect=False
        )

        return tuple(Activity.tableType(*row) for row in raw)[0]

    
    def get_organizations(self, id=None, owner_id=None):
        if target := id:
            raw = self.use_database(
                "SELECT * from organizations WHERE id = ?", (target), easySelect=False
            )
        elif target := owner_id:
            raw = self.use_database(
                "SELECT * from organizations WHERE owner_id = ?", (int(target),), easySelect=False
            )
        else:
            raw = self.use_database(
                "SELECT * from organizations", (), easySelect=False
            )
        return [Organization(*row) for row in raw]
    
    def get_comments(self):
        raw = self.use_database(
            "SELECT * from comments", (), easySelect=False
        )
        return [Comment(*row) for row in raw]

    def is_staff(self, users_id):

        if (item := self.use_database(
            "SELECT is_staff from users where id = ?", (users_id,)
        )[0]) == 0: return False 
        else: return True


    #This is Staff Related Stuff
    
    def get_tables(self):
        table_names = self.use_database(
            "SELECT name FROM sqlite_schema WHERE type ='table' AND name NOT LIKE 'sqlite_%';", () ,easySelect=False
        )
        
        return table_names
    
    def get_all_data(self, table="users"):

        self.connection = self.connect()

        res = self.connection.execute(f"SELECT * FROM {table}")
        column_names = [description[0] for description in res.description]
        returned_value = res.fetchall()

        count = self.connection.execute(f"SELECT COUNT(*) FROM {table}").fetchone()

        self.close()

        return column_names, returned_value, count
    
    
        
database = dataSQL("database.db")
