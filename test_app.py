from typing import Literal

from flask import Flask
import pytest
import sqlite3
import os
from werkzeug.security import generate_password_hash
from app import create_app  
from config import TestingConfig



#                                                 FIXTURES


@pytest.fixture
def registered_user(app):
    username = "user1"
    password = generate_password_hash("123password")
    plain_password = "123password"

    connection = sqlite3.connect(app.config["USERS_DB"])
    cursor = connection.cursor()
    cursor.execute("INSERT INTO Users (Username, Password_Hash) VALUES (?, ?)", (username, password))
    connection.commit()
    connection.close()

    return username, plain_password

@pytest.fixture
def app():
    app = create_app(TestingConfig)

    yield app

    if os.path.exists(app.config["USERS_DB"]):
        os.remove(app.config["USERS_DB"])
    if os.path.exists(app.config["STUDENTS_DB"]):
        os.remove(app.config["STUDENTS_DB"])

@pytest.fixture
def client(app):
    return app.test_client()

@pytest.fixture
def student():
    name = "chatGPT"
    age = "16"
    course = "BUSINESS"
    grade = "12"
    phone = "123456789"
    email = ""
    return name, age, grade, course, phone, email


def establish_session(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"



#                                  AUTHENTICATION AND AUTHORIZATION TESTS


def test_register_page(client):
    response = client.get("/register")
    assert response.status_code == 200

def test_post_register(client):
    response = client.post("/register_user", data={
        "username": "testuser",
        "password": "testpassword"
    })
    assert response.status_code == 200


def test_login_page(client):
    response = client.get("/login")
    assert response.status_code == 200

def test_post_login(client, registered_user):
    response = client.post("/login_user", data={
        "username": registered_user[0],
        "password": registered_user[1]
    })
    assert response.json["success"] is True

    with client.session_transaction() as session:
        assert session["user_id"] == 1
        assert session["role"] == "student"


def test_protected_route_requires_login(client):
    response = client.get("/students/")
    assert response.status_code == 302
    assert response.location.endswith("/not_logged_in")

def test_protected_route_allows_logged_in_user(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.get("/students/")
    assert response.status_code == 200


def test_protected_route_requires_role(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "student"
    response = client.get("/students/add_student")
    assert response.status_code == 302
    assert response.location.endswith("/not_authorized")

def test_protected_route_allows_required_role(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
        session["role"] = "admin"
    response = client.get("/students/add_student")
    assert response.status_code == 200


def test_logged_out_user_is_logged_out(client, registered_user):
    with client.session_transaction() as session:
        session["user_id"] = registered_user[0]
        session["role"] = "student"

    response = client.get("/logout")
    assert response.status_code == 302
    assert response.location.endswith("/login")

    with client.session_transaction() as session:
        assert "user_id" not in session
        assert "role" not in session

    response = client.get("/students/")
    assert response.status_code == 302
    assert response.location.endswith("/not_logged_in")



#                                         MAIN APP TESTS


def test_home_page(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.get("/students/")
    assert response.status_code == 200
    

def test_add_student_page(client):
    establish_session(client)
    response = client.get("/students/add_student")
    assert response.status_code == 200

def test_adding_student_in_add_student(client, student):
    establish_session(client)
    response = client.post("/students/add_student", data = {
        "name": student[0],
        "age": student[1],
        "grade": student[2],
        "course": student[3],
        "phone": student[4],
        "email": student[5]
    })
    assert response.json["success"] is True
    response2 = client.get(f"/students/search_student_results?name={student[0]}&grade=&course=")
    assert response2.json["success"] is True

@pytest.mark.parametrize("age", [1, -1, -10])
def test_adding_an_invalid_student(client, student, age):

    establish_session(client)
    response = client.post("/students/add_student", data = {
        "name": student[0],
        "age": age,
        "grade": student[2],
        "course": student[3],
        "phone": student[4],
        "email": student[5]
    })
    assert response.json["success"] is not True


def test_search_student(client):
    establish_session(client)
    response = client.get("/students/search_student_results?name=")
    assert response.status_code == 200


def test_student_route(client):
    with client.session_transaction() as session:
        session["user_id"] = 1
    response = client.get("/students/student")
    assert response.status_code == 404

def test_student_route_for_safe_redirection_after_delete(client):
    establish_session(client)
    response = client.get("/students/student/1?from=/students/view_students")
    assert response.status_code == 302


def test_update_student_page(client):
    establish_session(client)
    response = client.get("/students/update_student/1000000")
    assert response.status_code == 302
    response2 = client.get("/students/update_student/5")
    assert response2.status_code == 302

def test_updating_student(client):
    establish_session(client)
    response = client.post("/students/update_student/")
  

def test_delete_student_that_does_not_exist(client):
    establish_session(client)
    response = client.delete("/students/delete_student/10")
    assert response.status_code == 302
    response2 = client.delete("/students/delete_student/100000")
    assert response2.status_code == 302

