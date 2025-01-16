from fastapi import FastAPI, Request, Form, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import sqlite3, os, re
from dotenv import load_dotenv
from pydantic import BaseModel
import random

'''
L'objectif est d'envoyer un message et de vérifier si il s'agit d'un spam.
Nous récupérons les mots présents dans le message envoyé et vérifions si il est présent dans la 
'''

load_dotenv()

def get_db_connection():
    con = sqlite3.connect('messages.db')
    con.row_factory = sqlite3.Row  # Retourne des résultats sous forme de dictionnaire
    return con

app = FastAPI(
    title="Spam-Classifier",
    description="Cette API permet de vérifier si un message contient des mots considérés comme spam ou non.",
    version="1.0.0",
    contact={
        "name": "Ghilas",
        "url": "https://github.com/CCI-CDA/Spam-Classifier-Ghilas",
        "email": "ghilas.kebbi@campus-centre.fr",
    }
)


templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class History(BaseModel):
    id : int
    type : str
    content : str

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "id": 5800,
                    "type": "spam",
                    "content": "WINNER! Claim your prize now!",
                }
            ]
        }
    }
class Check(BaseModel):
    is_spam : bool
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_spam" : True
                }
            ]
        }
    }



@app.get("/", response_class=HTMLResponse, summary="Page d'accueil", description="Retourne la page principale de l'application pour vérifier si un message est un spam.")
async def read_item(request: Request):
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"heading": "Votre message est-il un spam ?"})

@app.post("/resultats", response_class=HTMLResponse, summary = "Page de résultat", description="Retourne la page résultat de l'application. Cette page indique si le message est un spam et les messages spam.")
async def read_form(request: Request, message: Annotated[str, Form(...)]):
    """
    Route POST pour vérifier si le message contient un mot spam.
    """
    # Séparer le message en mots
    mots_message = re.findall(r'\b\w+\b', message.lower())  # Extrait les mots du message

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
        cur.execute("INSERT INTO messages (type, content) VALUES('spam', ?)",(message,))
        con.commit()
        con.close()
        return templates.TemplateResponse(
            "resultats.html", 
            context={
                "request": request, 
                "message": message, 
                "result": f"Message contenant des mots spam : {', '.join(mots_trouves)}"
            }
        )
        
    else:
        cur.execute("INSERT INTO messages (type, content) VALUES('ham', ?)",(message,))
        con.commit()
        con.close()
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
@app.post("/check", response_model= Check)
async def check_spam(request: Request, message: Annotated[str, Form(...)]):
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
           return Check(is_spam=True)

    return Check(is_spam=False)



@app.get("/history", response_model=History)
async def message_history():
    """
    Route GET pour récupérer l'historique des messages spams et ham envoyés.
    """
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM messages")
    messages = cur.fetchall()

    # Convertir les objets Row en liste de dictionnaires
    messages_list = [dict(message) for message in messages]

    return JSONResponse(content=messages_list)

# @app.get("/statistiques", response_class=HTMLResponse)
# async def read_item(request: Request):
#     class noeud: 
#         def __init__(self, name:str, number: int):
#             self.name= name
#             self.number = number
#         while i  < 10 :
#             name = 
#     return templates.TemplateResponse(
#         request=request, name="statistiques.html",
#         context={"heading": "Les statistiques"})
