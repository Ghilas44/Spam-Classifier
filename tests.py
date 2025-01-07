from fastapi.testclient import TestClient
from server import app  # Assure-toi que server.py contient l'application FastAPI
import sqlite3, os
from dotenv import load_dotenv

client = TestClient(app)


def test_home():
    response = client.get("/")
    assert response.status_code == 200
    assert b"Votre message est-il un spam ?" in response.content  # Vérifie un morceau du contenu HTML


def test_spam():
    # Test avec un message spam
    response = client.post("/check", data={"message": "WINNER! Claim your prize now!"})
    assert response.status_code == 200
    assert response.json()["is_spam"] is True

def test_ham():
    # Test avec un message ham
    response = client.post("/check", data={"message": "Hello, how are you today?"})
    assert response.status_code == 200
    assert response.json()["is_spam"] is False
