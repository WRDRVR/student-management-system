from flask import Blueprint, request, session, render_template, jsonify, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import auth_user, get_connection


auth = Blueprint("auth", __name__)


@auth.route("/register")
def register():
    return render_template("register.html")

@auth.route("/register_user", methods=["POST"])
def register_user():

    username = request.form.get("username")
    password = request.form.get("password")

    verify = auth_user(username, password, register=True)
    if verify:
        message, field, mfield = verify
        return jsonify({"success": False, "message": message, "field": field, "mfield": mfield})

    password_hash = generate_password_hash(password)

    #------------- success ----------------
    connection = get_connection(current_app.config["USERS_DB"])
    cursor = connection.cursor()
    cursor.execute("""INSERT INTO Users (Username, Password_hash) VALUES (?, ?)""", (username, password_hash))
    connection.commit()
    connection.close()
    return jsonify({"success": True, "message": "Registration successful"})
    

@auth.route("/login")
def log_in():
     return render_template("log-in.html")

@auth.route("/login_user", methods=["POST"])
def log_in_user():

    username = request.form.get("username")
    password = request.form.get("password")

    verify = auth_user(username, password, register=False)
    if verify:
        message, field, mfield = verify
        return jsonify({"success": False, "message": message, "field": field, "mfield": mfield})



    connection = get_connection(current_app.config["USERS_DB"])
    cursor = connection.cursor()
    cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,))
    found_users = cursor.fetchall()
    connection.commit()
    connection.close()

    if len(found_users) == 0:
        return jsonify({"success": "NOT_FOUND", "message": "user not found"})

    user = found_users[0]

    if check_password_hash(user[2], password) == True:
        session["user_id"] = user[0]
        session["role"] = user[3]
        return jsonify({"success": True, "message": "Registration successful"})
    else:
        return jsonify({"success": False, "message": "Incorrect password", "field": "password", "mfield": "password_message"})


@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    session.pop("role", None)
    return redirect(url_for("auth.log_in"))


@auth.route("/not_logged_in")
def not_logged_in():
    return render_template("not_logged_in.html")


@auth.route("/not_authorized")
def not_authorized():
     return render_template("not_authorized.html")