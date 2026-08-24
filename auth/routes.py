from database import get_connection
from flask import Blueprint, request, session, render_template, jsonify, redirect, url_for
from werkzeug.security import generate_password_hash, check_password_hash
from config import USERS





auth = Blueprint("auth", __name__)


@auth.route("/register")
def register():
       return render_template("register.html")
    

@auth.route("/register_user", methods=["POST"])
def register_user():

        username = request.form.get("username")

        #----------- Verification -----------
        if username == "":
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})
        if len(username) > 15:
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})

        
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("SELECT * FROM Users WHERE Username = ?", (username,))
        existing_usernames = cursor.fetchone()

        if existing_usernames:
            return jsonify({"success": False, "message": "Username already exists, please enter another username", "field": "username", "mfield": "username_message"})


        #------------ password ----------------
        password = request.form.get("password")

        if password == "":
            return jsonify({"success": False, "message": "Please enter a valid password", "field": "password", "mfield": "password_message"})
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters", "field": "password", "mfield": "password_message"})

        password_hash = generate_password_hash(password)


        #------------- success ----------------
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("""INSERT INTO Users (Username, Password_hash) VALUES (?, ?)""", (username, password_hash))
        connection.commit()
        return jsonify({"success": True, "message": "Registration successful"})
    




# ------------------- log-in ----------------------
@auth.route("/login")
def log_in():
     return render_template("log-in.html")

@auth.route("/login_user", methods=["POST"])
def log_in_user():

        username = request.form.get("username")

        #----------- Verification -----------
        if username == "":
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})
        if len(username) > 15:
            return jsonify({"success": False, "message": "Please enter a valid username", "field": "username", "mfield": "username_message"})


        #------------ password ----------------
        password = request.form.get("password")

        if password == "":
            return jsonify({"success": False, "message": "Please enter a valid password", "field": "password", "mfield": "password_message"})
        if len(password) < 6:
            return jsonify({"success": False, "message": "Password must be at least 6 characters", "field": "password", "mfield": "password_message"})


        #------------- success ----------------
        connection = get_connection(USERS)
        cursor = connection.cursor()
        cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,))
        found_users = cursor.fetchall()
 
        #-------------- Check if user exists -------------

        if len(found_users) == 0:
            return jsonify({"success": "NOT_FOUND", "message": "user not found"})
        
        #--------------- Check password ----------------

        user = found_users[0]
        if check_password_hash(user[2], password) == True:
            session["user_id"] = user[0]
            session["role"] = user[3]
            return jsonify({"success": True, "message": "Registration successful"})
        else:
            return jsonify({"success": False, "message": "Incorrect password", "field": "password", "mfield": "password_message"})




# -------------------- log-out --------------------
@auth.route("/logout")
def logout():
    session.pop("user_id", None)
    return redirect(url_for("auth.log_in"))





# ------------------ not-logged-in ---------------------
@auth.route("/not_logged_in")
def not_logged_in():
    return render_template("not_logged_in.html")

@auth.route("/not_authorized")
def not_authorized():
     return render_template("not_authorized.html")