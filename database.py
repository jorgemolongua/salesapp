import sqlite3

database = sqlite3.connect("JWdatabase.db")
dbcursor = database.cursor()

dbcursor.execute(""" 
CREATE TABLE IF NOT EXISTS users (
    idNumber INTEGER PRIMARY KEY AUTOINCREMENT,
    firstName TEXT NOT NULL,
    lastName TEXT NOT NULL,
    userName TEXT NOT NULL,
    password TEXT NOT NULL,
    level INTEGER /* 1=USER, 2=SUPERVISOR, 3=ADMIN */
)
""" )

database.commit()
database.close()


