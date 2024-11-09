from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# SQLite Database connection function with context manager
def get_db_connection():
    try:
        conn = sqlite3.connect('university_schedule.db')  # Connects to the SQLite database file
        conn.row_factory = sqlite3.Row  # Allows rows to behave like dictionaries
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        return None

# Route to display the course schedule
@app.route('/', methods=['GET', 'POST'])
def index():
    try:
        # Retrieve filter parameters from the request
        teacher_name = request.args.get('teacher_name', '')
        course_code = request.args.get('course_code', '')
        day_of_week = request.args.get('day_of_week', '')

        # Build the query dynamically based on filters
        query = "SELECT * FROM course_schedule WHERE 1=1"
        params = []

        if teacher_name:
            query += " AND teacher_name LIKE ?"
            params.append(f"%{teacher_name}%")
        if course_code:
            query += " AND course_code LIKE ?"
            params.append(f"%{course_code}%")
        if day_of_week:
            query += " AND day_of_week LIKE ?"
            params.append(f"%{day_of_week}%")

        # Fetch the courses from the database based on the filter
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, tuple(params))
            courses = cursor.fetchall()

        return render_template('index.html', courses=courses)

    except sqlite3.Error as e:
        flash(f"Error fetching course data: {e}", "danger")
        return render_template('index.html', courses=[])

# Route to add a new course
@app.route('/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        # Get form data
        teacher_name = request.form['teacher_name']
        course_code = request.form['course_code']
        course_title = request.form['course_title']
        day_of_week = request.form['day_of_week']
        class_start_time = request.form['class_start_time']
        class_end_time = request.form['class_end_time']
        room = request.form['room']

        # Validate form fields
        if not all([teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room]):
            flash("All fields are required.", "warning")
            return render_template('add_course.html')

        # Validate start time and end time
        try:
            start_time = datetime.strptime(class_start_time, '%H:%M')
            end_time = datetime.strptime(class_end_time, '%H:%M')
            if start_time >= end_time:
                flash("End time must be after start time.", "warning")
                return render_template('add_course.html')
        except ValueError:
            flash("Invalid time format. Please use HH:MM format.", "warning")
            return render_template('add_course.html')

        try:
            with get_db_connection() as conn:
                cursor = conn.cursor()
                cursor.execute(""" 
                    INSERT INTO course_schedule 
                    (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room) 
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room))
                conn.commit()
                flash("Course added successfully.", "success")
            return redirect(url_for('index'))
        except sqlite3.Error as e:
            flash(f"Error adding course: {e}", "danger")
    
    return render_template('add_course.html')

# Route to edit a course
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM course_schedule WHERE id = ?", (id,))
            course = cursor.fetchone()

            if not course:
                flash("Course not found.", "danger")
                return redirect(url_for('index'))

            if request.method == 'POST':
                # Get updated form data
                teacher_name = request.form['teacher_name']
                course_code = request.form['course_code']
                course_title = request.form['course_title']
                day_of_week = request.form['day_of_week']
                class_start_time = request.form['class_start_time']
                class_end_time = request.form['class_end_time']
                room = request.form['room']

                # Validate form fields
                if not all([teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room]):
                    flash("All fields are required.", "warning")
                    return render_template('edit_course.html', course=course)

                # Validate start time and end time
                try:
                    start_time = datetime.strptime(class_start_time, '%H:%M')
                    end_time = datetime.strptime(class_end_time, '%H:%M')
                    if start_time >= end_time:
                        flash("End time must be after start time.", "warning")
                        return render_template('edit_course.html', course=course)
                except ValueError:
                    flash("Invalid time format. Please use HH:MM format.", "warning")
                    return render_template('edit_course.html', course=course)

                cursor.execute(""" 
                    UPDATE course_schedule 
                    SET teacher_name = ?, course_code = ?, course_title = ?, day_of_week = ?, 
                        class_start_time = ?, class_end_time = ?, room = ? 
                    WHERE id = ?""",
                    (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room, id))
                conn.commit()
                flash("Course updated successfully.", "success")
                return redirect(url_for('index'))

            return render_template('edit_course.html', course=course)
    except sqlite3.Error as e:
        flash(f"Error editing course: {e}", "danger")
        return redirect(url_for('index'))

# Route to delete a course
@app.route('/delete/<int:id>')
def delete_course(id):
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM course_schedule WHERE id = ?", (id,))
            conn.commit()
            flash("Course deleted successfully.", "success")
    except sqlite3.Error as e:
        flash(f"Error deleting course: {e}", "danger")
    
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
