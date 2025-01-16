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
    assert response.json() == {"is_spam": True}

def test_ham():
    # Test avec un message ham
    response = client.post("/check", data={"message": "Hello, how are you today?"})
    assert response.status_code == 200
    assert response.json() == {"is_spam": False}

def test_history():
    # Test pour récupérer l'historique
    response = client.get("/history")
    assert response.status_code == 200

    messages = response.json()
    assert isinstance(messages, list)  

    expected_message = {
        "content": "Had your contract mobile 11 Mnths? Latest Motorola, Nokia etc. all FREE! Double Mins & Text on Orange tariffs. TEXT YES for callback, no to remove from records.",
        "id": 5550,
        "type": "spam"
    }
    assert expected_message in messages  # Vérifiez que l'objet attendu est dans la liste