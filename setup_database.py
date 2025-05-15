import sqlite3
import csv
import os

DB_NAME = 'robot.db'
DATA_PATH = '.'  # Assumes CSV files are in the same directory as the script


def create_tables(conn):
    cursor = conn.cursor()
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Robots
                   (
                       robot_id
                       INTEGER
                       PRIMARY
                       KEY,
                       name
                       TEXT
                       NOT
                       NULL
                       UNIQUE
                   )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS Trajectories
                   (
                       trajectory_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       robot_id
                       INTEGER
                       NOT
                       NULL,
                       timestamp
                       INTEGER
                       NOT
                       NULL,
                       x_coord
                       REAL
                       NOT
                       NULL,
                       y_coord
                       REAL
                       NOT
                       NULL,
                       FOREIGN
                       KEY
                   (
                       robot_id
                   ) REFERENCES Robots
                   (
                       robot_id
                   ),
                       UNIQUE
                   (
                       robot_id,
                       timestamp
                   )
                       )
                   ''')
    cursor.execute('''
                   CREATE TABLE IF NOT EXISTS TargetIntervals
                   (
                       interval_id
                       INTEGER
                       PRIMARY
                       KEY
                       AUTOINCREMENT,
                       start_time
                       INTEGER
                       NOT
                       NULL,
                       end_time
                       INTEGER
                       NOT
                       NULL,
                       event_type
                       TEXT
                   )
                   ''')
    conn.commit()
    print("Tables created successfully.")


def import_robot_data(conn):
    cursor = conn.cursor()
    filepath = os.path.join(DATA_PATH, 'robot.csv')
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:  # utf-8-sig handles potential BOM
            reader = csv.reader(f)
            # next(reader) # Skip header if exists, robot.csv doesn't seem to have one
            for row_num, row in enumerate(reader):
                if not row:  # Skip empty rows
                    print(f"Skipping empty row {row_num + 1} in {filepath}")
                    continue
                if len(row) == 2:
                    try:
                        robot_id, name = int(row[0]), row[1]
                        cursor.execute("INSERT INTO Robots (robot_id, name) VALUES (?, ?)", (robot_id, name))
                    except ValueError as ve:
                        print(f"Skipping row {row_num + 1} in {filepath} due to data conversion error: {row} - {ve}")
                    except sqlite3.IntegrityError as ie:
                        print(f"Skipping duplicate robot ID or name in {filepath}: {row} - {ie}")

        conn.commit()
        print(f"Robot data from {filepath} imported successfully.")
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
    except Exception as e:
        print(f"Error importing robot data from {filepath}: {e}")


def import_trajectory_data(conn):
    cursor = conn.cursor()
    for i in range(1, 6):  # t1.csv to t5.csv
        filename = f't{i}.csv'
        filepath = os.path.join(DATA_PATH, filename)
        robot_id = i  # Robot ID corresponds to the file number t(i).csv
        timestamp_counter = 0
        try:
            with open(filepath, 'r', encoding='utf-8-sig') as f:
                reader = csv.reader(f)
                for row_num, row in enumerate(reader):
                    timestamp_counter = row_num + 1  # Timestamp starts from 1 for each file
                    if not row:  # Skip empty rows
                        print(f"Skipping empty row {row_num + 1} in {filepath}")
                        continue
                    if len(row) == 2:
                        try:
                            x_coord, y_coord = float(row[0]), float(row[1])
                            cursor.execute('''
                                           INSERT INTO Trajectories (robot_id, timestamp, x_coord, y_coord)
                                           VALUES (?, ?, ?, ?)
                                           ''', (robot_id, timestamp_counter, x_coord, y_coord))
                        except ValueError as ve:
                            print(
                                f"Skipping row {row_num + 1} in {filepath} due to data conversion error: {row} - {ve}")
                        except sqlite3.IntegrityError as ie:
                            print(
                                f"Skipping duplicate trajectory entry in {filepath} for robot {robot_id} at timestamp {timestamp_counter}: {row} - {ie}")

            print(f"Trajectory data from {filepath} imported successfully.")
        except FileNotFoundError:
            print(f"Error: {filepath} not found.")
        except Exception as e:
            print(f"Error importing trajectory data from {filepath}: {e}")
    conn.commit()
    print("All trajectory data imported.")


def import_target_interval_data(conn):
    cursor = conn.cursor()
    filepath = os.path.join(DATA_PATH, 'target_interval.csv')  # Corrected filename
    try:
        with open(filepath, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f)
            header = next(reader)  # Skip header: start_time,end_time,event_type
            for row_num, row in enumerate(reader):
                if not row:  # Skip empty rows
                    print(f"Skipping empty row {row_num + 1} in {filepath}")
                    continue
                if len(row) == 3:
                    try:
                        start_time, end_time, event_type = int(row[0]), int(row[1]), row[2]
                        cursor.execute('''
                                       INSERT INTO TargetIntervals (start_time, end_time, event_type)
                                       VALUES (?, ?, ?)
                                       ''', (start_time, end_time, event_type))
                    except ValueError as ve:
                        print(f"Skipping row {row_num + 1} in {filepath} due to data conversion error: {row} - {ve}")

        conn.commit()
        print(f"Target interval data from {filepath} imported successfully.")
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
    except Exception as e:
        print(f"Error importing target interval data from {filepath}: {e}")


def main():
    if os.path.exists(DB_NAME):
        os.remove(DB_NAME)
        print(f"Removed existing database {DB_NAME}.")

    conn = sqlite3.connect(DB_NAME)

    create_tables(conn)
    import_robot_data(conn)
    import_trajectory_data(conn)
    import_target_interval_data(conn)  # Use the corrected filename

    conn.close()
    print(f"Database {DB_NAME} created and populated successfully.")


if __name__ == '__main__':
    main()