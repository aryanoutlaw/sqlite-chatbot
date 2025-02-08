import sqlite3
import random
from datetime import datetime, timedelta

# Connect to SQLite database (creates chatbot.db if it doesn't exist)
conn = sqlite3.connect("chatbot.db")
cursor = conn.cursor()

# Create Employees table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Employees (
    ID INTEGER PRIMARY KEY, 
    Name TEXT, 
    Department TEXT, 
    Salary INTEGER, 
    Hire_Date TEXT
)
""")

# Create Departments table
cursor.execute("""
CREATE TABLE IF NOT EXISTS Departments (
    ID INTEGER PRIMARY KEY, 
    Name TEXT, 
    Manager TEXT
)
""")

# Department names & managers
departments = [
    ("Sales", "Alice"),
    ("Engineering", "Bob"),
    ("Marketing", "Charlie"),
    ("Finance", "Diana"),
    ("HR", "Ethan"),
    ("Customer Support", "Fiona"),
    ("IT", "George"),
    ("Operations", "Hannah"),
    ("Legal", "Ian"),
    ("Product Management", "Jack")
]

# Insert departments into the table
cursor.executemany("INSERT INTO Departments (ID, Name, Manager) VALUES (?, ?, ?)", 
                   [(i+1, dept[0], dept[1]) for i, dept in enumerate(departments)])

# Employee names list
employee_names = [
    "Alice", "Bob", "Charlie", "David", "Emma", "Frank", "Grace", "Hannah", "Ian", "Jack",
    "Kevin", "Lily", "Michael", "Nina", "Oliver", "Paula", "Quinn", "Rachel", "Steve", "Tina",
    "Uma", "Victor", "Wendy", "Xavier", "Yvonne", "Zack", "Andrew", "Brenda", "Chris", "Denise",
    "Edward", "Felicity", "George", "Helen", "Isaac", "Jasmine", "Kyle", "Laura", "Matthew", "Nancy",
    "Oscar", "Patricia", "Quincy", "Rebecca", "Sam", "Tracy", "Ursula", "Vincent", "Walter", "Zoe"
]

# Generate random employee data
employees = []
start_date = datetime(2015, 1, 1)
for i in range(50):
    name = employee_names[i % len(employee_names)]
    department = random.choice(departments)[0]  # Select random department
    salary = random.randint(45000, 120000)  # Random salary between 45K and 120K
    hire_date = start_date + timedelta(days=random.randint(0, 365 * 8))  # Random date in last 8 years
    hire_date_str = hire_date.strftime("%Y-%m-%d")
    employees.append((i+1, name, department, salary, hire_date_str))

# Insert employees into the table
cursor.executemany("INSERT INTO Employees (ID, Name, Department, Salary, Hire_Date) VALUES (?, ?, ?, ?, ?)", employees)

# Save changes and close connection
conn.commit()
conn.close()

print("✅ chatbot.db with 50 employees and 10 departments created successfully!")