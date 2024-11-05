import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def greedy_schedule(courses):
    """Greedy algorithm to schedule courses."""
    scheduled_courses = []
    time_slots = set()  # Track used time slots

    for course in courses:
        # Check if the time slots for the course overlap with scheduled courses
        if not any(slot in time_slots for slot in course['time_slots']):
            scheduled_courses.append(course)
            time_slots.update(course['time_slots'])  # Add time slots to the used set

    return scheduled_courses

def backtracking_schedule(courses, scheduled=[], index=0):
    """Backtracking algorithm to schedule courses."""
    if index == len(courses):
        return scheduled  # All courses are scheduled

    # Check if the course can be added
    current_course = courses[index]
    if all(slot not in scheduled for slot in current_course['time_slots']):
        scheduled.append(current_course)
        result = backtracking_schedule(courses, scheduled, index + 1)
        if result is not None:
            return result
        scheduled.pop()  # Backtrack if it doesn't lead to a solution

    return backtracking_schedule(courses, scheduled, index + 1)

@app.route("/", methods=["GET", "POST"])
def index():
    manual_data = None
    excel_data = None
    greedy_result_html = ""
    backtracking_result_html = ""

    if request.method == "POST":
        # Handle manual entry
        if 'manual_entry' in request.form:
            # Retrieve manual data and convert time slots to a list
            course_code = request.form['course_code']
            course_title = request.form['course_title']
            abbreviation = request.form['abbreviation']
            teacher_name = request.form['teacher_name']
            section_a_schedule = request.form['section_a_schedule'].split(',')  # List of time slots
            section_b_schedule = request.form['section_b_schedule'].split(',')  # List of time slots
            section_a_room = request.form['section_a_room']
            section_b_room = request.form['section_b_room']
            
            # Store the manual data for displaying
            manual_data = {
                "Course Code": course_code,
                "Course Title": course_title,
                "Abbreviation": abbreviation,
                "Course Teacher Name": teacher_name,
                "Section-A Schedule": section_a_schedule,
                "Section-B Schedule": section_b_schedule,
                "Section-A Room": section_a_room,
                "Section-B Room": section_b_room
            }

        # Handle file upload
        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)
                
                # Read the Excel file into a pandas DataFrame
                df = pd.read_excel(filename)

                # Convert DataFrame to list of course dictionaries
                courses = []
                for _, row in df.iterrows():
                    courses.append({
                        'course_code': row['Course Code'],
                        'course_title': row['Course Title'],
                        'abbreviation': row['Abbreviation'],
                        'teacher_name': row['Course Teacher Name'],
                        'time_slots': row['Section-A Schedule'].split(',')  # Assuming this is a comma-separated string
                    })

                # Schedule courses using greedy and backtracking algorithms
                greedy_result = greedy_schedule(courses)
                backtracking_result = backtracking_schedule(courses)

                # Convert results to HTML format for display
                greedy_result_html = pd.DataFrame(greedy_result).to_html(classes='data', header="true", index=False) if greedy_result else "No courses scheduled."
                backtracking_result_html = pd.DataFrame(backtracking_result).to_html(classes='data', header="true", index=False) if backtracking_result else "No courses scheduled."
                
                excel_data = df.to_html(classes='data', header="true", index=False)

    return render_template("index.html", manual_data=manual_data, excel_data=excel_data, 
                           greedy_result=greedy_result_html, backtracking_result=backtracking_result_html)

if __name__ == "__main__":
    app.run(debug=True)
