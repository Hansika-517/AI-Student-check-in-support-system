"""
extension_generator.py

Generates a professional extension request email
using information provided by the student.

The student can provide:
- Professor name
- Course name
- Assignment/exam
- Current deadline
- Requested extension
- Optional reason
"""


import json

from groq import Groq

import os
from dotenv import load_dotenv


# =========================================================
# LOAD ENVIRONMENT VARIABLES
# =========================================================

load_dotenv()

API_KEY = os.getenv("GROQ_API_KEY")


if not API_KEY:
    raise ValueError("GROQ_API_KEY not found.")


# =========================================================
# GROQ CLIENT
# =========================================================

client = Groq(api_key=API_KEY)

MODEL_NAME = "openai/gpt-oss-120b"


# =========================================================
# EMAIL GENERATOR
# =========================================================

def generate_extension_email(
    professor_name,
    course_name,
    assignment,
    current_deadline,
    requested_extension,
    reason
):
    """
    Generate a professional extension request email.

    Parameters
    ----------
    professor_name : str
        Name of the professor.

    course_name : str
        Course/subject name.

    assignment : str
        Assignment, project, or exam.

    current_deadline : str
        Current due date.

    requested_extension : str
        Extension being requested.

    reason : str
        Student's reason for requesting the extension.

    Returns
    -------
    dict
        Generated email details.
    """


    # =====================================================
    # PROMPT
    # =====================================================

    prompt = f"""
Write a professional and polite academic extension
request email.

Student details:

Professor: {professor_name}
Course: {course_name}
Assignment/Assessment: {assignment}
Current Deadline: {current_deadline}
Requested Extension: {requested_extension}
Reason: {reason}

Requirements:

1. Be respectful and professional.
2. Do not exaggerate the situation.
3. Clearly mention the assignment.
4. Mention the current deadline.
5. Clearly state the requested extension.
6. Briefly explain the reason.
7. Acknowledge that the professor may decline.
8. Do not make medical claims.
9. Keep the email concise.
10. Include a suitable subject line.

Return ONLY valid JSON:

{{
    "subject": "...",
    "email": "..."
}}
"""


    # =====================================================
    # CALL GROQ
    # =====================================================

    try:

        response = client.chat.completions.create(

            model=MODEL_NAME,

            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are an academic communication "
                        "assistant. Write respectful and "
                        "professional emails."
                    )
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],

            temperature=0.3
        )


        # =================================================
        # GET MODEL RESPONSE
        # =================================================

        raw_response = (
            response
            .choices[0]
            .message
            .content
            .strip()
        )


        # =================================================
        # PARSE JSON
        # =================================================

        try:

            result = json.loads(raw_response)

        except json.JSONDecodeError:

            cleaned_response = (
                raw_response
                .replace("```json", "")
                .replace("```", "")
                .strip()
            )

            result = json.loads(cleaned_response)


        return result


    except Exception as error:

        return {
            "error": str(error)
        }