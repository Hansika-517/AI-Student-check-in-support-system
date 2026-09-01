import sqlite3

# Import your functions from the files we just created
from database import DB_NAME, init_db
from scoring import calculate_support_score

def test_data_flow():
    # 1. Make sure the database and tables exist
    init_db()
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # 2. Insert the "Killer Demo Flow" data
    # 4.5 hours sleep, pressure 9, energy 3, high workload (9), 3 deadlines
    print("\nInserting demo check-in data...")
    cursor.execute('''
        INSERT INTO check_ins (
            student_id, sleep_hours, mood_score, energy_level, 
            workload_level, academic_pressure, deadlines_count, optional_message
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', ("student_001", 4.5, 4, 3, 9, 9, 3, "I have three assignments and I don't think I can finish."))
    
    conn.commit()

    # 3. Retrieve the latest data for that student
    print("Retrieving data from SQLite...")
    cursor.execute('''
        SELECT sleep_hours, academic_pressure, energy_level, workload_level, deadlines_count
        FROM check_ins 
        WHERE student_id = 'student_001' 
        ORDER BY timestamp DESC LIMIT 1
    ''')
    
    row = cursor.fetchone()
    conn.close()

    if row:
        # 4. Map the SQLite row back into a dictionary
        check_in_data = {
            'sleep_hours': row[0],
            'academic_pressure': row[1],
            'energy_level': row[2],
            'workload_level': row[3],
            'deadlines_count': row[4]
        }
        
        print("\n--- Data Pulled from DB ---")
        print(check_in_data)
        
        # 5. Pass the retrieved data into your scoring engine
        print("\n--- Output from scoring.py ---")
        results = calculate_support_score(check_in_data)
        
        print(f"Total Score: {results['total_score']}")
        print(f"Support Level: {results['support_level']}")
        print(f"Flags Triggered: {', '.join(results['identified_flags'])}")
        
    else:
        print("Error: No data found.")

if __name__ == "__main__":
    test_data_flow()