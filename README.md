# Code Review Feedback Generator

## Project Overview

The Code Review Feedback Generator is an AI-powered web application that automatically reviews source code and provides detailed feedback. The application analyzes code quality, identifies issues, suggests improvements, and generates a summary using Large Language Models (LLMs).

This project is built using Python, Streamlit, LangChain, Groq LLM, Pydantic, and Langfuse.

---

## Features

* Automated code review using AI
* Detects coding issues and vulnerabilities
* Provides improvement suggestions
* Assigns code quality ratings
* Generates review summaries
* Interactive web interface using Streamlit
* Structured JSON output validation using Pydantic
* Langfuse integration for observability and tracing

---

## Technologies Used

* Python
* Streamlit
* LangChain
* Groq LLM
* Pydantic
* Langfuse
* Python Dotenv

---

## Project Structure

```text
Code-Review-Feedback-Generator/
│
├── main.py
├── .env
├── requirements.txt
├── README.md
└── screenshots/
```

---

## Installation

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd Code-Review-Feedback-Generator
```

### Step 2: Create Virtual Environment

```bash
python -m venv venv
```

Activate the environment:

#### Windows

```bash
venv\Scripts\activate
```

#### Linux / Mac

```bash
source venv/bin/activate
```

---

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

---

## Environment Configuration

Create a `.env` file in the project root directory.

```env
GROQ_API_KEY=your_groq_api_key
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
LANGFUSE_HOST=https://cloud.langfuse.com
```

---

## Running the Application

Start the Streamlit application:

```bash
streamlit run main.py
```

The application will open in your browser.

---

## How It Works

1. User enters source code.
2. Streamlit captures the input.
3. LangChain creates a prompt.
4. Groq LLM analyzes the code.
5. AI generates a JSON response.
6. Pydantic validates the response.
7. Results are displayed to the user.

---

## Workflow

```text
User
  │
  ▼
Streamlit Interface
  │
  ▼
LangChain Prompt
  │
  ▼
Groq LLM
  │
  ▼
JSON Response
  │
  ▼
Pydantic Validation
  │
  ▼
Results Display
```

---

## Sample Input

```python
def get_data(q):
    import sqlite3
    conn = sqlite3.connect("db.sqlite")
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM users WHERE name='" + q + "'"
    )
    return cur.fetchall()
```

---

## Sample Output

### Identified Issues

* SQL Injection vulnerability
* Unsafe query construction

### Improvement Suggestions

* Use parameterized queries
* Validate user input

### Code Quality Level

```text
Critical
```

### Review Summary

The code is vulnerable to SQL Injection due to direct string concatenation while building database queries.

---

## Quality Levels

The application categorizes code into five quality levels:

* Excellent
* Good
* Moderate
* Low
* Critical

---

## Advantages

* Saves review time
* Improves code quality
* Detects vulnerabilities
* Provides instant feedback
* Easy to use
* Scalable solution

---

## Future Enhancements

* Support for multiple programming languages
* GitHub integration
* PDF report generation
* CI/CD pipeline integration
* Team collaboration features
* Advanced security analysis

---

## Challenges Faced

* Langfuse integration compatibility issues
* Groq model deprecation updates
* Prompt engineering improvements
* JSON output validation handling

---

## Conclusion

The Code Review Feedback Generator provides an efficient and intelligent way to automate code reviews. By leveraging AI-powered analysis, the system helps developers improve code quality, identify vulnerabilities, and follow best coding practices.

---

## Author

**Name:** [Your Name]

**Organization:** Innomatics Research Labs

**Project:** Code Review Feedback Generator

**Technology Stack:** Python, Streamlit, LangChain, Groq LLM, Pydantic, Langfuse
