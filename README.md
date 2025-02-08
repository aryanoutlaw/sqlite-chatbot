# SQLite Chat Assistant

A natural language interface for querying SQLite databases, built with Streamlit and Gradio. The application allows users to interact with employee and department data using simple English queries.

## Features

- **Natural Language Queries**: Ask questions about employees and departments in plain English
- **Multiple Interface Options**: 
  - Streamlit web interface
  - Gradio interface
- **Database Preview**: View sample data from both Employees and Departments tables
- **Real-time Statistics**: Monitor key metrics about employees and departments
- **Example Queries**: Built-in example queries to help users get started

## Technology Stack

- **Frontend**: 
  - Streamlit
  - Gradio (alternative interface)
- **Backend**:
  - Python
  - SQLite
  - LlamaCPP (Qwen 2.5 Coder model for query processing)
- **Database**: SQLite with two tables (Employees and Departments)

## Installation

1. Clone the repository
2. Install dependencies:
```bash
pip install streamlit gradio llama-cpp-python pandas db-sqlite3
```
3. Download the Qwen model:
   - Required model: `qwen2.5-coder-1.5b-instruct-q3_k_m.gguf`
   - Place it in the root directory

## Usage

### Streamlit Interface
```bash
streamlit run app.py
```

### Gradio Interface
```bash
python gradio_app.py
```

## Example Queries

- "Show employees in Sales"
- "Who is the manager of Engineering?"
- "Employees hired after 2021"
- "Total salary for Marketing"
- "Employees earning more than 70,000"
- "Employees hired between 2019 and 2022"

## Security Features

- SQL injection prevention
- Input validation
- Restricted query types
- Protected database operations

## File Structure

- `app.py`: Streamlit web interface
- `gradio_app.py`: [Gradio interface implementation](https://huggingface.co/spaces/aryanoutlaw/sqlite-chatbot)
- `logic.py`: Query processing and LLM integration
- `database.py`: Database management and operations

## Key Components

### Query Processing
- Uses regex patterns for common queries
- Falls back to LLM for complex queries
- Input validation and security checks

## Known Limitations

1. Query Complexity
   - Limited to single-table queries or simple joins
   - Complex aggregations may not be properly interpreted

2. Natural Language Processing
   - May misinterpret ambiguous questions
   - Limited context awareness across multiple queries

3. Performance Constraints
   - LLM initialization time affects response speed
   - Large result sets may slow down the interface

4. Database Operations
   - Read-only operations supported
   - No support for database modifications

## Suggestions for Improvement

1. Query Processing Enhancements
   - Implement support for complex joins
   - Add handling for subqueries

2. Natural Language Understanding
   - Add context awareness across conversations
   - Implement query suggestion system

3. Performance Optimization
   - Add support for distributed processing
   - Implement better memory management

4. Database Features
   - Add support for data modifications
   - Implement transaction management
