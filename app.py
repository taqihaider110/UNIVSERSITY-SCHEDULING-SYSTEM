import os
from flask import Flask, render_template, request
import pandas as pd

app = Flask(__name__)

# Folder to store uploaded files
UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# Allowed file extensions
ALLOWED_EXTENSIONS = {'xlsx', 'xls'}

# Function to check if the file extension is allowed
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Greedy Algorithm Code with Enhancements
def greedy_schedule(courses):
    teacher_schedule = {}
    room_schedule = {}
    schedule = []

    # Sort courses by their priority (e.g., number of sections, room availability)
    courses = sorted(courses, key=lambda x: (len(x['section_a_schedule']) + len(x['section_b_schedule'])), reverse=True)  # Prioritize courses with more sections

    for course in courses:
        assigned = False
        for time_slot in course['time_slots']:
            # Check for teacher clash
            if course['teacher_name'] not in teacher_schedule or time_slot not in teacher_schedule[course['teacher_name']]:
                # Check for room clash in Section-A
                if course['section_a_room'] not in room_schedule or time_slot not in room_schedule[course['section_a_room']]:
                    # Check for room clash in Section-B
                    if course['section_b_room'] not in room_schedule or time_slot not in room_schedule[course['section_b_room']]:
                        # Assign course to this timeslot and room
                        teacher_schedule.setdefault(course['teacher_name'], []).append(time_slot)
                        room_schedule.setdefault(course['section_a_room'], []).append(time_slot)
                        room_schedule.setdefault(course['section_b_room'], []).append(time_slot)
                        schedule.append({
                            'course_code': course['course_code'],
                            'time_slot': time_slot,
                            'teacher': course['teacher_name'],
                            'section_a_room': course['section_a_room'],
                            'section_b_room': course['section_b_room']
                        })
                        assigned = True
                        break
        if not assigned:
            print(f"Course {course['course_code']} could not be scheduled.")
    return schedule

# Backtracking Algorithm Code with Enhanced Conflict Resolution
def is_safe(course, time_slot, teacher_schedule, room_schedule):
    # Check if the teacher is free at this time slot
    if course['teacher_name'] in teacher_schedule and time_slot in teacher_schedule[course['teacher_name']]:
        return False

    # Check if Section-A room is free at this time slot
    if course['section_a_room'] in room_schedule and time_slot in room_schedule[course['section_a_room']]:
        return False

    # Check if Section-B room is free at this time slot
    if course['section_b_room'] in room_schedule and time_slot in room_schedule[course['section_b_room']]:
        return False

    return True

def backtrack_schedule(courses, teacher_schedule, room_schedule, schedule, idx):
    if idx == len(courses):
        return True  # All courses scheduled successfully

    course = courses[idx]
    for time_slot in course['time_slots']:
        if is_safe(course, time_slot, teacher_schedule, room_schedule):
            # Assign course to this time slot
            teacher_schedule.setdefault(course['teacher_name'], []).append(time_slot)
            room_schedule.setdefault(course['section_a_room'], []).append(time_slot)
            room_schedule.setdefault(course['section_b_room'], []).append(time_slot)

            # Add to schedule
            schedule.append({
                'course_code': course['course_code'],
                'time_slot': time_slot,
                'teacher': course['teacher_name'],
                'section_a_room': course['section_a_room'],
                'section_b_room': course['section_b_room']
            })

            # Recur for next course
            if backtrack_schedule(courses, teacher_schedule, room_schedule, schedule, idx + 1):
                return True

            # Backtrack
            teacher_schedule[course['teacher_name']].remove(time_slot)
            room_schedule[course['section_a_room']].remove(time_slot)
            room_schedule[course['section_b_room']].remove(time_slot)
            schedule.pop()

    return False  # No solution found for this course

def solve_backtracking(courses):
    teacher_schedule = {}
    room_schedule = {}
    schedule = []
    if backtrack_schedule(courses, teacher_schedule, room_schedule, schedule, 0):
        return schedule
    else:
        return "No valid schedule found."

