import sqlite3
from flask import Blueprint, request, render_template, jsonify, current_app, redirect, url_for
from helpers import validate_student, login_required, role_required, with_database



students = Blueprint("students", __name__, url_prefix="/students")


@students.route("/page_not_found")
def page_not_found():
    return render_template("page_not_found.html")


@students.route("/something_went_wrong")
def something_went_wrong():
    return render_template("something_went_wrong.html")



@students.route("/")
@login_required
def home():
   return render_template("HOME.html")


@students.route("/add_student")
#@login_required
#@role_required("admin" or "teacher")
def add_student():
    return render_template("add_student.html")


@students.route("/add_student", methods=["POST"])
#@login_required
#@role_required("admin" or "teacher")
def add_student_post():    
    name = request.form["name"].strip()
    age = request.form["age"].strip()
    grade = request.form["grade"] 
    course = request.form["course"]
    phone = request.form["phone"]
    email = request.form["email"]
    student_id = None

    valid = validate_student(name, age, grade, course, phone, student_id, email)
    if valid:
        field, error = valid
        return jsonify({ "success": False, "field": field, "message": error })
    
    #SQL
    def insert_student(cursor):
        cursor.execute(
        """ INSERT INTO Students (Name, Age, Grade, Course, Phone, Email) VALUES (?, ?, ?, ?, ?, ?) """,
        (name, age, grade, course, phone, email)
        )
    success, result = with_database("STUDENTS_DB", insert_student, commit=True)
    if not success:
        print(result)
        return redirect(url_for("students.something_went_wrong"))

    return jsonify({"success": True, "message": "Student added successfully"})



@students.route("/view_students")
@login_required
def view_students():
    return render_template("view_students.html")

@students.route("/view_students_results")
@login_required
def view_students_results():
    #SQL
    def fetch_students(cursor):
        cursor.execute(" SELECT * FROM Students ORDER BY ID ")
        return cursor.fetchall()
    success, result = with_database("STUDENTS_DB", fetch_students)
    if not success:
        print(result)
        return redirect(url_for('students.something_went_wrong'))
    
    students_list = result
    count = len(students_list)

    return jsonify({"students": students_list, "count": count})



@students.route("/search_student")
@login_required
def search_student_search():
    return render_template("search_student.html", students=[], count=0)
    
@students.route("/search_student_results")
@login_required
def search_student_results():
    name = request.args.get("name","").strip()
    grade = request.args.get("grade","").strip()
    course = request.args.get("course","").strip()
        
    query = "SELECT * FROM Students WHERE 1=1"
    params = []

    if name:
        query += " AND Name LIKE ?"
        params.append(f"%{name}%")
    
    if grade:
        query += " AND Grade LIKE ?"
        params.append(f"%{grade}%")

    if course:
        query += " AND Course LIKE ?"
        params.append(f"%{course}%")

    def search(cursor):
        cursor.execute(query, params)
        return cursor.fetchall()
    
    success, result = with_database("STUDENTS_DB", search)

    if not success:
        print(result)
        return redirect(url_for("students.something_went_wrong"))
    
    students_list = result
    return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
    


@students.route("/student/<int:student_id>", methods=["GET"])
@login_required
def student_details(student_id):

    source = request.args.get("from")
    if source is None:
        source = "/students/"
    elif source == "/view_students":
        source = "/view_students"
    elif source.startswith("/search_student_results"):
        source = source
    else:
        redirect(url_for("students.home"))

    if student_id > 1000 or student_id < 1:
        return redirect(url_for("students.page_not_found"))
    
    # SQL
    def select_student(cursor):
        cursor.execute(" SELECT * FROM Students WHERE ID = ?", (student_id,))
        return cursor.fetchone()
    success, result = with_database("STUDENTS_DB", select_student)
    if not success:
        print(result)
        return redirect(url_for("students.something_went_wrong"))
    student = result

    if student:
        return render_template("student_details.html", student=student, source=source)
    else:
        return redirect(url_for("students.page_not_found"))
        


@students.route("/update_student/<int:student_id>", methods=["GET", "POST"])
@login_required
@role_required("admin" or "teacher")
def update_student_GET_and_POST(student_id):
    if request.method == "GET":
        if student_id > 1000 or student_id < 1:
            return redirect(url_for("students.page_not_found"))

        # SQL
        def get_students(cursor):
            cursor.execute("SELECT * FROM Students WHERE ID = ?", (student_id,))
            return cursor.fetchone()
        success, result = with_database("STUDENTS_DB", get_students)
        if not success:
            print(result)
            return redirect(url_for("students.something_went_wrong"))
        
        selected_student = result
        if selected_student:
            return render_template("update_student.html", student=selected_student)
        else:
            return redirect(url_for("students.page_not_found"))
  
    elif request.method == "POST":
        if student_id > 1000 or student_id < 1:
            return redirect(url_for("students.page_not_found"))
        
        #CHECK IF STUDENT EXISTS
        def check_student(cursor):
            cursor.execute("SELECT * FROM Students WHERE ID = ?", (student_id))
            return cursor.fetchone()
        success, result = with_database("STUDENTS_DB", check_student)
        if not success:
            print(result)
            return redirect(url_for("students.something_went_wrong"))
        student = result
        if not student:
            return redirect(url_for("students.page_not_found"))

        name = request.form["name"].strip()
        age = request.form["age"].strip()
        grade = request.form["grade"].strip() 
        course = request.form["course"].strip()
        phone = request.form["phone"]
        email = request.form.get("email", "")  

        # Validation
        result = validate_student(name, age, grade, course, phone, student_id, email)
        if result:
            field, error = result
            return jsonify({ "success": False, "field": field, "message": error})

        # SQL
        def update_student(cursor):
            cursor.execute("UPDATE Students SET Name = ?, Age = ?, Grade = ?, Course = ?, Phone = ?, Email = ? WHERE ID = ?", 
            (name, age, grade, course, phone, email, student_id))
        success, result = with_database("STUDENT_DB", update_student, commit=True)
        if not success:
            print(result)
            return redirect(url_for("students.something_went_wrong"))
        
        return jsonify({ "success": True, "message": "Student has been updated" })



@students.route("/delete_student/<int:student_id>", methods=["DELETE"])
@login_required
@role_required("admin")
def delete_student_GET_and_POST(student_id):

    if student_id > 1000 or student_id < 1:
        return redirect(url_for("students.page_not_found"))
    
    # CHECK STUDENT ACTUALLY EXISTS
    def check_student(cursor):
        cursor.execute("SELECT * FROM Students WHERE ID = ?", (student_id))
        return cursor.fetchone()
    success, result = with_database("STUDENTS_DB", check_student)
    if not success:
        print(result)
        return redirect(url_for("students.something_went_wrong"))
    student = result
    if not student:
        return redirect(url_for("students.page_not_found"))
        

    # CONTINUE WITH DELETION
    def delete_student(cursor):
        cursor.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
    with_database("STUDENTS_DB", delete_student, commit=True)
    
    return jsonify({ "message": "Student has been deleted", "studentId":  student_id })


