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

dbcursor.execute("""CREATE TABLE IF NOT EXISTS products (
	productNumber TEXT PRIMARY KEY,
	productName TEXT,
	productDescription TEXT,
	units INTEGER,
	location TEXT,
	costPrice REAL,
    salePrice REAL
)
""")

dbcursor.execute("""CREATE TABLE IF NOT EXISTS sales (
    saleNumber INTEGER PRIMARY KEY AUTOINCREMENT,
	productNumber TEXT NOT NULL,
	units INTEGER,
	salePrice REAL,
	date TEXT,
    user TEXT
)
""")

database.commit()
database.close()


