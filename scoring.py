def calculate_support_score(check_in_data):
    """
    Calculates a prototype support score based on check-in metrics.
    Higher score = Higher need for intervention.
    """
    score = 0
    flags = []

    # 1. Low Sleep Signal
    if check_in_data['sleep_hours'] < 5.0:
        score += 3
        flags.append("Low Sleep")

    # 2. High Academic Pressure Signal
    if check_in_data['academic_pressure'] >= 8:
        score += 3
        flags.append("High Pressure")

    # 3. High Workload & Deadlines Signal
    if check_in_data['workload_level'] >= 8 or check_in_data['deadlines_count'] >= 3:
        score += 2
        flags.append("High Workload/Deadlines")

    # 4. Low Energy Signal
    if check_in_data['energy_level'] <= 3:
        score += 2
        flags.append("Low Energy")

    # Determine Support Level
    support_level = "Low"
    if score >= 7:
        support_level = "High"
    elif score >= 4:
        support_level = "Medium"

    return {
        "total_score": score,
        "support_level": support_level,
        "identified_flags": flags
    }

# Quick test based on the "Killer Demo Flow"
demo_data = {
    'sleep_hours': 4.5,
    'academic_pressure': 9,
    'energy_level': 3,
    'workload_level': 9,
    'deadlines_count': 3
}

print(calculate_support_score(demo_data))