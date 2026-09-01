# 🛠️ Data, Scoring & Logic Module: Integration Handoff

## 📌 Overview
This document outlines the backend data and logic modules I have completed for the AI Student Check-in & Support System. It serves as a guide for how to connect these foundational modules to the frontend UI, the AI triage engine, and the overall integration routing. 

### Files Delivered
*   `database.py`: Handles the SQLite database initialization and stores student check-in metrics (sleep, pressure, energy, etc.).
*   `scoring.py`: Calculates a deterministic prototype support score (High/Medium/Low) using signals like low sleep, high workload, and multiple deadlines.
*   `analytics.py`: Uses Pandas to calculate historical trends and detect patterns (e.g., worsening sleep, chronic academic pressure) over a 5-day window.
*   `planner.py`: Prioritizes tasks by urgency and generates a time-management plan, adapting the recommendation (Pomodoro vs. Time-Blocking) based on the student's current energy levels.

---

## 🤝 Integration Guide by Team Member

### 1. Rishabh (Resource & Integration Lead)
**Your Goal:** Route the data seamlessly between my backend, Hansika's frontend, and Sahithya's AI engine. 

**How to use my code:** 
You only need to import the master bridge function. This function executes all four of my modules and packages the output into a single dictionary.

```python
# Import the bridge function
from planner import build_ai_context_payload

# Execute the function using the current check-in data and tasks
system_data = build_ai_context_payload(
    student_id="student_001", 
    current_check_in=current_data, 
    tasks=current_tasks, 
    available_hours=4
)

# 1. Route this dict to Hansika for the Streamlit UI
ui_data = system_data["raw_data"] 

# 2. Route this string to Sahithya for the LLM prompt
ai_context = system_data["ai_prompt_context"]

### 2. Hansika (Frontend & UX Lead)

**Your Goal:** Populate the Streamlit dashboard, action-plan cards, trend charts, and status indicators[cite: 1].

**How to use my data:**  
Rishabh will pass you the `ui_data` dictionary (which maps to `system_data["raw_data"]`). You can extract the exact values you need for your visual polish without writing any calculation logic:
*   **Status Indicator:** Render the `ui_data['score']['support_level']` (e.g., High, Medium, Low).
*   **Trend Charts:** Parse `ui_data['trends']['trends']` to build the charts showing sleep and energy changes.
*   **Action Plan Cards:** Loop through `ui_data['plan']['action_plan']` to display the prioritized tasks and the specific recommended study technique.

---

### 3. Sahithya (AI & Chatbot Lead)

**Your Goal:** Build the AI Triage engine and the context-aware chatbot[cite: 1].

**How to use my data:**  
Rishabh will pass you the `ai_context` string (which maps to `system_data["ai_prompt_context"]`).
*   **System Prompt:** Inject this exact string directly into your Groq/LLM system prompt so the chatbot remembers the check-in context[cite: 1].
*   **Triage Explanation:** You do not need to ask the AI to guess the support level. My context block explicitly provides the deterministic Primary Support Level and Identified Risk Flags for your AI to explain[cite: 1].
*   **Extension Automation:** My time-management logic calculates if the student's workload mathematically exceeds their available time. If the string says `Extension Draft Needed: True`, your chatbot should immediately offer to draft a professional extension email[cite: 1].