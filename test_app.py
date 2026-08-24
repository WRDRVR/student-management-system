import pytest
from app import create_app  
from config import test_config


@pytest.fixture
def client():
    app = create_app(test_config)
    return app.test_client()



def test_login_page(client):
    response = client.get("/login")

    assert response.status_code == 200

def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_post_register(client):
    response = client.post("/register_user")
    assert response.status_code == 200