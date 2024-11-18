from flask import Flask, render_template, request, redirect, session, url_for, flash
import sqlite3
from datetime import datetime
from datetime import datetime, timedelta

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


# Validate course start and end times
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
    """Check scheduling conflicts for teacher, room, slot overlaps, and days."""
    cursor = conn.cursor()
    
    # SQL query to check for conflicts based on combinations of criteria
    cursor.execute("""
        SELECT * FROM course_schedule WHERE
        (
            -- Case 1: Teacher conflict
            teacher_name = ? AND day_of_week = ? AND
            (
                (class_start_time < ? AND class_end_time > ?) OR  -- New course starts before existing course ends
                (class_start_time < ? AND class_end_time > ?)     -- New course ends after existing course starts
            )
        )
        OR 
        (
            -- Case 2: Room conflict (same room, same day, overlapping time)
            room = ? AND day_of_week = ? AND
            (
                (class_start_time < ? AND class_end_time > ?) OR  -- New course starts before existing course ends
                (class_start_time < ? AND class_end_time > ?)     -- New course ends after existing course starts
            )
        )
    """, (teacher_name, day_of_week, start_time, start_time, end_time, end_time, 
          room, day_of_week, start_time, start_time, end_time, end_time))
    
    conflicts = cursor.fetchall()
    return conflicts
   


# Resolving Conflicts through Both Greedy and Backtracking
@app.route('/resolve_conflicts', methods=['POST'])
def resolve_conflicts():
    selected_courses_ids = session.get('selected_courses', [])
    
    # Check if any courses are selected
    if not selected_courses_ids:
        flash("No courses selected yet.", "info")
        return redirect(url_for('course_schedule'))

    try:
        # Greedy algorithm result
        greedy_result = resolve_conflicts_greedy(selected_courses_ids)

        # Backtracking algorithm result
        backtracking_result = resolve_conflicts_backtracking(selected_courses_ids)
        
        # Ensure backtracking_result is a dictionary with expected keys
        if not isinstance(backtracking_result, dict):
            backtracking_result = {'resolved_courses': [], 'unresolved_courses': [], 'error_message': "Error resolving conflicts using backtracking."}

        # Check if the results are empty and provide alternative messages
        if not backtracking_result['resolved_courses']:
            backtracking_result['resolved_message'] = "The backtracking algorithm couldn't resolve any conflicts."
        else:
            backtracking_result['resolved_message'] = "Conflicts were resolved successfully by the backtracking algorithm."
        
        if not backtracking_result['unresolved_courses']:
            backtracking_result['unresolved_message'] = "No unresolved conflicts were found after applying the backtracking algorithm."
        else:
            backtracking_result['unresolved_message'] = "Some unresolved conflicts exist after applying the backtracking algorithm."
        
        # Check if greedy algorithm results are valid (this should be added similarly to backtracking)
        if 'resolved_courses' not in greedy_result:
            greedy_result = {'resolved_courses': [], 'unresolved_courses': [], 'error_message': "Error resolving conflicts using the greedy algorithm."}
        
        if not greedy_result['resolved_courses']:
            greedy_result['resolved_message'] = "The greedy algorithm couldn't resolve any conflicts."
        else:
            greedy_result['resolved_message'] = "Conflicts were resolved successfully by the greedy algorithm."
        
        if not greedy_result['unresolved_courses']:
            greedy_result['unresolved_message'] = "No unresolved conflicts were found after applying the greedy algorithm."
        else:
            greedy_result['unresolved_message'] = "Some unresolved conflicts exist after applying the greedy algorithm."

    except Exception as e:
        # In case of an error during conflict resolution
        flash(f"An error occurred: {str(e)}", "danger")
        return redirect(url_for('course_schedule'))

    # Return both results to the template
    return render_template('resolve_conflicts.html', greedy_result=greedy_result, backtracking_result=backtracking_result)




def backtrack(courses, index, assigned_courses, available_times):
    # Base case: if all courses have been checked, return the assigned courses
    if index >= len(courses):
        return assigned_courses
    
    current_course = courses[index]
    day = current_course[3]  # 'day_of_week'
    start_time = current_course[4]  # 'class_start_time'
    end_time = current_course[5]  # 'class_end_time'
    
    # Ensure availability for the day is tracked
    if day not in available_times:
        available_times[day] = []

    # Check if current course conflicts with assigned courses on the same day
    conflict = False
    for assigned_course in available_times[day]:
        assigned_start = assigned_course[4]
        assigned_end = assigned_course[5]

        # Check for time overlap
        if not (end_time <= assigned_start or start_time >= assigned_end):
            conflict = True
            break
    
    # If no conflict, try to assign this course and continue
    if not conflict:
        # Add to assigned courses and update available times
        assigned_courses.append(current_course)
        available_times[day].append(current_course)
        
        # Recursively call backtrack for the next course
        result = backtrack(courses, index + 1, assigned_courses, available_times)
        if result:  # If a valid schedule was found
            return result
        
        # Backtrack: remove the current course and try the next possibility
        assigned_courses.pop()
        available_times[day].remove(current_course)
    
    # Try skipping the current course and continue with the next one
    return backtrack(courses, index + 1, assigned_courses, available_times)

