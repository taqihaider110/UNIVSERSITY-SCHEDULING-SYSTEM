# scheduler.py

class TimetableScheduler:
    def __init__(self):
        self.schedule = {}
        self.time_slots = ["9:00 AM", "10:00 AM", "11:00 AM", "12:00 PM", "1:00 PM", "2:00 PM"]
        self.rooms = ["Room A", "Room B", "Room C"]

    def greedy_schedule(self, subjects):
        for i, subject in enumerate(subjects):
            if i < len(self.time_slots):
                # Assign subject to available time slots
                self.schedule[subject] = {
                    "time": self.time_slots[i],
                    "room": self.rooms[i % len(self.rooms)]  # Cycle through rooms
                }
        return self.schedule

    def backtrack_schedule(self, subjects, index=0, assigned=None):
        if assigned is None:
            assigned = {}

        # Base case: if all subjects are assigned
        if index == len(subjects):
            return assigned

        subject = subjects[index]
        for time in self.time_slots:
            for room in self.rooms:
                # Check if this time and room are already assigned
                if not any(s["time"] == time and s["room"] == room for s in assigned.values()):
                    assigned[subject] = {"time": time, "room": room}
                    result = self.backtrack_schedule(subjects, index + 1, assigned)
                    if result:
                        return result
                    del assigned[subject]  # Remove the assignment if it didn't lead to a solution
        return None  # No valid assignment found

    def get_schedule(self):
        return self.schedule
