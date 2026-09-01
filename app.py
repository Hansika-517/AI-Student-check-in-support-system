"""
app.py

Main integration file for the AI Student Check-in & Support System.

Connects:
    Rishik's backend planner
            ↓
       AI context
            ↓
      Action Router
            ↓
     Support Features
            ↓
        Groq Chatbot
"""


# =========================================================
# IMPORTS
# =========================================================

from planner import build_ai_context_payload
from chatbot import StudentSupportChatbot
from action_router import detect_action
from resource_router import route_resource


# =========================================================
# DEMO STUDENT DATA
# =========================================================

STUDENT_ID = "student_001"

CURRENT_CHECK_IN = {
    "sleep_hours": 4.5,
    "academic_pressure": 9,
    "energy_level": 3,
    "workload_level": 9,
    "deadlines_count": 3
}

TASKS = [
    {
        "name": "DBMS Assignment",
        "days_until_due": 1,
        "estimated_hours": 2
    },
    {
        "name": "Python Project",
        "days_until_due": 2,
        "estimated_hours": 4
    },
    {
        "name": "Math Revision",
        "days_until_due": 4,
        "estimated_hours": 3
    }
]

AVAILABLE_HOURS = 4


# =========================================================
# BUILD AI CONTEXT
# =========================================================

def build_student_context():
    """
    Get the student's existing context from Rishik's backend.

    We do not modify the backend.
    """

    return build_ai_context_payload(
        STUDENT_ID,
        CURRENT_CHECK_IN,
        TASKS,
        AVAILABLE_HOURS
    )


# =========================================================
# DISPLAY RESOURCE
# =========================================================

def display_resource(
    support_level,
    identified_flags,
    message
):
    """
    Find and display the most relevant campus resource.
    """

    resource = route_resource(
        support_level,
        identified_flags,
        message
    )

    print("\nRecommended Resource:")
    print(resource["name"])

    print("\nWhy:")
    print(resource["reason"])


# =========================================================
# MAIN APPLICATION
# =========================================================

def main():

    print("\n" + "=" * 60)
    print("      AI STUDENT CHECK-IN & SUPPORT SYSTEM")
    print("=" * 60)


    # -----------------------------------------------------
    # STEP 1: Get backend-generated student context
    # -----------------------------------------------------

    print("\nLoading student support context...")

    system_data = build_student_context()

    ai_context = system_data["ai_prompt_context"]


    # -----------------------------------------------------
    # STEP 2: Extract useful backend information
    # -----------------------------------------------------

    # These values are already produced by the backend.
    # We use them for resource routing and AI context.

    support_level = "High"
    
    identified_flags = [
        "Low Sleep",
        "High Pressure",
        "High Workload/Deadlines",
        "Low Energy"
    ]


    # -----------------------------------------------------
    # STEP 3: Create chatbot
    # -----------------------------------------------------

    chatbot = StudentSupportChatbot(ai_context)


    print("\nSystem ready!")
    print("Type 'exit' to end the session.")


    # =====================================================
    # CHAT LOOP
    # =====================================================

    while True:

        print("\n" + "-" * 60)

        student_message = input("Student: ").strip()


        # -------------------------------------------------
        # Exit
        # -------------------------------------------------

        if student_message.lower() == "exit":

            print("\nSession ended.")
            break


        if not student_message:

            print("Please enter a message.")

            continue


        # -------------------------------------------------
        # ACTION DETECTION
        # -------------------------------------------------

        action = detect_action(student_message)


        print("\nDetected Action:")
        print(action)


        # -------------------------------------------------
        # RESOURCE ROUTING
        # -------------------------------------------------

        if action == "RESOURCE_ROUTING":

            display_resource(
                support_level,
                identified_flags,
                student_message
            )


        # -------------------------------------------------
        # POMODORO
        # -------------------------------------------------

        elif action == "POMODORO":

            print("\nPomodoro Recommendation:")
            print(
                "Focus for 25 minutes, then take a "
                "5-minute break."
            )


        # -------------------------------------------------
        # DE-ESCALATION
        # -------------------------------------------------

        elif action == "DE_ESCALATION":

            print("\nImmediate Support:")
            print(
                "Take a short 5-10 minute walk, stretch, "
                "or try slow breathing before starting "
                "your next task."
            )


        # -------------------------------------------------
        # STUDY PLAN
        # -------------------------------------------------

        elif action == "STUDY_PLAN":

            print("\nStudy Planning:")
            print(
                "Your backend recommends using Pomodoro "
                "to divide the available study time into "
                "focused work sessions."
            )


        # -------------------------------------------------
        # EXTENSION EMAIL
        # -------------------------------------------------

        elif action == "EXTENSION_EMAIL":

            print("\nExtension Support:")
            print(
                "I can help you create a professional "
                "extension request for your professor."
            )


        # -------------------------------------------------
        # SEND MESSAGE TO AI
        # -------------------------------------------------

        print("\nAI:")

        response = chatbot.get_response(
            student_message
        )

        print(response)


# =========================================================
# PROGRAM ENTRY POINT
# =========================================================

if __name__ == "__main__":
    main()