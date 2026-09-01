def generate_study_plan(tasks, available_hours, energy_level):
    """
    Prioritizes academic tasks and generates a structured daily action plan.
    Adapts the time-management recommendation based on the student's energy level.
    """
    # 1. Prioritize Tasks: Calculate a simple urgency-weight
    for task in tasks:
        # Prevent division by zero; fewer days = higher urgency
        urgency = 1 / (task['days_until_due'] + 0.1) 
        task['priority_score'] = urgency * task['estimated_hours']

    # Sort tasks by priority score descending
    prioritized_tasks = sorted(tasks, key=lambda x: x['priority_score'], reverse=True)

    # 2. Select Time Management Strategy
    if energy_level <= 4:
        strategy = "Pomodoro (25 min work / 5 min break)"
        advice = "Energy is low. Focus on short, manageable bursts to avoid burnout."
    else:
        strategy = "Time-Blocking (90 min deep work / 15 min break)"
        advice = "Energy is solid. Use deep work blocks to tackle complex assignments."

    # 3. Create the Action Plan
    plan = []
    hours_allocated = 0

    for task in prioritized_tasks:
        if hours_allocated >= available_hours:
            break
        
        allocated_time = min(task['estimated_hours'], available_hours - hours_allocated)
        hours_allocated += allocated_time
        
        plan.append({
            "task_name": task['name'],
            "allocated_hours": allocated_time,
            "technique": strategy
        })

    # Calculate if they are overallocated
    total_needed = sum(t['estimated_hours'] for t in tasks)
    unallocated = total_needed - hours_allocated

    return {
        "strategy_recommended": strategy,
        "rationale": advice,
        "action_plan": plan,
        "unallocated_hours": unallocated,
        "needs_extension": unallocated > 0  # Flag for AI to suggest an extension email
    }

# Import your modules
from scoring import calculate_support_score
from analytics import get_student_trends
from planner import generate_study_plan

def build_ai_context_payload(student_id, current_check_in, tasks, available_hours):
    """
    Aggregates all deterministic backend data into a single structured payload 
    for the AI Triage Engine and Chatbot.
    """
    # 1. Process current check-in data
    score_data = calculate_support_score(current_check_in)
    
    # 2. Fetch historical trends
    trend_data = get_student_trends(student_id, days=5)
    
    # 3. Generate time-management plan
    plan_data = generate_study_plan(tasks, available_hours, current_check_in['energy_level'])
    
    # 4. Construct the AI System Prompt Context
    ai_context = f"""
    [SYSTEM CONTEXT - DO NOT EXPOSE TO USER]
    Student Status Overview:
    - Primary Support Level: {score_data['support_level']}
    - Identified Risk Flags: {', '.join(score_data['identified_flags']) if score_data['identified_flags'] else 'None'}
    
    Historical Trends (Last 5 Days):
    - Chronic Pressure: {trend_data.get('warnings', {}).get('chronic_academic_pressure', False)}
    - Worsening Sleep: {trend_data.get('warnings', {}).get('worsening_sleep', False)}
    
    Action Plan & Time Management:
    - Recommended Strategy: {plan_data['strategy_recommended']}
    - Unallocated Workload: {plan_data['unallocated_hours']} hours
    - Extension Draft Needed: {plan_data['needs_extension']}
    
    Instructions for AI:
    Use this context to guide the conversation. If 'Extension Draft Needed' is True, proactively offer to help the student draft a professional extension email to their professor.
    """
    
    return {
        "raw_data": {
            "score": score_data,
            "trends": trend_data,
            "plan": plan_data
        },
        "ai_prompt_context": ai_context
    }