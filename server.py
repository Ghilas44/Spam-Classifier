from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import sqlite3, os, re
from dotenv import load_dotenv

'''
L'objectif est d'envoyer un message et de vérifier si il s'agit d'un spam.
Nous récupérons les mots présents dans le message envoyé et vérifions si il est présent dans la 
'''

load_dotenv()

def get_db_connection():
    con = sqlite3.connect(os.getenv('DB_NAME'))
    con.row_factory = sqlite3.Row  # Retourne des résultats sous forme de dictionnaire
    return con

app = FastAPI()


templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/", response_class=HTMLResponse)
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"heading": "Votre message est-il un spam ?"})

@app.post("/resultats", response_class=HTMLResponse)
async def read_form(request: Request, message: Annotated[str, Form(...)]):
    """
    Route POST pour vérifier si le message contient un mot spam.
    """
    # Séparer le message en mots
    mots_message = re.findall(r'\b\w+\b', message.lower())  # Extrait les mots du message
    print(mots_message)
    # Vérifier la présence de mots spam dans la table 'mots_spam'
    mots_trouves = []

    # Utiliser une connexion à la base de données dans la route
    con = get_db_connection()
    cur = con.cursor()

    for mot in mots_message:
        cur.execute("SELECT 1 FROM mots_spam WHERE word = ?", (mot,))
        if cur.fetchone():  # Si le mot est trouvé dans la table mots_spam
            mots_trouves.append(mot)

    # Vérifier si des mots spam ont été trouvés
    if mots_trouves:
        return templates.TemplateResponse(
            "resultats.html", 
            context={
                "request": request, 
                "message": message, 
                "result": f"Message contenant des mots spam : {', '.join(mots_trouves)}"
            }
        )
    else:
        return templates.TemplateResponse(
            "resultats.html", 
            context={
                "request": request, 
                "message": message, 
                "result": "Ce message ne contient pas de mots spam."
            }
        )
    
'''
Pour les tests -> retourner un json
'''
@app.post("/check")
async def check_spam(message: Annotated[str, Form(...)]):
    """
    Route POST pour vérifier si un message contient des mots spam.
    Retourne un JSON indiquant si c'est un spam.
    """
    # Séparer le message en mots
    mots_message = re.findall(r'\b\w+\b', message.lower())
    print(mots_message)
    # Utiliser une connexion à la base de données dans la route
    con = get_db_connection()
    cur = con.cursor()
    # Vérifier la présence de mots spam dans la table 'mots_spam'
    for mot in mots_message:
        cur.execute("SELECT 1 FROM mots_spam WHERE word = ?", (mot,))
        if cur.fetchone():  # Si un mot spam est trouvé
            return {"is_spam": True}

    return {"is_spam": False}


