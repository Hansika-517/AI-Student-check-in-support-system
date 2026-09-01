"""
action_router.py

Detects what action the student is requesting.

The LLM handles natural-language conversation,
while this Python module identifies specific
application actions.
"""


# =========================================================
# KEYWORDS FOR EACH ACTION
# =========================================================

ACTION_KEYWORDS = {

    "EXTENSION_EMAIL": [
        "extension",
        "professor",
        "prof",
        "email",
        "deadline extension",
        "extra time"
    ],

    "STUDY_PLAN": [
        "study plan",
        "schedule",
        "plan my study",
        "organize my work",
        "what should i study",
        "how should i study"
    ],

    "POMODORO": [
        "pomodoro",
        "timer",
        "focus session",
        "focus for 25",
        "study timer"
    ],

    "DE_ESCALATION": [
        "break",
        "overwhelmed",
        "stressed",
        "can't focus",
        "need to relax",
        "need a reset",
        "take a break"
    ],

    "RESOURCE_ROUTING": [
        "tutor",
        "tutoring",
        "writing center",
        "counselor",
        "counselling",
        "financial aid",
        "advisor",
        "campus resource"
    ]
}


# =========================================================
# ACTION DETECTOR
# =========================================================

def detect_action(message):
    """
    Detect the most relevant application action.

    Parameters
    ----------
    message : str
        Student's message.

    Returns
    -------
    str
        Detected action.
    """

    # Convert message to lowercase so that matching
    # is case-insensitive.
    text = message.lower()


    # Check each action.
    for action, keywords in ACTION_KEYWORDS.items():

        for keyword in keywords:

            if keyword in text:

                return action


    # No special action detected.
    return "CHAT"