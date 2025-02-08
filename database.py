import sqlite3

class DatabaseManager:
    def __init__(self, db_path="chatbot.db"):
        self.db_path = db_path

    def init_db(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # Create Employees table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Employees (
                ID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Department TEXT NOT NULL,
                Salary INTEGER NOT NULL,
                Hire_Date DATE NOT NULL
            )
        """)

        # Create Departments table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS Departments (
                ID INTEGER PRIMARY KEY,
                Name TEXT NOT NULL,
                Manager TEXT NOT NULL
            )
        """)

        conn.commit()
        conn.close()

    def execute_query(self, query, params=None):
        """Execute a SQL query and return results or error messages"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        try:
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)

            if cursor.description:  # If it's a SELECT query
                results = cursor.fetchall()
                column_names = [desc[0] for desc in cursor.description]
                return {"columns": column_names, "data": results}
            else:  # If it's an INSERT, UPDATE, or DELETE
                conn.commit()
                return {"message": "Query executed successfully."}
        except sqlite3.Error as e:
            return {"error": f"Database error: {str(e)}"}
        finally:
            conn.close()

    def get_departments(self):
        """Get list of all department names"""
        result = self.execute_query("SELECT Name FROM Departments")
        if "data" in result:
            return [dept[0] for dept in result["data"]]
        return []