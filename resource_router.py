"""
resource_router.py

Routes a student to the most appropriate campus resource.

The student's current message is the primary signal.
Backend flags provide additional context.
"""


# =========================================================
# RESOURCE DATABASE
# =========================================================

RESOURCES = {

    "faculty_advisor": {
        "name": "Faculty Advisor",
        "reason": (
            "Useful when academic workload, deadlines, "
            "or course-related difficulties are becoming "
            "difficult to manage."
        )
    },

    "peer_tutoring": {
        "name": "Peer Tutoring",
        "reason": (
            "Useful when the student needs help "
            "understanding course material or completing "
            "academic work."
        )
    },

    "writing_center": {
        "name": "Writing Center",
        "reason": (
            "Useful for help with reports, essays, "
            "documentation, and academic writing."
        )
    },

    "counseling_services": {
        "name": "Counseling Services",
        "reason": (
            "Useful when a student would benefit from "
            "speaking with a trained professional about "
            "their well-being or emotional difficulties."
        )
    },

    "financial_aid": {
        "name": "Financial Aid Office",
        "reason": (
            "Useful for questions related to fees, "
            "scholarships, or financial assistance."
        )
    },

    "student_life": {
        "name": "Student Life / Student Support",
        "reason": (
            "Useful for general campus support, student "
            "activities, and non-academic assistance."
        )
    }
}


# =========================================================
# ROUTING FUNCTION
# =========================================================

def route_resource(
    support_level,
    identified_flags,
    student_message=""
):
    """
    Select the most appropriate campus resource.

    Priority:

    1. Well-being
    2. Financial support
    3. Tutoring
    4. Writing support
    5. Academic/faculty support
    6. General student support
    """

    # -----------------------------------------------------
    # Normalize the message
    # -----------------------------------------------------

    message = student_message.lower().strip()


    # -----------------------------------------------------
    # Normalize backend flags
    # -----------------------------------------------------

    flags = [
        str(flag).lower().strip()
        for flag in identified_flags
    ]


    # =====================================================
    # 1. WELL-BEING / EMOTIONAL SUPPORT
    # =====================================================

    wellbeing_phrases = [

        "overwhelmed",
        "stressed",
        "stress",
        "anxious",
        "anxiety",
        "burned out",
        "burnt out",
        "feeling low",
        "feeling very low",
        "emotionally",
        "can't cope",
        "cannot cope",
        "need emotional support",
        "mental health"
    ]

    if any(
        phrase in message
        for phrase in wellbeing_phrases
    ):

        return RESOURCES["counseling_services"]


    # =====================================================
    # 2. FINANCIAL SUPPORT
    # =====================================================

    financial_phrases = [

        "financial aid",
        "scholarship",
        "scholarships",
        "college fees",
        "college fee",
        "tuition",
        "pay my fees",
        "paying my fees",
        "money problems",
        "financial problem"
    ]

    if any(
        phrase in message
        for phrase in financial_phrases
    ):

        return RESOURCES["financial_aid"]


    # =====================================================
    # 3. PEER TUTORING
    # =====================================================

    tutoring_phrases = [

        "tutor",
        "tutoring",
        "don't understand",
        "dont understand",
        "can't understand",
        "cannot understand",
        "help with subject",
        "help me understand",
        "understand my subject"
    ]

    if any(
        phrase in message
        for phrase in tutoring_phrases
    ):

        return RESOURCES["peer_tutoring"]


    # =====================================================
    # 4. WRITING CENTER
    # =====================================================

    writing_phrases = [

        "writing",
        "report",
        "essay",
        "documentation",
        "academic writing",
        "write my assignment"
    ]

    if any(
        phrase in message
        for phrase in writing_phrases
    ):

        return RESOURCES["writing_center"]


    # =====================================================
    # 5. FACULTY ADVISOR
    # =====================================================

    academic_phrases = [

        "academic workload",
        "too much work",
        "too many assignments",
        "too many deadlines",
        "deadline",
        "professor",
        "course problem",
        "academic problem",
        "extension",
        "assignment deadline"
    ]

    if any(
        phrase in message
        for phrase in academic_phrases
    ):

        return RESOURCES["faculty_advisor"]


    # =====================================================
    # 6. USE BACKEND FLAGS AS SUPPORTING CONTEXT
    # =====================================================

    # Only recommend a faculty advisor when the student's
    # message actually talks about academic work.

    academic_context_words = [

        "assignment",
        "assignments",
        "study",
        "exam",
        "exams",
        "course",
        "subject",
        "workload",
        "deadline",
        "academic"
    ]

    has_academic_context = any(
        word in message
        for word in academic_context_words
    )


    if (
        "high workload/deadlines" in flags
        and has_academic_context
    ):

        return RESOURCES["faculty_advisor"]


    # =====================================================
    # 7. DEFAULT
    # =====================================================

    return RESOURCES["student_life"]