from flask import Flask, render_template, request, redirect, session, url_for, flash, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'your_secret_key'  # Required for flash messages

# SQLite Database connection function with context manager
def get_db_connection():
    """Establishes and returns a connection to the SQLite database."""
    try:
        conn = sqlite3.connect('university_schedule.db')  # Connect to the database file
        conn.row_factory = sqlite3.Row  # Allows rows to behave like dictionaries
        return conn
    except sqlite3.Error as e:
        print(f"Database connection error: {e}")
        flash(f"Database error: {e}", "danger")
        return None


# Helper function to validate course times
def validate_times(class_start_time, class_end_time):
    """Validates start time and end time of the course."""
    try:
        start_time = datetime.strptime(class_start_time, '%H:%M')
        end_time = datetime.strptime(class_end_time, '%H:%M')
        if start_time >= end_time:
            return "End time must be after start time."
        return None
    except ValueError:
        return "Invalid time format. Please use HH:MM format."


# Helper function to check for conflicts in scheduling.
def check_schedule_conflict(conn, teacher_name, day_of_week, start_time, end_time, room):
    """Helper function to check for scheduling conflicts."""
    cursor = conn.cursor()
    cursor.execute("""
        SELECT * FROM course_schedule WHERE 
        (teacher_name = ? AND day_of_week = ? AND 
        ((class_start_time < ? AND class_end_time > ?) OR 
         (class_start_time < ? AND class_end_time > ?)))
        OR (room = ? AND day_of_week = ? AND
        ((class_start_time < ? AND class_end_time > ?) OR 
         (class_start_time < ? AND class_end_time > ?)))
    """, (teacher_name, day_of_week, start_time, start_time, end_time, end_time,
          room, day_of_week, start_time, start_time, end_time, end_time))
    return cursor.fetchall()


@app.route('/', methods=['GET'])
def index():
    with get_db_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM course_schedule")
        courses = cursor.fetchall()
        return render_template('base.html', courses=courses)


# Route to display the course schedule
@app.route('/courses', methods=['GET', 'POST'])
def course_list():
    try:
        # Retrieve filter parameters from the request
        teacher_name = request.args.get('teacher_name', '').strip()
        course_code = request.args.get('course_code', '').strip()
        day_of_week = request.args.get('day_of_week', '').strip()

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
            if conn:
                cursor = conn.cursor()
                cursor.execute(query, tuple(params))
                courses = cursor.fetchall()
            else:
                raise sqlite3.Error("Failed to connect to the database")

        # If no courses are found, display a message
        if not courses:
            flash("No courses found with the selected filters.", "info")

        return render_template('index.html', courses=courses)

    except sqlite3.Error as e:
        flash(f"Error fetching course data: {e}", "danger")
        return render_template('index.html', courses=[])


# Route For Course Selected
@app.route('/course_schedule', methods=['GET'])
def course_schedule():
    try:
        # Fetch selected courses from the session (or database if saved there)
        selected_courses = session.get('selected_courses', [])

        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                if selected_courses:
                    # Fetch the selected courses from the database
                    query = "SELECT * FROM course_schedule WHERE id IN ({})".format(
                        ','.join('?' for _ in selected_courses)
                    )
                    cursor.execute(query, tuple(selected_courses))
                    courses = cursor.fetchall()
                else:
                    courses = []  # No courses selected

        if not courses:
            flash("No courses are currently selected.", "info")

        return render_template('course_schedule.html', courses=courses)

    except sqlite3.Error as e:
        flash(f"Error fetching selected courses: {e}", "danger")
        return render_template('course_schedule.html', courses=[])


# Route to select courses
@app.route('/select_courses', methods=['GET', 'POST'])
def select_courses():
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM course_schedule")
                courses = cursor.fetchall()
            else:
                raise sqlite3.Error("Failed to connect to the database")

        if request.method == 'POST':
            selected_courses = request.form.getlist('courses')

            if len(selected_courses) > 6:
                flash("You can only select up to 6 courses.", "warning")
                return render_template('select_courses.html', courses=courses, selected_courses=selected_courses)

            # Save selected courses to the session
            session['selected_courses'] = [int(course_id) for course_id in selected_courses]

            flash("Courses selected successfully.", "success")
            return redirect(url_for('course_schedule'))

        return render_template('select_courses.html', courses=courses, selected_courses=[])

    except sqlite3.Error as e:
        flash(f"Error fetching courses: {e}", "danger")
        return render_template('select_courses.html', courses=[])