def resolve_conflicts_backtracking(selected_courses_ids):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        query = "SELECT id, teacher_name, course_title, day_of_week, class_start_time, class_end_time, room FROM course_schedule WHERE id IN ({})".format(
            ','.join('?' for _ in selected_courses_ids)
        )
        cursor.execute(query, tuple(selected_courses_ids))
        selected_courses = cursor.fetchall()

    # Sort courses for better backtracking performance (e.g., by start time or other criteria)
    selected_courses.sort(key=lambda x: (x[3], x[4]))  # Sort by 'day_of_week' and 'class_start_time'

    # Initiate backtracking with empty structures
    assigned_courses = []
    available_times = {}
    resolved_courses = backtrack(selected_courses, 0, assigned_courses, available_times)

    # Prepare the response dictionary
    unresolved_courses = [course for course in selected_courses if course not in resolved_courses]

    if not resolved_courses:
        return {
            'resolved_courses': [],
            'unresolved_courses': unresolved_courses,
            'error_message': "No conflicts could be resolved. Please review your input data."
        }

    return {
        'resolved_courses': resolved_courses,
        'unresolved_courses': unresolved_courses,
    }

# Greedy Algorithm: Resolves conflicts by selecting the first available room/time slot.
def resolve_conflicts_greedy(selected_courses_ids):
    with get_db_connection() as conn:
        cursor = conn.cursor()
        
        # Ensure the query is properly constructed with placeholders for selected_courses_ids
        query = "SELECT id, teacher_name, course_title, day_of_week, class_start_time, class_end_time, room FROM course_schedule WHERE id IN ({})".format(
            ','.join(['?'] * len(selected_courses_ids))  # Ensure the right number of placeholders
        )

        # Execute the query with the tuple of selected_courses_ids
        cursor.execute(query, tuple(selected_courses_ids))
        selected_courses = cursor.fetchall()

    # Map weekdays to numeric values
    DAY_MAP = {
        'Monday': 1,
        'Tuesday': 2,
        'Wednesday': 3,
        'Thursday': 4,
        'Friday': 5,
        'Saturday': 6,
        'Sunday': 7
    }

    # Sort courses by day_of_week (numeric) and then by start_time
    selected_courses.sort(key=lambda x: (DAY_MAP[x[3]], x[4]))  # Convert day_of_week to numeric using DAY_MAP

    resolved_courses = []
    unresolved_courses = []

    # Dictionary to track room bookings: {day: {room: [(start_time, end_time), ...]}}

    room_availability = {day: {room: [] for room in range(1, 6)} for day in range(1, 8)}

    for course in selected_courses:
        course_id, teacher_name, course_title, day_of_week, start_time, end_time, room = course
        day_of_week_numeric = DAY_MAP[day_of_week]  # Convert day_of_week to numeric

        conflict = False

        # Check if room is available for the given time slot
        for existing_start, existing_end in room_availability[day_of_week_numeric][room]:
            if not (end_time <= existing_start or start_time >= existing_end):  # Conflict
                conflict = True
                break

        if conflict:
            # Try to resolve conflict by selecting the first available alternative room
            found_alternative = False
            for alt_room in range(1, 6):  # Room 1-5
                if alt_room != room:  # Skip the same room
                    for existing_start, existing_end in room_availability[day_of_week_numeric][alt_room]:
                        if not (end_time <= existing_start or start_time >= existing_end):
                            break
                    else:
                        # No conflict, assign this course to the alternative room
                        room_availability[day_of_week_numeric][alt_room].append((start_time, end_time))
                        resolved_courses.append({
                            'id': course_id,
                            'course_title': course_title,
                            'teacher_name': teacher_name,
                            'day_of_week': day_of_week,
                            'class_start_time': start_time,
                            'class_end_time': end_time,
                            'room': alt_room
                        })
                        found_alternative = True
                        break

            if not found_alternative:
                unresolved_courses.append({
                    'id': course_id,
                    'course_title': course_title,
                    'teacher_name': teacher_name,
                    'day_of_week': day_of_week,
                    'class_start_time': start_time,
                    'class_end_time': end_time,
                    'room': room,
                    'conflict': "No available room for this time slot"
                })
        else:
            # No conflict, assign the course to the room
            room_availability[day_of_week_numeric][room].append((start_time, end_time))
            resolved_courses.append({
                'id': course_id,
                'course_title': course_title,
                'teacher_name': teacher_name,
                'day_of_week': day_of_week,
                'class_start_time': start_time,
                'class_end_time': end_time,
                'room': room
            })

    return {
        'resolved_courses': resolved_courses,
        'unresolved_courses': unresolved_courses
    }



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
@app.route('/course_schedule', methods=['GET', 'POST'])
def course_schedule():
    try:
        # Fetch selected course IDs from the session
        selected_courses_ids = session.get('selected_courses', [])

        # Check if any courses were selected
        if not selected_courses_ids:
            flash("No courses selected yet.", "info")
            return render_template('course_schedule.html', grouped_courses_by_day={}, selected_courses=[], conflicts={})

        # Connect to the database and get course details
        with get_db_connection() as conn:
            cursor = conn.cursor()
            query = "SELECT id, teacher_name, course_title, day_of_week, class_start_time, class_end_time, room FROM course_schedule WHERE id IN ({})".format(
                ','.join('?' for _ in selected_courses_ids)
            )
            cursor.execute(query, tuple(selected_courses_ids))
            selected_courses = cursor.fetchall()

        # Group courses by day for better organization
        grouped_courses_by_day = {}
        for course in selected_courses:
            day = course[3]  # 'day_of_week'
            if day not in grouped_courses_by_day:
                grouped_courses_by_day[day] = []
            grouped_courses_by_day[day].append(course)

        # Initialize an empty dict to store conflicts
        conflicts = {}

        # Check for conflicts
        for day, courses in grouped_courses_by_day.items():
            day_conflicts = []
            for i, course in enumerate(courses):
                for j, other_course in enumerate(courses):
                    if i >= j:
                        continue
                    # Check for time and room conflicts
                    if (course[4] < other_course[5] and course[5] > other_course[4]):  # Time overlap
                        if course[6] == other_course[6]:  # Room conflict only if they are in the same room
                            conflict_details = {
                                'course_name': course[2],
                                'teacher_name': course[1],
                                'conflicting_course_name': other_course[2],
                                'conflicting_teacher_name': other_course[1],
                                'conflicting_start_time': other_course[4],
                                'conflicting_end_time': other_course[5],
                                'conflicting_room': other_course[6],
                            }
                            day_conflicts.append(conflict_details)
            if day_conflicts:
                conflicts[day] = day_conflicts

        return render_template('course_schedule.html', grouped_courses_by_day=grouped_courses_by_day, selected_courses=selected_courses, conflicts=conflicts)

    except sqlite3.Error as e:
        flash(f"Error fetching selected courses: {e}", "danger")
        return render_template('course_schedule.html', grouped_courses_by_day={}, selected_courses=[], conflicts={})

    except Exception as e:
        flash(f"An unexpected error occurred: {e}", "danger")
        return render_template('course_schedule.html', grouped_courses_by_day={}, selected_courses=[], conflicts={})



