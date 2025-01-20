import sqlite3
import os
import re
import csv
from dotenv import load_dotenv
import bcrypt


password = "password123".encode('utf-8')  # Convertir en bytes
hashed_password = bcrypt.hashpw(password, bcrypt.gensalt())

print(hashed_password)  # Exemple: b'$2b$12$WvMEH4QjA8qUq2Y59X/DfOmdqGclYeDpwlz0asSCMpS8TXyOeMW0C'

'''
L'objectif est de créer un utilisateur pour une connexion
'''

# Charger les variables d'environnement
load_dotenv()

DB_NAME = os.getenv('DB_NAME')

# Connexion à la base de données
con = sqlite3.connect(DB_NAME)
cur = con.cursor()
cur.execute('''
    CREATE TABLE IF NOT EXISTS users
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT UNIQUE NOT NULL,
        password_hash TEXT NOT NULL
    )
''')

# Insertion dans SQLite
cur.execute("INSERT INTO users (username, password_hash) VALUES (?, ?)", ("admin", hashed_password))
con.commit()
con.close()
