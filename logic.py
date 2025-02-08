from llama_cpp import Llama
import sqlite3
import re
from database import DatabaseManager
import datetime


# Load GGUF model
llm = Llama(model_path="qwen2.5-coder-1.5b-instruct-q3_k_m.gguf", n_ctx=512, n_threads=8)

# Initialize database manager
db_manager = DatabaseManager()

def is_valid_query(nl_query):
    """Check if the query contains meaningful words."""
    # Reject if too many non-alphabetic characters
    if len(re.findall(r"[a-zA-Z]", nl_query)) < 3:  # Less than 3 letters
        return False
    
    # Reject if only numbers/symbols
    if not re.search(r"[a-zA-Z]", nl_query):  
        return False  

    return True

def detect_query_type(query):
    """Use regex for simple queries, fallback to LLM for complex ones"""

    department_match = re.search(r"(?:from|in)\s+(\w+)\s+department?", query)

    if department_match:
        department = department_match.group(1)  # Extract department name
        return "SELECT * FROM Employees WHERE LOWER(Department) = LOWER(?);", [department], False  # Return valid SQL

    # Detect vague queries and ask for clarification
    if re.match(r".*\bshow\b.*\bemployees\b.*", query):
        return "Your query is too vague. Do you mean employees from a specific department?", [], False

    if re.match(r".*\bshow\b.*\bsalary\b.*", query):
        return "Whose salary should I show? Please provide a department or employee name.", [], False

    # preventing SQL injection
    forbidden_keywords = ["drop", "delete", "alter", "truncate", "update"]
    if any(keyword in query for keyword in forbidden_keywords):
        return "I can't process that request for security reasons.", [], False 
    
    # Detect salary contradictions
    match = re.search(r"salary.*more than (\d+).*less than (\d+)", query)
    if match:
        if int(match.group(1)) > int(match.group(2)):  
            return "This query contradicts itself. Please clarify.", [], False

    # Detect future hire dates
    current_year = datetime.datetime.now().year
    match = re.search(r"hired after (\d{4})", query)
    if match and int(match.group(1)) > current_year:
        return f"No employees were hired after {current_year}.", [], False
    
    # Basic regex-based detection for simple queries
    if re.match(r".*(?:show|list|get|display)\s+(?:all|every)\s+employees?.*", query):
        return "SELECT * FROM Employees ORDER BY Name;", [], False  # False means no LLM needed

    if re.match(r".*who\s+(?:is\s+)?the\s+manager\s+of\s+(?:the\s+)?(\w+)\s+department.*", query):
        department = re.search(r"manager\s+of\s+(?:the\s+)?(\w+)", query).group(1)
        return "SELECT Manager FROM Departments WHERE LOWER(Name) = LOWER(?);", [department], False

    if re.match(r".*(?:group|sort|arrange)\s+(?:all\s+)?employees?\s+(?:by|per)\s+department.*", query):
        return """SELECT Department, COUNT(*) AS Employee_Count, 
                         AVG(Salary) AS Avg_Salary, SUM(Salary) AS Total_Salary 
                  FROM Employees 
                  GROUP BY Department
                  ORDER BY Department;""", [], False

    # If no simple pattern matches, defer to LLM
    return None, [], True  # True means use LLM

def format_response(query_type, results):
    """Formats SQL query results into readable text."""
    
    if "error" in results:
        return f"Error: {results['error']}"

    # If there's no data found, return an appropriate message
    if not results["data"]:
        return "No records found."

    # Fetch column names dynamically
    column_names = results["columns"]

    response = "Results:\n"
    for row in results["data"]:
        response += "\n".join([f"{col}: {val}" for col, val in zip(column_names, row)])
        response += "\n---\n"
    return response.strip()

def execute_sql(nl_query):
    """Handles SQL query execution and detects ambiguous inputs."""
    
    try:
        print(f"\nProcessing query: {nl_query}")

        sql_query, params, use_llm = detect_query_type(nl_query)

        # If query is too vague, return clarification message instead of executing SQL
        if isinstance(sql_query, str) and "SELECT" not in sql_query:
            return sql_query  

        if use_llm:
            print("Using LLM for complex query...")
            sql_query = generate_llm_sql(nl_query)
            params = []
            query_type = "llm_generated"
        else:
            query_type = "regex_detected"

        print(f"Generated SQL: {sql_query}, Parameters: {params}")

        results = db_manager.execute_query(sql_query, params)
        return format_response(query_type, results)

    except sqlite3.OperationalError as db_error:
        return f"Database Error: {db_error}"

    except Exception as e:
        return f"Unexpected Error: {str(e)}"

def generate_llm_sql(nl_query):
    """Generate SQL using LLM with strict instructions to prevent extra explanations."""
    
    # Reinitialize Llama model each time to avoid context accumulation
    llm = Llama(model_path="qwen2.5-coder-1.5b-instruct-q3_k_m.gguf", n_ctx=512, n_threads=8)

    prompt = f"""You are an AI assistant that strictly converts natural language questions into SQL queries.
    
STRICT RULES:
- ONLY return a valid SQL query. NO explanations, comments, or additional text.
- The query must be 100% executable on SQLite.
- Use ONLY the following database schema:

Database Schema:
- Employees (ID, Name, Department, Salary, Hire_Date)
- Departments (ID, Name, Manager)

EXAMPLES:
User: Show all employees in Sales.
SQL: SELECT * FROM Employees WHERE Department = 'Sales';

User: Who is the manager of the Engineering department?
SQL: SELECT Manager FROM Departments WHERE LOWER(Name) = 'engineering';

User: What is the total salary in Marketing?
SQL: SELECT SUM(Salary) FROM Employees WHERE LOWER(Department) = 'marketing';

Convert the following question into an SQL query.

User: {nl_query}
SQL:"""

    response = llm(
        prompt, 
        max_tokens=150, 
        temperature=0,  # Keep temperature at 0 for strict behavior
        stop=["\n", "User:", "Explanation:", "SQL Query:"]  # Stop unwanted completions
    )
    
    sql_query = response["choices"][0]["text"].strip()

    # Remove formatting if LLM adds unwanted SQL block markers
    sql_query = sql_query.replace("```sql", "").replace("```", "").strip()

    print(f"LLM Generated SQL: {sql_query}")  # Debug log

    return sql_query