import pandas as pd
import sqlite3
from database import DB_NAME

def get_student_trends(student_id, days=5):
    """
    Pulls recent check-in history and calculates trends for sleep, pressure, and energy.
    Identifies repeated high-support patterns.
    """
    conn = sqlite3.connect(DB_NAME)
    
    # Pull the most recent check-ins for the student
    query = '''
        SELECT timestamp, sleep_hours, academic_pressure, energy_level, workload_level
        FROM check_ins
        WHERE student_id = ?
        ORDER BY timestamp ASC
        LIMIT ?
    '''
    
    # Load directly into a Pandas DataFrame for easy analysis
    df = pd.read_sql_query(query, conn, params=(student_id, days))
    conn.close()
    
    # We need at least 2 data points to establish a trend
    if df.empty or len(df) < 2:
        return {
            "status": "insufficient_data", 
            "message": "Need at least 2 check-ins to analyze trends."
        }
        
    # Calculate simple delta between the oldest and newest records in this window
    first_record = df.iloc[0]
    latest_record = df.iloc[-1]
    
    trends = {
        "sleep_change": latest_record['sleep_hours'] - first_record['sleep_hours'],
        "pressure_change": latest_record['academic_pressure'] - first_record['academic_pressure'],
        "energy_change": latest_record['energy_level'] - first_record['energy_level']
    }
    
    # Pattern Detection: Identify repeated high-support patterns (e.g., chronic pressure)
    high_pressure_days = len(df[df['academic_pressure'] >= 8])
    chronic_pressure = high_pressure_days >= 3  # Flag if 3 or more days show high pressure
    
    low_sleep_days = len(df[df['sleep_hours'] < 5.0])
    chronic_sleep_deprivation = low_sleep_days >= 3
    
    return {
        "status": "success",
        "records_analyzed": len(df),
        "trends": trends,
        "warnings": {
            "chronic_academic_pressure": bool(chronic_pressure),
            "chronic_sleep_deprivation": bool(chronic_sleep_deprivation),
            "worsening_sleep": bool(trends["sleep_change"] <= -1.5) # Sleep dropped by 1.5+ hours
        }
    }

# To test this standalone:
if __name__ == "__main__":
    print(get_student_trends('student_001', days=5))