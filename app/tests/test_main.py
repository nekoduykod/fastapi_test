from fastapi.testclient import TestClient

from app.main import app


client = TestClient(app)


def test_home():
   ### I did not do tests
    assert response.status_code == 200
    response = client.get("/static/css/styles.css")
    assert response.status_code == 200

def test_login():
   response = client.post("/login", data={"username": "testuser", "password": "testpass"})
   assert response.status_code == 200

def test_register():
   response = client.post("/register", data={"username": "newuser", "password": "newpass"})
   assert response.status_code == 200