from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3

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
@app.route('/')
def index():
    try:
        with get_db_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM course_schedule")
            courses = cursor.fetchall()
        return render_template('index.html', courses=courses)
    except sqlite3.Error as e:
        flash(f"Error fetching course data: {e}", "danger")
        return render_template('index.html', courses=[])

# Route to add a new course
@app.route('/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        teacher_name = request.form['teacher_name']
        course_code = request.form['course_code']
        course_title = request.form['course_title']
        day_of_week = request.form['day_of_week']
        class_start_time = request.form['class_start_time']
        class_end_time = request.form['class_end_time']
        room = request.form['room']

        if not (teacher_name and course_code and course_title and day_of_week and class_start_time and class_end_time and room):
            flash("All fields are required.", "warning")
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
                teacher_name = request.form['teacher_name']
                course_code = request.form['course_code']
                course_title = request.form['course_title']
                day_of_week = request.form['day_of_week']
                class_start_time = request.form['class_start_time']
                class_end_time = request.form['class_end_time']
                room = request.form['room']

                if not (teacher_name and course_code and course_title and day_of_week and class_start_time and class_end_time and room):
                    flash("All fields are required.", "warning")
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
