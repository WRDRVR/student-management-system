import secrets, hashlib
import smtplib
from datetime import datetime, timedelta, timezone
from flask import Blueprint, request, session, render_template, jsonify, redirect, url_for, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import auth_user, get_connection, with_database, send_verification_email, send_verification_sms, auth_email, auth_phone

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
    

    #--------------------------------- success -----------------------------------
    def insert_user(cursor):
        cursor.execute("""INSERT INTO Users (Username, Password_hash) VALUES (?, ?)""", (username, password_hash))
        return cursor.lastrowid
    success, result = with_database("USERS_DB", insert_user, commit=True)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    user_id = result
    session["register_user_id"] = user_id
    
    return jsonify({"success": True, "message": "Registration Finshed."})
    

# EMAIL VERIFICATION

@auth.route("/auth-email", methods=["GET", "POST"])
def authenticate_email():
    if request.method == "GET":
        return render_template("auth_email.html")
    elif request.method == "POST":
        user_id = session.get("register_user_id")
        email = request.form.get("email")
    
        verify = auth_email(email)
        if verify:
            message, field, mfield = verify
            return jsonify({"success": False, "message": message, "field": field, "mfield": mfield})
        
        def insert_email(cursor):
            cursor.execute("""UPDATE Users SET Email = ?""", (email,))
        success, result = with_database("USERS_DB", insert_email, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")


        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        expires_at = datetime.now() + timedelta(minutes=15)
        resend_available_at = datetime.now() + timedelta(seconds=60)


        def insert_token(cursor):
            cursor.execute("""INSERT INTO EmailVerification (UserID, TokenHash, ExpiresAt, ResendAvailableAt) VALUES (?, ?, ?, ?)""", 
            (user_id, token_hash, expires_at, resend_available_at))
        success, result = with_database("EMAIL_VER", insert_token, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")
        #send_verification_email(email, token)

        return jsonify({"success": True, "message": "Token sent to your email, please verify your email"})

@auth.route("/resend-token")
def resend_token():
    user_id = request.args.get("user_id")

    def get_timestamp(cursor):
        cursor.execute("SELECT ResendAvailableAt FROM EmailVerification WHERE UserID = ?", (user_id,))
        return cursor.fetchone()
    success, result = with_database("EMAIL_VER", get_timestamp)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    time = result[0]
    if datetime.now() < datetime.fromisoformat(time):
        return jsonify({ "success": False, "message": "You cannot resend code right now"})

    new_token = secrets.token_urlsafe(32)
    new_token_hash = hashlib.sha256(new_token.encode()).hexdigest()
    new_expires_at = datetime.now() + timedelta(minutes=15)
    resend_available_at = datetime.now() + timedelta(seconds=60)



    def replace_verification_token(cursor):
        cursor.execute("DELETE FROM EmailVerification WHERE UserID = ?", (user_id))
        cursor.execute("""INSERT INTO EmailVerification (UserID, TokenHash, ExpiresAt, ResendAvailableAt) VALUES (?, ?, ?, ?)""",
         (user_id, new_token_hash, new_expires_at, resend_available_at))
    success, result = with_database("EMAIL_VER", replace_verification_token, commit=True)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    
    def get_email(cursor):
        cursor.execute("SELECT * FROM Users WHERE UserID = ?", (user_id))
        return cursor.fetchone()
    success, result = with_database("USERS_DB", get_email)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    email = result[3]

    #send_verification_email(email, new_token)

    return jsonify({"success": True, "message": "Token has been resent"})

@auth.route("/verify-email")
def verify_email():
    token = request.args.get("token")
    user_id = session.get("register_user_id")

    if token == "":
        return render_template("page_not_found.html", 404)
    
    def record_attempt(cursor):
        cursor.execute("UPDATE EmailVerification SET Attempts = Attempts + 1 WHERE UserID = ?", (user_id,))
    success, result = with_database("EMAIL_VER", record_attempt, commit=True)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    
    token_hash = hashlib.sha256(token.encode()).hexdigest()
    def verify_token(cursor):
        cursor.execute("SELECT * FROM EmailVerification WHERE UserID = ?", (user_id,))
        cursor.fetchone()
    success, result = with_database("EMAIL_VER", verify_token)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    user = result

    if user[2] != token_hash:
        if user[4] >= 5:
            def delete_user(cursor):
                cursor.execute("DELETE FROM Users WHERE ID = ?", (user_id,))
            success, result = with_database("USERS_DB", delete_user, commit=True)
            if not success:
                return render_template("something_went_wrong.html")
            return render_template("register.html", message="You have attempted to verify your email too many times.")
        return render_template("auth_email.html", message="You submitted an Invalid token")
    

    if datetime.now() >= datetime.fromisoformat(user[3]):
        return render_template("auth_email.html", message="Your token has expired")
    else:
        def update_email_verfication(cursor):
            cursor.execute("UPDATE Users SET EmailVerified = ? WHERE ID = ?", (1, user[1]))
        success, result = with_database("EMAIL_VER", update_email_verfication, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")

        def delete_verification_record(cursor):
            cursor.execute("DELETE FROM EmailVerification WHERE ID = ?", (user[0],))
        success, result = with_database("EMAIL_VER", delete_verification_record, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")
        return redirect(url_for("auth-phone"))


# PHONE VERFICATION

@auth.route("/auth-phone", methods=["GET", "POST"])
def authenticate_phone():
    if request.method == "GET":
        return render_template("auth_phone.html")
    elif request.method == "POST":
        phone = request.form.get("phone")
        user_id = session.get("register_user_id")

        verify = auth_phone(phone)
        if verify:
            message, field, mfield = verify
            return jsonify({"success": False, "message": message, "field": field, "mfield": mfield})
        
        def insert_phone(cursor):
            cursor.execute("""UPDATE Users SET Phone = ?""", (phone,))
        success, result = with_database("USERS_DB", insert_phone, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")

        code = secrets.randbelow(900000) + 100000
        code_hash = hashlib.sha256(str(code).encode()).hexdigest()
        expires_at = datetime.now() + timedelta(minutes=15)
        resend_available_at = datetime.now() + timedelta(seconds=60)

        def insert_code(cursor):
            cursor.execute("""INSERT INTO PhoneVerification (UserID, CodeHash, ExpiresAt, ResendAvailableAt) VALUES (?, ?, ?, ?)""", 
               (user_id, code_hash, expires_at, resend_available_at))
        success, result = with_database("PHONE_VER", insert_code, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")
        send_verification_sms(phone, code)
        return jsonify({"success": True, "message": "phone was recieved"})
    

@auth.route("/resend-code")
def resend_code():
    user_id = session.get("register_user_id")

    def get_timestamp(cursor):
        cursor.execute("SELECT ResendAvailableAt FROM PhoneVerification WHERE UserID = ?", (user_id,))
        return cursor.fetchone()
    success, result = with_database("PHONE_VER", get_timestamp)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    time = result[0]
    if datetime.now() < datetime.fromisoformat(time):
        return jsonify({ "success": False, "message": "You cannot resend code right now"})

    code = secrets.randbelow(900000) + 100000
    code_hash = hashlib.sha256(str(code).encode()).hexdigest()
    expires_at = datetime.now() + timedelta(minutes=15)
    resend_available_at = datetime.now() + timedelta(seconds=60)

    def replace_verification_token(cursor):
        cursor.execute("DELETE FROM PhoneVerification WHERE UserID = ?", (user_id,))
        cursor.execute("""INSERT INTO PhoneVerification (UserID, CodeHash, ExpiresAt, ResendAvailableAt) VALUES (?, ?, ?, ?)""",
         (user_id, code_hash, expires_at, resend_available_at))
    success, result = with_database("PHONE_VER", replace_verification_token, commit=True)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    
    def get_phone(cursor):
        cursor.execute("SELECT * FROM Users WHERE ID = ?", (user_id,))
        return cursor.fetchone()
    success, result = with_database("USERS_DB", get_phone)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    phone = result[5]
    send_verification_sms(phone, code)

    return jsonify({"success": True, "cooldown": 60})


@auth.route("/verify-phone", methods=["GET", "POST"])
def verify_phone():
    if request.method == "GET":
       return render_template("verify_phone.html")
    elif request.method == "POST":
        user_id = session.get("register_user_id")
        code = request.form.get("code")
        code_hash = hashlib.sha256(code.encode()).hexdigest()

        def record_attempt(cursor):
            cursor.execute("UPDATE PhoneVerification SET Attempts = Attempts + 1 WHERE UserID = ?", (user_id,))
        success, result = with_database("PHONE_VER", record_attempt, commit=True)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")


        def verify_code(cursor):
            cursor.execute("SELECT * FROM PhoneVerification WHERE UserID = ?", (user_id,))
            return cursor.fetchone()
        success, result = with_database("PHONE_VER", verify_code)
        if not success:
            print(result)
            return render_template("something_went_wrong.html")
        user = result

        if user[2] != code_hash:
            if user[4] >= 5:
                def delete_user(cursor):
                    cursor.execute("DELETE FROM Users WHERE ID = ?", (user_id,))
                success, result = with_database("USERS_DB", delete_user, commit=True)
                if not success: 
                    print(result)  
                    return render_template("something_went_wrong.html")
                def delete_email(cursor):
                    cursor.execute("DELETE FROM EmailVerification WHERE ID = ?", (user_id,))
                success, result = with_database("EMAIL_VER", delete_email, commit=True)
                if not success:
                    print(result)
                    return render_template("something_went_wrong.html")
                def delete_phone(cursor):
                    cursor.execute("DELETE FROM PhoneVerification WHERE ID = ?", (user_id))
                    success, result = with_database("PHONE_VER", delete_phone, commit=True)
                    if not success:
                        print(result)
                        return render_template("something_went_wrong.html")        
                return jsonify({"success": "Forbidden", "message": "You have attempted to verify your phone too many times"})
            return jsonify({"success": False, "message": "Sorry, Your code is incorrect"})
        

        if datetime.now() >= datetime.fromisoformat(user[3]):
            return jsonify({"success": False, "message": "Your code has expired"})
        else:
            def update_phone_verfication(cursor):
                cursor.execute("UPDATE Users SET PhoneVerified = ? WHERE ID = ?", (1, user[1]))
            success, result = with_database("USERS_DB", update_phone_verfication, commit=True)
            if not success:
                print(result)
                return render_template("something_went_wrong.html")

            def delete_verification_record(cursor):
                cursor.execute("DELETE FROM PhoneVerification WHERE ID = ?", (user[0],))
            success, result = with_database("PHONE_VER", delete_verification_record, commit=True)
            if not success:
                print(result)
                return render_template("something_went_wrong.html")
            return jsonify({"success": True, "message": "verification successfull"})





@auth.route("/login")
def log_in():
     return render_template("log-in.html")

@auth.route("/login_user", methods=["POST"])
def log_in_user():

    username = request.form.get("username")
    password = request.form.get("password")

    verify = auth_user(username, password)
    if verify:
        message, field, mfield = verify
        return jsonify({"success": False, "message": message, "field": field, "mfield": mfield})
    
    def find_user(cursor):
        cursor.execute("""SELECT * FROM Users WHERE Username = ?""", (username,))
        return cursor.fetchall()
    success, result = with_database("USERS_DB", find_user)
    if not success:
        print(result)
        return render_template("something_went_wrong.html")
    found_users = result

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