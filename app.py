import gradio as gr
from logic import execute_sql
from database import DatabaseManager
import pandas as pd

# Initialize database
db_manager = DatabaseManager()
db_manager.init_db()

def get_table_preview(table_name):
    """Get a preview of the specified table"""
    query = f"SELECT * FROM {table_name} LIMIT 5"
    result = db_manager.execute_query(query)
    if result and "data" in result:
        return pd.DataFrame(result["data"], columns=result["columns"])
    return pd.DataFrame()

def get_table_stats():
    """Get basic statistics about the tables"""
    stats = {}
    
    # Employee stats
    emp_query = """
    SELECT 
        COUNT(*) as total_employees,
        COUNT(DISTINCT Department) as total_departments,
        AVG(Salary) as avg_salary,
        MIN(Hire_Date) as earliest_hire,
        MAX(Hire_Date) as latest_hire
    FROM Employees
    """
    emp_result = db_manager.execute_query(emp_query)
    
    if emp_result and emp_result["data"]:
        total_emp, total_dept, avg_salary, earliest, latest = emp_result["data"][0]
        stats["Employees"] = f"""
Total Employees: {total_emp}
Unique Departments: {total_dept}
Average Salary: ${avg_salary:,.2f}
Hire Date Range: {earliest} to {latest}
"""
    
    # Department stats
    dept_query = "SELECT COUNT(*) FROM Departments"
    dept_result = db_manager.execute_query(dept_query)
    
    if dept_result and dept_result["data"]:
        total_dept = dept_result["data"][0][0]
        stats["Departments"] = f"Total Departments: {total_dept}"
    
    return "\n\n".join(f"{k}:\n{v}" for k, v in stats.items())

def process_query(message, history):
    """Process user query and return updated history and empty message"""
    if not message.strip():
        return history, ""
    
    result = execute_sql(message)
    history.append([message, str(result)])
    return history, ""

# Define the Gradio interface with tabs
with gr.Blocks(title="SQLite Chat Assistant") as demo:
    gr.Markdown("# SQLite Database Chat Assistant")
    gr.Markdown("Ask questions about employees and departments in natural language!")
    
    with gr.Tabs():
        # Chat Interface Tab
        with gr.Tab("Chat"):
            chatbot = gr.Chatbot(
                value=[],
                height=400,
                label="Conversation History"
            )
            msg = gr.Textbox(
                placeholder="Ask me about employees or departments...",
                label="Your Question",
                scale=8
            )
            with gr.Row():
                submit = gr.Button("Submit")
                clear = gr.Button("Clear History")
            
            # Example queries
            gr.Examples(
                examples=[
                    ["Show employees in Sales"],
                    ["Who is the manager of Engineering?"],
                    ["Employees hired after 2021"],
                    ["Total salary for Marketing"],
                    ["Employees earning more than 70,000"],
                    ["Employees hired between 2019 and 2022"]
                ],
                inputs=msg,
                label="Example Queries"
            )
            
            # Set up chat functionality
            submit.click(
                process_query,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            msg.submit(
                process_query,
                inputs=[msg, chatbot],
                outputs=[chatbot, msg]
            )
            
            clear.click(lambda: ([], ""), outputs=[chatbot, msg])
        
        # Database Preview Tab
        with gr.Tab("Database Preview"):
            gr.Markdown("### Employees Table Preview")
            emp_preview = gr.DataFrame(get_table_preview("Employees"))
            
            gr.Markdown("### Departments Table Preview")
            dept_preview = gr.DataFrame(get_table_preview("Departments"))
        
        # Database Stats Tab
        with gr.Tab("Database Stats"):
            gr.Markdown("### Database Statistics")
            stats_text = gr.TextArea(
                value=get_table_stats(),
                label="Current Statistics",
                interactive=False
            )
            refresh_stats = gr.Button("Refresh Stats")
            refresh_stats.click(get_table_stats, outputs=stats_text)

if __name__ == "__main__":
    demo.launch()