# Function to detect scheduling clashes
def detect_clashes(courses):
    clashes = []
    teacher_schedule = {}
    room_schedule = {}

    for course in courses:
        # Check teacher clash
        for time_slot in course['time_slots']:
            if course['teacher_name'] in teacher_schedule and time_slot in teacher_schedule[course['teacher_name']]:
                clashes.append(f"Clash: Teacher '{course['teacher_name']}' assigned to multiple courses at the same time ({time_slot}).")
            else:
                teacher_schedule.setdefault(course['teacher_name'], []).append(time_slot)

        # Check room clash for Section A
        for time_slot in course['section_a_schedule']:
            if course['section_a_room'] in room_schedule and time_slot in room_schedule[course['section_a_room']]:
                clashes.append(f"Clash: Room '{course['section_a_room']}' is booked for multiple courses at the same time ({time_slot}).")
            else:
                room_schedule.setdefault(course['section_a_room'], []).append(time_slot)

        # Check room clash for Section B
        for time_slot in course['section_b_schedule']:
            if course['section_b_room'] in room_schedule and time_slot in room_schedule[course['section_b_room']]:
                clashes.append(f"Clash: Room '{course['section_b_room']}' is booked for multiple courses at the same time ({time_slot}).")
            else:
                room_schedule.setdefault(course['section_b_room'], []).append(time_slot)

    return clashes

@app.route("/", methods=["GET", "POST"])
def index():
    manual_data = None
    excel_data = None
    clash_results = []
    greedy_schedule_results = []
    backtracking_schedule_results = []

    if request.method == "POST":
        if 'manual_entry' in request.form:
            course_code = request.form['course_code']
            course_title = request.form['course_title']
            abbreviation = request.form['abbreviation']
            teacher_name = request.form['teacher_name']
            section_a_schedule = request.form['section_a_schedule'].split(',')
            section_b_schedule = request.form['section_b_schedule'].split(',')
            section_a_room = request.form['section_a_room']
            section_b_room = request.form['section_b_room']
            
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

            # Detect clashes using greedy and backtracking
            clashes = detect_clashes([manual_data])
            if clashes:
                clash_results = clashes
            else:
                clash_results = ["No clashes detected for manually entered data."]

            # Greedy schedule
            greedy_schedule_results = greedy_schedule([manual_data])

            # Backtracking schedule
            backtracking_schedule_results = solve_backtracking([manual_data])

        if 'file' in request.files:
            file = request.files['file']
            if file and allowed_file(file.filename):
                filename = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
                file.save(filename)

                df = pd.read_excel(filename)
                courses = []
                for _, row in df.iterrows():
                    courses.append({
                        'course_code': row['Course Code'],
                        'course_title': row['Course Title'],
                        'abbreviation': row['Abbreviation'],
                        'teacher_name': row['Course Teacher Name'],
                        'time_slots': row['Section-A Schedule'].split(','),
                        'section_a_schedule': row['Section-A Schedule'].split(','),
                        'section_b_schedule': row['Section-B Schedule'].split(','),
                        'section_a_room': row['Section-A Room'],
                        'section_b_room': row['Section-B Room']
                    })

                # Detect clashes for uploaded file data
                clashes = detect_clashes(courses)
                if clashes:
                    clash_results = clashes
                else:
                    clash_results = ["No clashes detected for uploaded data."]

                # Greedy schedule
                greedy_schedule_results = greedy_schedule(courses)

                # Backtracking schedule
                backtracking_schedule_results = solve_backtracking(courses)

                excel_data = df.to_html(classes='data', header="true", index=False)

    return render_template("index.html", manual_data=manual_data, excel_data=excel_data, 
                           clashes=clash_results, greedy_schedule=greedy_schedule_results, 
                           backtracking_schedule=backtracking_schedule_results)

if __name__ == "__main__":
    app.run(debug=True)
