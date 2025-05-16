# task3_meta_info.py
import sqlite3
import os

DB_NAME = 'robot.db'


def execute_query_and_print(conn, query_description, query, params=None):
    cursor = conn.cursor()
    print(f"\n--- {query_description} ---")
    # print(f"SQL Query: {query.strip()}") # Optional: uncomment to print the SQL query

    try:
        if params:
            # print(f"Parameters: {params}") # Optional: uncomment to print parameters
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()

        if rows:
            header = [description[0] for description in cursor.description]
            print("Results:")
            # Print header
            header_str = " | ".join(header)
            print(header_str)
            print("-" * len(header_str))  # Dynamic separator length
            # Print rows
            for row in rows:
                # Convert all items in row to string for consistent printing
                print(" | ".join(map(str, row)))
        else:
            print("No results found.")

    except sqlite3.Error as e:
        print(f"An SQL error occurred: {e}")
    finally:
        # Dynamic separator length based on description length
        print("-" * (len(query_description) + 12 if query_description else 50))


def main():
    if not os.path.exists(DB_NAME):
        print(f"Database '{DB_NAME}' not found. Please run task2_setup_database.py first to create and populate it.")
        return

    conn = sqlite3.connect(DB_NAME)

    print("\n" + "=" * 10 + " EXECUTING TASK 3: META-INFO QUERIES " + "=" * 10)

    query1_desc = "1. Table: Robot Names with Maximal and Minimum X-axis"
    query1 = '''
             SELECT r.name         AS robot_name, \
                    MAX(t.x_coord) AS max_x_reached, \
                    MIN(t.x_coord) AS min_x_reached
             FROM Robots r \
                      JOIN \
                  Trajectories t ON r.robot_id = t.robot_id
             GROUP BY r.name
             ORDER BY r.name; \
             '''
    execute_query_and_print(conn, query1_desc, query1)

    query2_desc = "2. Table: Robot Names with Maximal and Minimum Y-axis"
    query2 = '''
             SELECT r.name         AS robot_name, \
                    MAX(t.y_coord) AS max_y_reached, \
                    MIN(t.y_coord) AS min_y_reached
             FROM Robots r \
                      JOIN \
                  Trajectories t ON r.robot_id = t.robot_id
             GROUP BY r.name
             ORDER BY r.name; \
             '''
    execute_query_and_print(conn, query2_desc, query2)

    conn.close()
    print("\nTask 3 queries complete.")


if __name__ == '__main__':
    main()