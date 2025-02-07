📌 CourseFlow - University Course Scheduler
Automated Course Scheduling with Greedy & Backtracking Algorithms

📖 Overview
CourseFlow is a web-based University Course Scheduling System that automates the process of assigning courses to classrooms and time slots while resolving conflicts. It uses Flask (Python) & SQLite to manage the course schedule and employs Greedy & Backtracking Algorithms for conflict resolution.

🚀 Features
✅ Conflict-free scheduling using Greedy & Backtracking algorithms
✅ Real-time conflict detection & resolution
✅ Interactive web interface for admins to manage course schedules
✅ Supports teacher & room conflict resolution
✅ Algorithm performance comparison

🛠️ Tech Stack
Component	Technology Used
Backend	Flask (Python)
Database	SQLite
Frontend	HTML, CSS, Jinja Templates
Algorithms	Greedy & Backtracking
📥 Installation Guide
Follow these steps to set up CourseFlow locally.

1️⃣ Clone the Repository
bash
Copy
Edit
git clone https://github.com/yourusername/courseflow.git
cd courseflow
2️⃣ Install Dependencies
bash
Copy
Edit
pip install -r requirements.txt
3️⃣ Setup the Database
bash
Copy
Edit
python setup_db.py
4️⃣ Run the Application
bash
Copy
Edit
flask run
✅ The application will run at http://127.0.0.1:5000/.

📌 How It Works
1️⃣ Database Setup
Stores course details (course code, title, teacher, time slot, room).
Uses SQLite as the database.
2️⃣ Conflict Detection
Teacher Conflict: Prevents teachers from being double-booked.
Room Conflict: Ensures no two classes occupy the same room simultaneously.
3️⃣ Conflict Resolution
Greedy Algorithm: Fast, assigns courses to the first available slot.
Backtracking Algorithm: Slower but ensures an optimal schedule.
Performance Comparison: The system determines the better algorithm for each scenario.
🖥️ Usage Guide
1️⃣ Adding Courses
Navigate to "Add Course" page
Enter course details
Click Submit
2️⃣ Viewing Courses
Navigate to "View Courses" page
See all scheduled courses
Edit or delete courses as needed
3️⃣ Conflict Resolution
Select courses to check for conflicts
Click "Resolve Conflicts"
View results of Greedy vs. Backtracking Algorithms
📊 Algorithm Comparison
Algorithm	Speed	Accuracy	Best For
Greedy	✅ Fast	❌ May not find optimal solution	Small & simple schedules
Backtracking	❌ Slow	✅ Finds optimal schedule	Complex schedules with many constraints
🛠️ Future Enhancements
🔹 AI-powered scheduling for intelligent course assignment
🔹 Drag & Drop scheduling UI for admins
🔹 Cloud-based database support for scalability

📄 License
This project is licensed under the MIT License.

📧 Contact & Contributions
👤 Muhammad Taqi Haider (Group Leader)
👥 Team Members: Syed Faris Ali

🔹 Contributions are welcome! Feel free to submit a pull request. 🚀
