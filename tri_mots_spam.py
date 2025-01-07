import sqlite3
import os
import re
import csv
from dotenv import load_dotenv


'''
L'objectif est de récupérer les mots présents uniquement dans les spams.
Ainsi, tous les messages qui seront envoyés avec un mot ou plusieurs présents dans les spams sera considéré comme tel. Sinon, ce sera un ham.
'''

# Charger les variables d'environnement
load_dotenv()

DB_NAME = os.getenv('DB_NAME')

# Connexion à la base de données
con = sqlite3.connect(DB_NAME)
cur = con.cursor()

def extraire_mots_uniques_spam():
    # Ensembles pour stocker les mots
    mots_spam = set()
    mots_ham = set()

    # Requête pour récupérer tous les messages de type 'spam'
    cur.execute("SELECT content FROM messages WHERE type = 'spam'")
    messages_spam = cur.fetchall()

    # Récupérer les mots dans les spams
    for (content,) in messages_spam:
        mots_spam.update(re.findall(r'\b\w+\b', content.lower()))  # Normalisation en minuscules

    # Requête pour récupérer tous les messages de type 'ham'
    cur.execute("SELECT content FROM messages WHERE type = 'ham'")
    messages_ham = cur.fetchall()

    # Récupérer les mots dans les hams
    for (content,) in messages_ham:
        mots_ham.update(re.findall(r'\b\w+\b', content.lower()))  # Normalisation en minuscules

    # Différence entre les ensembles pour trouver les mots uniquement dans les spams
    mots_uniques_spam = mots_spam - mots_ham

    return mots_uniques_spam

# Appeler la fonction
mots_uniques_spam = extraire_mots_uniques_spam()

# Afficher les mots uniques
print("Mots présents uniquement dans les spams :")
print(mots_uniques_spam)

# Exporter les mots uniques dans un fichier CSV
with open('mots_uniques_spam.csv', mode='w', newline='', encoding='utf-8') as file:
    writer = csv.writer(file)
    writer.writerow(['Mot'])  # Écrire l'en-tête
    for mot in mots_uniques_spam:
        writer.writerow([mot])  # Écrire chaque mot dans une nouvelle ligne

print("Les mots uniques dans les spams ont été exportés dans 'mots_uniques_spam.csv'.")

# Fermer la connexion
con.close()
