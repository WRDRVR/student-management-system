from flask import Blueprint, request, render_template, jsonify
from database import get_connection
from config import STUDENTS
from helpers import validate_student, login_required, role_required




students = Blueprint("students", __name__, url_prefix="/students")



@students.route("/")
@login_required
def home():
   message = 'Weclome!'
   return render_template("HOME.html", message=message)



@students.route("/add_student")
@login_required
@role_required("admin" or "teacher")
def add_student():
    return render_template("add_student.html")



@students.route("/add_student", methods=["POST"])
@login_required
@role_required("admin" or "teacher")
def add_student_post():
    # Request Input
        name = request.form["name"].strip()
        age = request.form["age"].strip()
        grade = request.form["grade"] 
        course = request.form["course"]
        phone = request.form["phone"]
        email = request.form["email"]  
        student_id = None

    # Validation
        result = validate_student(name, age, grade, course, phone, student_id)
        if result:
            field, error = result
            return jsonify({ "success": False, "field": field, "message": error })
    
    # SQL
        connection = get_connection(STUDENTS)
        cursor = connection.cursor()
        cursor.execute(
          """ INSERT INTO Students (Name, Age, Grade, Course, Phone, Email) VALUES (?, ?, ?, ?, ?, ?) """,
          (name, age, grade, course, phone, email)
        )
        connection.commit()
    
        return jsonify({
            "success": True,
            "message": "Student added successfully"
        })




@students.route("/view_students")
@login_required
def view_students():
    return render_template("view_students.html")

@students.route("/view_students_results")
@login_required
def view_students_results():

    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students ORDER BY ID ")
    students_list = cursor.fetchall()
    count = len(students_list)
    
    return jsonify({"students": students_list, "count": count})










@students.route("/search_student")
@login_required
def search_student_search():
        return render_template("search_student.html", students=[], count=0)
    
@students.route("/search_student_results")
@login_required
def search_student_results():
        name = request.args["name"].strip()
        grade = request.args["grade"]
        course = request.args["course"]
        
        if grade == "" and course == "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? ORDER BY ID """, (name,))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif grade == "" and course != "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"
            course = f"{course}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Course LIKE ? ORDER BY ID""", (name, course))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
        
        elif course == "" and grade != "":

            connection = get_connection(STUDENTS)
            cursor = connection.cursor()

            name = f"%{name}%"
            grade = f"{grade}"

            cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Grade LIKE ? ORDER BY ID""", (name, grade))
            students_list = cursor.fetchall()
            return jsonify({ "success": True, "students": students_list, "count": len(students_list) })







        
    # SQL
        connection = get_connection(STUDENTS)
        cursor = connection.cursor()
        
        name = f"%{name}%"
        grade = f"{grade}"
        course = f"{course}"

        cursor.execute("""SELECT * FROM Students WHERE Name LIKE ? AND Grade LIKE ? AND Course LIKE ? ORDER BY Name""", 
                       (name, grade, course))
        students_list = cursor.fetchall()
        return jsonify({ "success": True, "students": students_list, "count": len(students_list) })
    







@students.route("/student/<int:student_id>", methods=["GET"])
@login_required
def student_details(student_id):

    source = request.args.get("from")

    
    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute(" SELECT * FROM Students WHERE ID = ?", (student_id,))
    student = cursor.fetchone()
    
    return render_template("student_details.html", student=student, source=source)








@students.route("/update_student/<int:student_id>", methods=["GET", "POST"])
@login_required
@role_required("admin" or "teacher")
def update_student_GET_and_POST(student_id):

    if request.method == "GET":
       connection = get_connection(STUDENTS)
       cursor = connection.cursor()

       cursor.execute("SELECT * FROM Students WHERE ID = ?", (student_id,))
       selected_student =  cursor.fetchone()

       return render_template("update_student.html", student=selected_student)
    
    elif request.method == "POST":
       name = request.form["name"].strip()
       age = request.form["age"].strip()
       grade = request.form["grade"].strip() 
       course = request.form["course"].strip()
       phone = request.form["phone"]
       email = request.form["email"]    

    # Validation
       result = validate_student(name, age, grade, course, phone, student_id)
       if result:
            field, error = result
            return jsonify({ "success": False, "field": field, "message": error})

    # SQL
       connection = get_connection(STUDENTS)
       cursor = connection.cursor()

       cursor.execute("UPDATE Students SET Name = ?, Age = ?, Grade = ?, Course = ?, Phone = ?, Email = ? WHERE ID = ?", 
                      (name, age, grade, course, phone, email, student_id))
    
       connection.commit()
       return jsonify({ "success": True, "message": "Student has been updated" })









@students.route("/delete_student/<int:student_id>", methods=["DELETE"])
@login_required
@role_required("admin" or "teacher")
def delete_student_GET_and_POST(student_id):

    connection = get_connection(STUDENTS)
    cursor = connection.cursor()

    cursor.execute("DELETE FROM Students WHERE ID = ?", (student_id,))
    connection.commit()

    return jsonify({ "message": "Student has been deleted", "studentId":  student_id })



