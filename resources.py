"""
resources.py — Campus Resource Database & Routing
Owner: Rishabh (Resource & Integration Lead)

Purpose:
Maps a student's identified support need(s) to the most relevant campus
resource(s). Two inputs can drive the mapping:

1. Deterministic signals already available from Rishik's pipeline:
   - scoring.py's `identified_flags` (e.g. "Low Sleep", "High Pressure")
   - scoring.py's `support_level` (Low / Medium / High)
   - analytics.py's chronic warnings (e.g. chronic_academic_pressure)

2. Sahithya's AI triage `primary_need` category (once her module exists),
   expected to be one of:
   academic_overload | fatigue | high_stress | skill_gap |
   writing_difficulty | financial_concern

This module works fine with ONLY the deterministic signals (so it's usable
today, before the AI triage engine lands) and gets more precise once
`primary_need` is passed in.

NOTE: Contact details below are PLACEHOLDERS. Replace with your actual
campus resource names/links/hours before the demo.
"""

RESOURCE_DATABASE = {
    "peer_tutoring": {
        "name": "Peer Tutoring Center",
        "description": "Free one-on-one and group tutoring from trained peer tutors across subjects.",
        "contact": "REPLACE — e.g. tutoring.university.edu",
    },
    "writing_center": {
        "name": "Writing Center",
        "description": "Support for essays, papers, and writing assignments at any stage of drafting.",
        "contact": "REPLACE — e.g. writingcenter.university.edu",
    },
    "financial_aid": {
        "name": "Financial Aid Office",
        "description": "Guidance on emergency funds, scholarships, payment plans, and financial hardship.",
        "contact": "REPLACE — e.g. financialaid.university.edu",
    },
    "faculty_advisor": {
        "name": "Faculty / Academic Advisor",
        "description": "Help with course load decisions, deadline extensions, and academic planning.",
        "contact": "REPLACE — e.g. your assigned advisor's office hours",
    },
    "counseling": {
        "name": "Counseling & Psychological Services",
        "description": "Confidential support for stress, anxiety, and general well-being — same-day slots often available.",
        "contact": "REPLACE — e.g. counseling.university.edu",
    },
    "student_life": {
        "name": "Student Life / Wellness Programs",
        "description": "Workshops, drop-in wellness activities, and community support for balance and rest.",
        "contact": "REPLACE — e.g. studentlife.university.edu",
    },
}

# Maps a flag string (as produced by scoring.py) to relevant resource keys.
_FLAG_TO_RESOURCES = {
    "Low Sleep": ["student_life", "counseling"],
    "High Pressure": ["counseling", "faculty_advisor"],
    "High Workload/Deadlines": ["faculty_advisor", "peer_tutoring"],
    "Low Energy": ["student_life"],
}

# Maps a chronic/trend warning (from analytics.py) to resource keys.
_CHRONIC_WARNING_TO_RESOURCES = {
    "chronic_academic_pressure": ["counseling", "faculty_advisor"],
    "chronic_sleep_deprivation": ["counseling", "student_life"],
}

# Maps an AI-identified primary need (from Sahithya's triage engine, once
# built) to resource keys. Keys here are the agreed vocabulary from the
# team plan — confirm these exact strings with Sahithya before integrating.
_PRIMARY_NEED_TO_RESOURCES = {
    "academic_overload": ["faculty_advisor", "peer_tutoring"],
    "fatigue": ["student_life", "counseling"],
    "high_stress": ["counseling"],
    "skill_gap": ["peer_tutoring"],
    "writing_difficulty": ["writing_center"],
    "financial_concern": ["financial_aid"],
}


def map_resources(
    flags: list | None = None,
    support_level: str | None = None,
    chronic_warnings: dict | None = None,
    primary_need: str | None = None,
) -> list[dict]:
    """
    Resolves a student's signals into a deduplicated, ordered list of
    resource dicts to display/route to.

    Args:
        flags: e.g. score_data['identified_flags'] from scoring.py
        support_level: e.g. score_data['support_level'] ('Low'/'Medium'/'High')
        chronic_warnings: e.g. trend_data['warnings'] from analytics.py
            (only keys with a truthy value are used)
        primary_need: optional category string from the AI triage engine

    Returns:
        list of resource dicts, in relevance order, each shaped like
        RESOURCE_DATABASE's values (with a 'key' field added).
    """
    resource_keys: list[str] = []

    # Highest-precision signal first: AI-identified primary need.
    if primary_need:
        for key in _PRIMARY_NEED_TO_RESOURCES.get(primary_need, []):
            _append_unique(resource_keys, key)

    # Deterministic flags from scoring.py.
    for flag in flags or []:
        for key in _FLAG_TO_RESOURCES.get(flag, []):
            _append_unique(resource_keys, key)

    # Chronic/trend warnings from analytics.py.
    for warning_name, is_active in (chronic_warnings or {}).items():
        if is_active:
            for key in _CHRONIC_WARNING_TO_RESOURCES.get(warning_name, []):
                _append_unique(resource_keys, key)

    # If support level is High and nothing has routed to counseling yet,
    # make sure counseling is included — a high overall need should always
    # surface a human-support option even if individual flags didn't.
    if support_level == "High":
        _append_unique(resource_keys, "counseling")

    # Fallback: if nothing matched at all (e.g. Low support level, no
    # flags), point toward student life as a general, low-friction option.
    if not resource_keys:
        _append_unique(resource_keys, "student_life")

    return [
        {"key": key, **RESOURCE_DATABASE[key]}
        for key in resource_keys
        if key in RESOURCE_DATABASE
    ]


def _append_unique(items: list, value) -> None:
    if value not in items:
        items.append(value)


# Manual smoke tests
if __name__ == "__main__":
    print("-- High-need demo flow --")
    result = map_resources(
        flags=["Low Sleep", "High Pressure", "High Workload/Deadlines", "Low Energy"],
        support_level="High",
        chronic_warnings={"chronic_academic_pressure": False, "chronic_sleep_deprivation": False},
    )
    for r in result:
        print(r["key"], "-", r["name"])

    print("\n-- Low-need, no flags --")
    print([r["key"] for r in map_resources(flags=[], support_level="Low")])

    print("\n-- AI primary_need = writing_difficulty --")
    print([r["key"] for r in map_resources(primary_need="writing_difficulty")])
