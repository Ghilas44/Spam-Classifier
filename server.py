from fastapi import FastAPI, Request, Form, Depends, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse, HTMLResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from typing import Annotated
import sqlite3, os, re, base64, hashlib
from dotenv import load_dotenv
from pydantic import BaseModel
import random, bcrypt
from fastapi.security import OAuth2PasswordBearer
from fastapi.openapi.utils import get_openapi
import time

'''
L'objectif est d'envoyer un message et de vérifier si il s'agit d'un spam.
Nous récupérons les mots présents dans le message envoyé et vérifions si il est présent dans la 
'''

load_dotenv()

SECRET_KEY = "ma_clé_secrète"  # Clé secrète pour signer et vérifier la session

# Créer un token de session
def create_session_token(username: str):
    session_token = hashlib.sha256((SECRET_KEY).encode('utf-8')).hexdigest()
    return session_token

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

# def custom_openapi():
#     if app.openapi_schema:
#         return app.openapi_schema
#     openapi_schema = get_openapi(
#         title=app.title,
#         version=app.version,
#         description=app.description,
#         routes=app.routes,
#     )
#     openapi_schema["components"] = {
#         "securitySchemes": {
#             "sessionCookie": {
#                 "type": "apiKey",
#                 "in": "cookie",
#                 "name": "session_token",
#             }
#         }
#     }
#     openapi_schema["security"] = [{"sessionCookie": []}]
#     app.openapi_schema = openapi_schema
#     return app.openapi_schema


# app.openapi = custom_openapi
templates = Jinja2Templates(directory="templates")

app.mount("/static", StaticFiles(directory="static"), name="static")


class History(BaseModel):
    id: int
    type: str
    content: str

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
    is_spam: bool
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "is_spam": True
                }
            ]
        }
    }


# Fonction pour récupérer le token de session depuis les cookies
def get_session_token_from_cookie(request: Request):
    # Extraire le token de session depuis le cookie
    token = request.cookies.get("session_token")

    if not token:
        raise HTTPException(status_code=401, detail="Session expirée ou non valide")
    return token

def get_username_from_cookie(request: Request):
    username = request.cookies.get("username")
    return username


# Fonction pour vérifier le token
def verify_session_token(token: str, username: str):
    # Vérifier la validité du token en le recalculant
    recalculated_token = hashlib.sha256((SECRET_KEY).encode('utf-8')).hexdigest()
    return recalculated_token == token


@app.get("/", response_class=HTMLResponse, summary="Page d'accueil", description="Retourne la page principale de l'application pour vérifier si un message est un spam.")
async def read_item(request: Request):
    """
    Cette route vérifie que l'utilisateur est authentifié avant de lui permettre d'accéder à la page d'accueil.
    """

    # Récupérer le token de session depuis le cookie
    session_token = get_session_token_from_cookie(request)

    # Extraire le nom d'utilisateur associé à la session
    username =  get_username_from_cookie(request) # Vous devez récupérer cela de la session ou du cookie, selon votre implémentation

    # Vérifier la validité du token
    if not verify_session_token(session_token, username):
        raise HTTPException(status_code=401, detail="Session invalide")

    # Si le token est valide, afficher la page d'accueil
    return templates.TemplateResponse(
        request=request, name="index.html",
        context={"heading": "Votre message est-il un spam ?"}
    )


@app.post("/resultats", response_class=HTMLResponse, response_model=None, status_code=200, summary = "Page de résultat", description="Retourne la page résultat de l'application. Cette page indique si le message est un spam et les messages spam.")
async def read_form(request: Request, message: Annotated[str, Form(...)]):
    """
    Route POST pour vérifier si le message contient un mot spam.
    """
    # Récupérer le token de session depuis le cookie
    session_token = get_session_token_from_cookie(request)

    # Extraire le nom d'utilisateur associé à la session
    username =  get_username_from_cookie(request) # Vous devez récupérer cela de la session ou du cookie, selon votre implémentation

    # Vérifier la validité du token
    if not verify_session_token(session_token, username):
        raise HTTPException(status_code=401, detail="Session invalide")

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
        cur.execute("INSERT INTO messages (type, content, timestamp) VALUES('spam', ?, current_timestamp)",(message,))
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
        cur.execute("INSERT INTO messages (type, content, timestamp) VALUES('ham', ?, current_timestamp)",(message,))
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
    
# Pour les tests -> retourner un json
@app.post("/check", response_model= Check, summary="Route message spam ou ham", description="")
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

@app.get("/historique")
async def message_history(request: Request, page: int = 1):
    """
    Route GET pour récupérer l'historique des messages spams et ham envoyés.
    """
        # Récupérer le token de session depuis le cookie
    session_token = get_session_token_from_cookie(request)

    # Extraire le nom d'utilisateur associé à la session
    username =  get_username_from_cookie(request) # Vous devez récupérer cela de la session ou du cookie, selon votre implémentation

    # Vérifier la validité du token
    if not verify_session_token(session_token, username):
        raise HTTPException(status_code=401, detail="Session invalide")

    con = get_db_connection()
    cur = con.cursor()
    
    # Calculer l'offset basé sur la page
    offset = (page - 1) * 10
    
    # Récupérer seulement 10 messages à la fois
    cur.execute("SELECT * FROM messages ORDER BY timestamp DESC LIMIT 10 OFFSET ?", (offset,))
    messages = cur.fetchall()

    # Convertir les objets Row en liste de dictionnaires
    messages_list = [dict(message) for message in messages]

    # Vérifier le nombre total de messages pour calculer le nombre total de pages
    cur.execute("SELECT COUNT(*) FROM messages")
    total_messages = cur.fetchone()[0]
    total_pages = (total_messages + 9) // 10  # Calculer le nombre total de pages

    return templates.TemplateResponse(
        "historique.html", 
        context={
            "request": request,  # Ajoutez ici l'objet 'request'
            "messages_list": messages_list,
            "page": page,
            "total_pages": total_pages
        }
    )



@app.get("/login")
async def login(request: Request):
    '''
    Route pour récupérer la page HTML de connexion
    '''
    return templates.TemplateResponse(
        request=request, name="login.html",
        context={"title": "Page de connexion","heading": "Spam Classifier"})

@app.post("/log")
async def login_post(request: Request, username: Annotated[str, Form(...)], password: Annotated[str, Form(...)]):
    """
    Route POST pour traiter la connexion.
    """
    con = get_db_connection()
    cur = con.cursor()
    cur.execute("SELECT * FROM users WHERE username = ?", (username,))
    user = cur.fetchone()

    if user and bcrypt.checkpw(password.encode('utf-8'), user["password_hash"]):
        # Créer un token de session pour l'utilisateur
        session_token = create_session_token(username)

        # Sauvegarder le token de session dans un cookie
        response = RedirectResponse(url="/", status_code=302)
        response.set_cookie(key="username", value=username, httponly=True)
        response.set_cookie(key="session_token", value=session_token, httponly=True)

        return response
    else:
        return templates.TemplateResponse(
            request=request, name="login.html",
            context={"title": "Page de connexion", "heading": "Spam Classifier", "error": "Identifiants incorrects"}
    )

@app.get("/logout")
async def logout(request: Request):
    """
    Route pour déconnecter l'utilisateur en supprimant les cookies de session.
    """
    response = RedirectResponse(url="/login", status_code=302)

    # Expirer les cookies en les réglant à une date dans le passé
    response.delete_cookie("session_token")
    response.delete_cookie("username")

    return response