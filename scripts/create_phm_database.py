
import sqlite3
import csv
import os

def create_database():
    db_path = 'phm_data.db'
    # Remove the database if it exists
    if os.path.exists(db_path):
        os.remove(db_path)

    conn = sqlite3.connect(db_path)
    c = conn.cursor()

    # Create training_summary table
    c.execute('''
        CREATE TABLE training_summary (
            bearing_id TEXT PRIMARY KEY,
            operation_condition TEXT,
            load_n REAL,
            rpm INTEGER,
            actual_rul_min REAL,
            data_file_count INTEGER,
            total_duration_min REAL,
            data_points_per_file INTEGER,
            sample_rate_hz INTEGER
        )
    ''')

    # Create vibration_statistics table
    c.execute('''
        CREATE TABLE vibration_statistics (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            file_index INTEGER,
            time_min REAL,
            horiz_rms REAL,
            vert_rms REAL,
            horiz_peak REAL,
            vert_peak REAL,
            horiz_kurtosis REAL,
            vert_kurtosis REAL,
            bearing_name TEXT
        )
    ''')

    # Import data from training_data_summary.csv
    with open('phm_analysis_results/training_data_summary.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            c.execute('''
                INSERT INTO training_summary VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (row[0], row[1], float(row[2]), int(row[3]), float(row[4]), int(row[5]), float(row[6]), int(row[7]), int(row[8])))

    # Import data from vibration_statistics.csv
    with open('phm_analysis_results/vibration_statistics.csv', 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            c.execute('''
                INSERT INTO vibration_statistics (file_index, time_min, horiz_rms, vert_rms, horiz_peak, vert_peak, horiz_kurtosis, vert_kurtosis, bearing_name)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (int(row[0]), float(row[1]), float(row[2]), float(row[3]), float(row[4]), float(row[5]), float(row[6]), float(row[7]), row[8]))

    conn.commit()
    conn.close()
    print(f"Database '{db_path}' created successfully.")

if __name__ == '__main__':
    create_database()
