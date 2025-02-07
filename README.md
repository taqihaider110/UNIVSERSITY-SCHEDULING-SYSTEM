# 📌 CourseFlow - University Course Scheduler  
_Automated Course Scheduling with Greedy & Backtracking Algorithms_

---

## 📖 Overview  
CourseFlow is a web-based **University Course Scheduling System** that automates the process of assigning courses to classrooms and time slots while resolving conflicts.  
It uses **Flask (Python) & SQLite** to manage the course schedule and employs **Greedy & Backtracking Algorithms** for conflict resolution.

---

## 🚀 Features  
✅ Conflict-free scheduling using **Greedy & Backtracking** algorithms  
✅ Real-time **conflict detection & resolution**  
✅ Interactive web interface for **admins to manage course schedules**  
✅ Supports **teacher & room conflict resolution**  
✅ **Algorithm performance comparison**  

---

## 🛠️ Tech Stack  

| Component  | Technology Used |
|------------|----------------|
| **Backend** | Flask (Python) |
| **Database** | SQLite |
| **Frontend** | HTML, CSS, Jinja Templates |
| **Algorithms** | Greedy & Backtracking |

---

## 📥 Installation Guide  
Follow these steps to set up **CourseFlow** locally.

### 1️⃣ Clone the Repository  
git clone https://github.com/yourusername/courseflow.git
cd courseflow

2️⃣ Install Dependencies
pip install -r requirements.txt

3️⃣ Setup the Database
python setup_db.py

4️⃣ Run the Application
flask run

### 📌 How It Works
#### 1️⃣ Database Setup
- Stores course details (course code, title, teacher, time slot, room).
- Uses SQLite as the database.

#### 2️⃣ Conflict Detection
- Teacher Conflict: Prevents teachers from being double-booked.
- Room Conflict: Ensures no two classes occupy the same room simultaneously.
  
#### 3️⃣ Conflict Resolution
- Greedy Algorithm: Fast, assigns courses to the first available slot.
- Backtracking Algorithm: Slower but ensures an optimal schedule.
- Performance Comparison: The system determines the better algorithm for each scenario.

### 🖥️ Usage Guide  

### 1️⃣ Adding Courses  
- Navigate to **"Add Course"** page  
- Enter course details  
- Click **Submit**  

### 2️⃣ Viewing Courses  
- Navigate to **"View Courses"** page  
- See all scheduled courses  
- Edit or delete courses as needed  

### 3️⃣ Conflict Resolution  
- Select courses to **check for conflicts**  
- Click **"Resolve Conflicts"**  
- View results of **Greedy vs. Backtracking Algorithms**  

---

## 📊 Algorithm Comparison  

| Algorithm  | Speed  | Accuracy | Best For |
|------------|--------|----------|----------|
| **Greedy** | ✅ Fast | ❌ May not find optimal solution | Small & simple schedules |
| **Backtracking** | ❌ Slow | ✅ Finds optimal schedule | Complex schedules with many constraints |

---

## Visual Representation of the Project
![image](https://github.com/user-attachments/assets/37e77920-b9c1-48ce-b1f3-61ce9a7899bb)

### Add a New Course:
●	**Purpose**: Allows users to add a new course by filling out a form.<br>
●	**Features**:
  - **Input Fields**: Includes fields for teacher name, course code, course title, day of the week, class start and end times, and room.
  - **Submit Button**: Users can submit the form to add the course to the schedule.
  - **Navigation**: Provides an option to go back to the main schedule page.

![image](https://github.com/user-attachments/assets/f99ccaf0-7264-473f-aab1-deebfe264726)

### View Courses:
●	**Purpose**: Allows users to view, filter, and manage courses.
●	**Features**:
  - **Course Table**: Displays course details like teacher, course code, and schedule.
  - **Action Buttons**: Options to edit or delete courses.
  - **Filter Form**: Enables users to search for courses by teacher, course code, or day of the week.

![image](https://github.com/user-attachments/assets/a9f79bac-323c-45f5-add6-e7ad0995f58f)

### Course Selection Page:
●	**Purpose**: Allow users to choose up to six courses from a provided list.
●	**Features**:
  - **Selection** Form: Checkboxes for course selection, up to a six-course limit.
  - **Feedback**: Flash messages to inform users of actions or errors.
  - **Controls**: Buttons for submitting selections or clearing the form.

![image](https://github.com/user-attachments/assets/8adf8ccd-2a49-4665-aa1e-a84c756d4805)
![image](https://github.com/user-attachments/assets/ddfc3c94-3bdb-4f66-b235-cfe8c694ad76)

### Course Schedule Page:
●	**Purpose**: Display a user's selected courses organized by day of the week in a structured table format.
●	**Features**:
  - **Daily Schedule Tables**: Each day has its table with columns for course name, professor, time, and room.
  - **Conflict Detection**: Alerts for overlapping course times, detailing conflicts between courses.
  - **Resolve Conflicts Button**: Provides users with an option to address scheduling issues.


![image](https://github.com/user-attachments/assets/b09790e9-44f9-4fd0-aec1-67bd968386ae)
![image](https://github.com/user-attachments/assets/1ed9cd73-fd34-4477-9c09-d35ddfaa9533)

### Resolve Course Conflicts Page:
●	 **Purpose**: Show results of scheduling conflict resolution using Greedy and Backtracking algorithms.
●	**Sections**:
  - **Greedy Algorithm**: Lists resolved and unresolved courses, details conflicts.
  - **Backtracking Algorithm**: Highlights outcomes with detailed conflict info.

![image](https://github.com/user-attachments/assets/8c3264c7-4903-4609-bc97-c073383ce8f3)
![image](https://github.com/user-attachments/assets/4f4814fd-b9da-4e02-9e20-c54bee5ecf29)

### IN THE END RESULTS:
![image](https://github.com/user-attachments/assets/b32ee734-b74b-4c4d-96ed-57bd4b0616f2)


## 🛠️ Future Enhancements  
🔹 **AI-powered scheduling** for intelligent course assignment  
🔹 **Drag & Drop scheduling UI** for admins  
🔹 **Cloud-based database support** for scalability  

---

## 📄 License  
This project is licensed under the **MIT License**.

---

## 📧 Contact & Contributions  

👤 **Muhammad Taqi Haider**  

🔹 Contributions are welcome! Feel free to submit a **pull request**. 🚀  
