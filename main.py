import sqlite3
import csv

'''
L'objectif est de créer une base de données avec les données présentes dans les fichiers csv
Pour le traitement des messages spam.
'''
# Connexion à la base de données 
con = sqlite3.connect("messages.db")
cur = con.cursor()

cur.execute(''' 
    CREATE TABLE IF NOT EXISTS messages 
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        type TEXT NOT NULL,
        content TEXT NOT NULL
    )
    ''')

cur.execute('''
    CREATE TABLE IF NOT EXISTS mots_spam
    (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        word TEXT NOT NULL
    )
''')

csv_file = "mots_uniques_spam.csv"
with open(csv_file, encoding="utf-8") as f:
    csv_reader = csv.reader(f)  # Pas de délimiteur, chaque ligne contient un seul mot
    next(csv_reader) # Pour les 
    for row in csv_reader:
        if len(row) == 1:  # Chaque ligne contient un mot
            mot = row[0] 
            cur.execute('''
            INSERT INTO mots_spam (word)
            VALUES (?)
            ''', (mot,))

csv_file = "SMSSpamCollection.csv"
with open(csv_file, encoding="utf-8") as f:
    csv_reader = csv.reader(f, delimiter=';')
    for row in csv_reader:
        if len(row) == 2:
            message_type, message_content = row
            cur.execute('''
            INSERT INTO messages (type, content)
            VALUES (?, ?)
            ''', (message_type, message_content))

con.commit()
con.close()
print("Données insérées avec succès dans la base de données SQLite.")