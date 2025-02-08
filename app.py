import streamlit as st

# Must be the first Streamlit command
st.set_page_config(
    page_title="SQLite Chat Assistant",
    layout="wide",
    initial_sidebar_state="collapsed"
)

from logic import execute_sql
from database import DatabaseManager
import pandas as pd

# Initialize database
db_manager = DatabaseManager()
db_manager.init_db()
st.markdown("""
<style>
    /* Further reduce text size in chat messages */
    .stMarkdown p {
        font-size: 0.8rem !important;
        line-height: 1.2 !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* Make metrics more compact */
    .stMetric {
        padding: 0.75rem !important;
    }
    .stMetric div[data-testid="stMetricValue"] {
        font-size: 1.2rem !important;
    }
    .stMetric div[data-testid="stMetricLabel"] {
        font-size: 0.8rem !important;
    }
    
    /* Reduce header sizes more */
    .stMarkdown h1 {
        font-size: 1.6rem !important;
    }
    .stMarkdown h2 {
        font-size: 1.3rem !important;
    }
    .stMarkdown h3 {
        font-size: 1.1rem !important;
    }
    
    /* Make chat messages even more compact */
    .stChatMessage {
        padding: 0.4rem 0.8rem !important;
        margin-bottom: 0.4rem !important;
    }
    
    /* Reduce size of example buttons */
    .stButton button {
        font-size: 0.8rem !important;
        padding: 0.2rem 0.5rem !important;
    }
    
    /* Make dataframes more compact */
    .stDataFrame {
        font-size: 0.8rem !important;
    }
</style>
""", unsafe_allow_html=True)


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
        stats["Employees"] = {
            "Total Employees": total_emp,
            "Unique Departments": total_dept,
            "Average Salary": f"${avg_salary:,.2f}",
            "Hire Date Range": f"{earliest} to {latest}"
        }
    
    # Department stats
    dept_query = "SELECT COUNT(*) FROM Departments"
    dept_result = db_manager.execute_query(dept_query)
    
    if dept_result and dept_result["data"]:
        total_dept = dept_result["data"][0][0]
        stats["Departments"] = {
            "Total Departments": total_dept
        }
    
    return stats

def initialize_session_state():
    """Initialize session state variables"""
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

def main():
    initialize_session_state()

    st.title("SQLite Database Chat Assistant", anchor=False)
    st.markdown("Ask questions about employees and departments in natural language!", help=None)

    # Create tabs
    tab1, tab2, tab3 = st.tabs(["Chat", "Database Preview", "Database Stats"])

    # Chat Tab
    with tab1:
        # Container for chat history
        chat_container = st.container()
        
        # Input container at the bottom
        input_container = st.container()
        
        # Example queries in a small expander
        with st.expander("Example Queries", expanded=False):
            example_queries = [
                "Show employees in Sales",
                "Who is the manager of Engineering?",
                "Employees hired after 2021",
                "Total salary for Marketing",
                "Employees earning more than 70,000",
                "Employees hired between 2019 and 2022"
            ]
            cols = st.columns(2)
            for i, query in enumerate(example_queries):
                col_idx = i % 2
                with cols[col_idx]:
                    if st.button(query, key=f"example_{i}", use_container_width=True):
                        result = execute_sql(query)
                        st.session_state.chat_history.append([query, result])
                        st.rerun()
        
        # Display chat history in the container
        with chat_container:
            for message in st.session_state.chat_history:
                with st.chat_message("user"):
                    st.write(message[0])
                with st.chat_message("assistant"):
                    st.write(message[1])
        
        # Chat input at the bottom
        with input_container:
            user_input = st.chat_input("Ask me about employees or departments...")
            if user_input:
                result = execute_sql(user_input)
                st.session_state.chat_history.append([user_input, result])
                st.rerun()
            
            # Clear history button in a smaller container
            col1, col2, col3 = st.columns([1, 1, 4])
            with col1:
                if st.button("Clear History", use_container_width=True):
                    st.session_state.chat_history = []
                    st.rerun()

    # Database Preview Tab
    with tab2:
        st.header("Database Preview", anchor=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("Employees Table Preview", anchor=False)
            emp_df = get_table_preview("Employees")
            st.dataframe(emp_df, use_container_width=True)
        
        with col2:
            st.subheader("Departments Table Preview", anchor=False)
            dept_df = get_table_preview("Departments")
            st.dataframe(dept_df, use_container_width=True)

    # Database Stats Tab
    with tab3:
        st.header("Database Statistics", anchor=False)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if "Employees" in (stats := get_table_stats()):
                st.subheader("Employee Statistics", anchor=False)
                for key, value in stats["Employees"].items():
                    st.metric(key, value)
        
        with col2:
            if "Departments" in stats:
                st.subheader("Department Statistics", anchor=False)
                for key, value in stats["Departments"].items():
                    st.metric(key, value)
        
        if st.button("Refresh Stats", use_container_width=True):
            st.rerun()

if __name__ == "__main__":
    main()