# Route to select courses
@app.route('/select_courses', methods=['GET', 'POST'])
def select_courses():
    try:
        # Fetch all available courses with teacher information
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("""
                    SELECT id, teacher_name, course_code , course_title, day_of_week, class_start_time, class_end_time
                    FROM course_schedule
                """)
                courses = cursor.fetchall()
            else:
                raise sqlite3.Error("Failed to connect to the database")

        # Get the list of selected courses from the session, defaulting to an empty list if none
        selected_courses = session.get('selected_courses', [])

        if request.method == 'POST':
            # Get the list of selected courses from the form (checkboxes)
            selected_courses = request.form.getlist('courses')

            # Ensure the user selects no more than 6 courses
            if len(selected_courses) > 6:
                flash("You can only select up to 6 courses.", "warning")
                return redirect(url_for('select_courses'))  # Redirect back to the same page

            if len(selected_courses) == 0:
                flash("Please select at least one course.", "warning")
                return redirect(url_for('select_courses'))

            # Store the selected courses in the session for persistence
            session['selected_courses'] = selected_courses

            flash("Courses successfully selected!", "success")
            return redirect(url_for('course_schedule'))  # Redirect to the course schedule page

        # Pass the selected_courses to the template
        return render_template('select_courses.html', courses=courses, selected_courses=selected_courses)

    except sqlite3.Error as e:
        flash(f"Database error: {e}", "danger")
        return render_template('select_courses.html', courses=[], selected_courses=[])



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
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (teacher_name, course_code, course_title, day_of_week, class_start_time, class_end_time, room))
                conn.commit()
                flash("Course added successfully!", "success")
                return redirect(url_for('index'))  # Redirect to the home page

        except sqlite3.Error as e:
            flash(f"Error adding course: {e}", "danger")

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

                if course is None:
                    flash("Course not found.", "danger")
                    return redirect(url_for('course_list'))

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
                    return redirect(url_for('course_list'))
                else:
                    return render_template('edit_course.html', course=course)
            else:
                raise sqlite3.Error("Failed to connect to the database")

    except sqlite3.Error as e:
        flash(f"Error updating course: {e}", "danger")
        return redirect(url_for('course_list'))


# Route to delete a course
@app.route('/delete/<int:id>', methods=['GET',])
def delete_course(id):
    try:
        with get_db_connection() as conn:
            if conn:
                cursor = conn.cursor()
                cursor.execute("DELETE FROM course_schedule WHERE id = ?", (id,))
                conn.commit()

                flash("Course deleted successfully.", "success")
                return redirect(url_for('course_list'))

    except sqlite3.Error as e:
        flash(f"Error deleting course: {e}", "danger")
        return redirect(url_for('course_list'))

    
# Start the Flask application
if __name__ == '__main__':
    app.run(debug=True)