# Route to add a new course
@app.route('/add', methods=['GET', 'POST'])
def add_course():
    if request.method == 'POST':
        try:
            # Get form data
            teacher_name = request.form['teacher_name'].strip()
            course_code = request.form['course_code'].strip()
            course_title = request.form['course_title'].strip()
            day_of_week = request.form['day_of_week'].strip()
            class_start_time = request.form['class_start_time'].strip()
            class_end_time = request.form['class_end_time'].strip()
            room = request.form['room'].strip()

            # Validate form fields
            if not all([teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room]):
                flash("All fields are required.", "warning")
                return render_template('add_course.html')

            # Validate start time and end time
            time_validation_message = validate_times(class_start_time, class_end_time)
            if time_validation_message:
                flash(time_validation_message, "warning")
                return render_template('add_course.html')

            # Check for scheduling conflicts
            with get_db_connection() as conn:
                if conn:
                    cursor = conn.cursor()
                    cursor.execute(""" 
                        SELECT * FROM course_schedule 
                        WHERE (teacher_name = ? AND day_of_week = ? AND 
                            ((class_start_time < ? AND class_end_time > ?) OR 
                             (class_start_time < ? AND class_end_time > ?)))
                        OR (room = ? AND day_of_week = ? AND
                            ((class_start_time < ? AND class_end_time > ?) OR 
                             (class_start_time < ? AND class_end_time > ?)))
                    """, (teacher_name, day_of_week, class_start_time, class_start_time, class_end_time, class_end_time,
                          room, day_of_week, class_start_time, class_start_time, class_end_time, class_end_time))
                    existing_courses = cursor.fetchall()

                    if existing_courses:
                        flash("Course conflicts with an existing course.", "danger")
                        return render_template('add_course.html')

                    # Insert new course
                    cursor.execute(""" 
                        INSERT INTO course_schedule 
                        (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room) 
                        VALUES (?, ?, ?, ?, ?, ?, ?)""", 
                        (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room))
                    conn.commit()

                    flash("Course added successfully.", "success")
                    return redirect(url_for('index'))

                else:
                    raise sqlite3.Error("Failed to connect to the database")

        except sqlite3.Error as e:
            flash(f"Error saving course: {e}", "danger")
            return render_template('add_course.html')

    # If it's a GET request, render the add course form
    return render_template('add_course.html')


# Route to edit a course
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_course(id):
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM course_schedule WHERE id = ?", (id,))
                course = cursor.fetchone()

                if request.method == 'POST':
                    teacher_name = request.form['teacher_name']
                    course_code = request.form['course_code']
                    course_title = request.form['course_title']
                    day_of_week = request.form['day_of_week']
                    class_start_time = request.form['class_start_time']
                    class_end_time = request.form['class_end_time']
                    room = request.form['room']

                    cursor.execute("""
                        UPDATE course_schedule
                        SET teacher_name = ?, course_code = ?, course_title = ?, 
                            day_of_week = ?, class_start_time = ?, class_end_time = ?, room = ?
                        WHERE id = ?""", (teacher_name, course_code, course_title, day_of_week,
                                          class_start_time, class_end_time, room, id))
                    conn.commit()

                    flash("Course updated successfully.", "success")
                    return redirect(url_for('course_schedule'))
                else:
                    return render_template('edit_course.html', course=course)
            else:
                raise sqlite3.Error("Failed to connect to the database")

    except sqlite3.Error as e:
        flash(f"Error updating course: {e}", "danger")
        return redirect(url_for('course_schedule'))


# Route to delete a course
@app.route('/delete/<int:id>', methods=['POST'])
def delete_course(id):
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM course_schedule WHERE id = ?", (id,))
                conn.commit()

                flash("Course deleted successfully.", "success")
                return redirect(url_for('course_schedule'))

    except sqlite3.Error as e:
        flash(f"Error deleting course: {e}", "danger")
        return redirect(url_for('course_schedule'))

    
# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
