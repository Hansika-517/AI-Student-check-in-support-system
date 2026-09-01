# ⚓ Harbor — AI Student Check-in & Support System
> A minimal, intelligent student check-in, workload triage, and wellbeing support platform built with Python, Streamlit, Pandas, Plotly, and Groq LLM.

---

## 📋 Table of Contents
1. [Project Overview](#-project-overview)
2. [Prerequisites](#-prerequisites)
3. [Installation & Setup](#-installation--setup)
4. [Database Initialization](#-database-initialization)
5. [Running the Application](#-running-the-application)
6. [API Configuration (Optional)](#-api-configuration-optional)
7. [Running Tests](#-running-tests)
8. [Project Directory Structure](#-project-directory-structure)

---

## 📌 Project Overview
Harbor provides proactive, empathetic academic and emotional support for students. Key capabilities include:
- **Morning Alignment Check-in**: Rest deficit & intention tracking.
- **Support Network & Helplines**: 24/7 crisis support text/calls and peer tutor connections.
- **Unified Harmony AI Chat & Contextual Deck**: Intelligent conversational support and interactive deep work/rest timers.
- **Analytics & Insights**: Historical trend tracking (sleep, academic pressure, energy levels).
- **Logbook & Resources**: Activity history and academic/wellbeing resource navigation.

---

## 🛠️ Prerequisites
Ensure you have the following installed on your machine:
- **Python**: `3.9` or higher
- **pip**: Package manager for Python
- **Git**: For source control

---

## 🚀 Installation & Setup

### Step 1: Clone or Navigate to the Workspace
```bash
cd /path/to/AI-Student-check-in-support-system
```

### Step 2: Create and Activate a Virtual Environment (Recommended)
```bash
# macOS / Linux
python3 -m venv venv
source venv/bin/activate

# Windows (Command Prompt)
python -m venv venv
venv\Scripts\activate
```

### Step 3: Install Required Dependencies
Install the required Python packages:
```bash
pip install streamlit pandas plotly groq
```

*Note: `sqlite3`, `datetime`, `random`, `time`, and `base64` are part of Python's standard library and do not require separate installation.*

---

## 🗄️ Database Initialization

Initialize the SQLite database (`student_support.db`) and seed it with historical student check-in data:

```bash
# 1. Initialize the SQLite database schema
python3 database.py

# 2. Seed historical check-ins from dataset.csv
python3 -c "
import sqlite3, pandas as pd
from database import init_db, DB_NAME

init_db()
df = pd.read_csv('dataset.csv')
conn = sqlite3.connect(DB_NAME)
for _, row in df.iterrows():
    conn.execute('''
        INSERT OR REPLACE INTO check_ins (id, student_id, timestamp, sleep_hours, mood_score, energy_level, workload_level, academic_pressure, deadlines_count, optional_message)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (int(row['id']), str(row['student_id']), str(row['timestamp']), float(row['sleep_hours']), int(row['mood_score']), int(row['energy_level']), int(row['workload_level']), int(row['academic_pressure']), int(row['deadlines_count']), str(row['optional_message'])))
conn.commit()
conn.close()
print('Database successfully initialized and seeded.')
"
```

---

## 🏃 Running the Application

Launch the Streamlit web application:

```bash
streamlit run app.py
```

Once executed, the application will automatically open in your default browser at:
`http://localhost:8501`

---

## ⚙️ API Configuration (Optional)

Harbor includes fallback mock responses for offline operation. To enable live AI support using Groq LLM:

1. Obtain an API key from [Groq Console](https://console.groq.com/).
2. Set your API key as an environment variable or place it in `GROQ_API.key`:

```bash
# Set environment variable (macOS/Linux)
export GROQ_API_KEY="your_groq_api_key_here"

# Windows (Command Prompt)
set GROQ_API_KEY="your_groq_api_key_here"
```

Or save your key directly in `GROQ_API.key` in the root directory.

---

## 🧪 Running Tests & Verification

### Verify Python Syntax
To verify syntax across the codebase:
```bash
python3 -m py_compile app.py database.py analytics.py scoring.py planner.py chatbot.py
```

### Run Integration Tests
To execute backend integration tests:
```bash
python3 test_integration.py
```

---

## 📂 Project Directory Structure

```text
AI-Student-check-in-support-system/
├── app.py                      # Main Streamlit web application & UI renderers
├── database.py                 # SQLite database schema initialization (student_support.db)
├── analytics.py                # Student trend analysis & pattern detection
├── scoring.py                  # Support score & risk calculation logic
├── planner.py                  # Workload triage & action plan generation
├── chatbot.py                  # Groq LLM chat integration with safety fallback
├── safety.py                   # Crisis detection & safety concern filters
├── action_router.py            # User action intent router
├── resource_router.py          # Academic & wellbeing resource routing
├── integration.py              # End-to-end data pipeline runner
├── dataset.csv                 # Historical student check-in dataset (CSV)
├── dataset.json                # Historical student check-in dataset (JSON)
├── logo.png                    # Custom application logo asset
├── GROQ_API.key                # Groq API key configuration file
├── setup.md                    # Setup and installation instructions
└── student_support.db          # SQLite database storage file
```
