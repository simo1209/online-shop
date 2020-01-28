import sqlite3

DB_NAME = 'example.db'

conn = sqlite3.connect(DB_NAME)

conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS ads
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT,
        description TEXT,
        price REAL,
        date_added TEXT,
        creator_id INTEGER,
        active BOOLEAN,
        buyer_id INTEGER
    )
''')
conn.cursor().execute('''
CREATE TABLE IF NOT EXISTS user
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT UNIQUE NOT NULL,
        password TEXT NOT NULL,
        username TEXT UNIQUE NOT NULL,
        address TEXT,
        phone TEXT,
        salt TEXT
    )
''')
conn.commit()


class DB:
    def __enter__(self):
        self.conn = sqlite3.connect(DB_NAME)
        return self.conn.cursor()

    def __exit__(self, type, value, traceback):
        self.conn.commit()
