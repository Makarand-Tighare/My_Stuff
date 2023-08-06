from datetime import datetime, timedelta
from dateutil import parser
import sqlite3

# Function to create the timetable table in the database
def create_table():
    conn = sqlite3.connect("timetable.db")
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS timetable (
            day TEXT,
            time TEXT,
            activity TEXT,
            time_duration TEXT,
            PRIMARY KEY (day, time)
        )
    ''')

    conn.commit()
    conn.close()

# Function to insert the timetable data into the database
def insert_timetable_data(timetable):
    conn = sqlite3.connect("timetable.db")
    cursor = conn.cursor()

    for day_data in timetable:
        day = day_data["Day"]
        time = day_data["Time"]
        activity = day_data["Activity"]
        time_duration = day_data["Time Duration"]

        # Check if the record already exists in the database
        cursor.execute("SELECT * FROM timetable WHERE day=? AND time=?", (day, time))
        existing_record = cursor.fetchone()

        if existing_record is None:
            cursor.execute("INSERT INTO timetable VALUES (?, ?, ?, ?)", (day, time, activity, time_duration))
        else:
            # You can choose to update the existing record here if needed
            # For example: cursor.execute("UPDATE timetable SET activity=?, time_duration=? WHERE day=? AND time=?", (activity, time_duration, day, time))
            pass

    conn.commit()
    conn.close()

# Function to parse time strings with and without minutes
def parse_time_string(time_str):
    try:
        time_obj = parser.parse(time_str)
        return time_obj.strftime("%I:%M%p")
    except ValueError:
        return None

# Function to mark the GATE study completion for a specific day and time
def mark_gate_study_completion(day, time):
    conn = sqlite3.connect("timetable.db")
    cursor = conn.cursor()

    # Update the "Time Duration" column to mark the completion of GATE study
    cursor.execute("UPDATE timetable SET time_duration='completed' WHERE day=? AND time=?", (day, time))

    conn.commit()
    conn.close()

# Function to check if you studied for GATE as per the timetable
def check_gate_study_completion(timetable_data):
    today = datetime.now().strftime("%A")  # Get the current day (e.g., "Monday")
    current_time = datetime.now().strftime("%I:%M%p")  # Get the current time in the format "8:30am"

    for day in timetable_data:
        if day["Day"] == today and "GATE study" in day["Activity"]:
            start_time_str, end_time_str = day["Time"].split(" - ")

            # Parse the time strings in the consistent format
            start_time = parser.parse(start_time_str)
            end_time = parser.parse(end_time_str)
            current_time_obj = parser.parse(current_time)

            # Check if the current time falls within the GATE study time range
            if start_time <= current_time_obj <= end_time:
                # Mark GATE study completion for the current day and time
                mark_gate_study_completion(today, day["Time"])
                return True

    return False

# Function to calculate the total reward to be transferred
def calculate_reward_to_transfer(timetable_data, reward_per_hour=10):
    completed_gate_study_hours = 0

    for day in timetable_data:
        if day["Time Duration"] == "completed":
            start_time_str, end_time_str = day["Time"].split(" - ")

            # Parse the time strings in the consistent format
            start_time = parser.parse(start_time_str)
            end_time = parser.parse(end_time_str)

            # Calculate the study hours using timedelta
            study_duration = end_time - start_time
            study_hours = study_duration.total_seconds() / 3600

            completed_gate_study_hours += study_hours

    total_reward = completed_gate_study_hours * reward_per_hour
    return total_reward
# Function to ask whether the GATE study was completed as per the timetable
def ask_gate_study_completion():
    current_time = datetime.now().strftime("%I:%M%p")
    day = datetime.now().strftime("%A")
    completed_gate_study = False

    # Get the GATE study activity for the current hour
    current_hour_activity = next((activity for activity in timetable if activity["Day"] == day and activity["Time"] == current_time), None)

    if current_hour_activity and "GATE study" in current_hour_activity["Activity"]:
        while True:
            user_input = input(f"Did you complete the GATE study for {day} from {current_time} to {current_hour_activity['Time'].split(' - ')[1]}? (yes/no): ")
            if user_input.lower() == "yes":
                completed_gate_study = True
                break
            elif user_input.lower() == "no":
                completed_gate_study = False
                break
            else:
                print("Invalid input. Please enter 'yes' or 'no'.")

    return completed_gate_study

# Function to convert database query result into a list of dictionaries
def convert_to_dict(data):
    keys = ["Day", "Time", "Activity", "Time Duration"]
    timetable_list = []

    for row in data:
        timetable_dict = dict(zip(keys, row))
        timetable_list.append(timetable_dict)

    return timetable_list

# Example timetable data
timetable = [
    # Monday
    {
        "Day": "Monday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "8am - 9am",
        "Activity": "Travel",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "9am - 12pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "12pm - 1pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "1pm - 4pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "4pm - 5pm",
        "Activity": "Evening Routine",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "5pm - 6pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Monday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Tuesday
    {
        "Day": "Tuesday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "8am - 9am",
        "Activity": "Travel",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "9am - 12pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "12pm - 1pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "1pm - 4pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "4pm - 5pm",
        "Activity": "Evening Routine",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "5pm - 6pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Tuesday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Wednesday
    {
        "Day": "Wednesday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "8am - 9am",
        "Activity": "Travel",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "9am - 12pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "12pm - 1pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "1pm - 4pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "4pm - 5pm",
        "Activity": "Evening Routine",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "5pm - 6pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Wednesday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Thursday
    {
        "Day": "Thursday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "8am - 9am",
        "Activity": "Travel",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "9am - 12pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "12pm - 1pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "1pm - 4pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "4pm - 5pm",
        "Activity": "Evening Routine",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "5pm - 6pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Thursday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Friday
    {
        "Day": "Friday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "8am - 9am",
        "Activity": "Travel",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "9am - 12pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "12pm - 1pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "1pm - 4pm",
        "Activity": "College lectures",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "4pm - 5pm",
        "Activity": "Evening Routine",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "5pm - 6pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Friday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Saturday
    {
        "Day": "Saturday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "8am - 9am",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "9am - 10:30am",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "10:30am - 11am",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "11am - 12:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "12:30pm - 1:30pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "1:30pm - 3pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "3pm - 4pm",
        "Activity": "Revision of important topics",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "4pm - 5pm",
        "Activity": "Mock test",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "5pm - 6pm",
        "Activity": "Analysis of mock test",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Saturday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },

    # Sunday
    {
        "Day": "Sunday",
        "Time": "7am - 8am",
        "Activity": "Morning Routine",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "8am - 9am",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "9am - 10:30am",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "10:30am - 11am",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "11am - 12:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "12:30pm - 1:30pm",
        "Activity": "Lunch Break",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "1:30pm - 3pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "3pm - 4pm",
        "Activity": "Revision of important topics",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "4pm - 5pm",
        "Activity": "Mock test",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "5pm - 6pm",
        "Activity": "Analysis of mock test",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "6pm - 7pm",
        "Activity": "Break/Snacks",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "7pm - 8:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "8:30pm - 9pm",
        "Activity": "Dinner",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "9pm - 10:30pm",
        "Activity": "GATE study",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "10:30pm - 11pm",
        "Activity": "Revision of day's topics",
        "Time Duration": "",
    },
    {
        "Day": "Sunday",
        "Time": "11pm",
        "Activity": "Sleep",
        "Time Duration": "",
    },
]

# Create the timetable table in the database and insert the data
create_table()
insert_timetable_data(timetable)

# Retrieve data from the database and calculate the reward
conn = sqlite3.connect("timetable.db")
cursor = conn.cursor()

cursor.execute("SELECT * FROM timetable")
timetable_data = cursor.fetchall()

timetable_data_as_dict = convert_to_dict(timetable_data)

reward = calculate_reward_to_transfer(timetable_data_as_dict)
print("Total reward: {} rupees".format(reward))

completed_gate_study = ask_gate_study_completion()

if completed_gate_study:
    print("Great! You completed the GATE study as per the timetable for today.")
else:
    print("Oops! Looks like you missed your GATE study as per the timetable for today.")

print("Total reward to be transferred: {} rupees".format(reward if completed_gate_study else 0))

conn.close()
