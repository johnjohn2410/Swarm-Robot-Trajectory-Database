import sqlite3
import math
import os

DB_NAME = 'robot.db'


def execute_query_and_print(conn, query_description, query, params=None):
    cursor = conn.cursor()
    print(f"\n--- {query_description} ---")
    print(f"SQL Query: {query.strip()}")
    if params:
        print(f"Parameters: {params}")

    try:
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)

        rows = cursor.fetchall()

        if rows:
            header = [description[0] for description in cursor.description]
            print("Results:")
            print(header)
            for row in rows:
                print(row)
        else:
            print("No results found.")

    except sqlite3.Error as e:
        print(f"An SQL error occurred: {e}")
    finally:
        print("-" * (len(query_description) + 12))  # Adjust line length


def task3_queries(conn):
    print("\n" + "=" * 10 + " TASK 3: META-INFO QUERIES " + "=" * 10)
    query1_desc = "1. Robot Names with Max/Min X-axis"
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

    query2_desc = "2. Robot Names with Max/Min Y-axis"
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


def task4_queries(conn):
    print("\n" + "=" * 10 + " TASK 4: TRAJECTORY ANALYSIS " + "=" * 10)

    # 1. Regions where Astro and IamHuman are close
    #    A "region" here is defined as a continuous sequence of timestamps
    #    where the robots are close. We will output the start and end timestamp
    #    of each such continuous region, along with the bounding box of Astro's
    #    movement during that specific close period.

    query_close_regions_desc = "1. Regions where Astro and IamHuman are close"
    # This query is more complex to find continuous regions.
    # We first identify all timestamps where they are close.
    # Then, group consecutive timestamps.
    query_close_regions = '''
                          WITH CloseTimestamps AS (SELECT t_astro.timestamp, \
                                                          t_astro.x_coord AS astro_x, \
                                                          t_astro.y_coord AS astro_y, \
                                                          t_human.x_coord AS human_x, \
                                                          t_human.y_coord AS human_y \
                                                   FROM Trajectories t_astro \
                                                            JOIN \
                                                        Robots r_astro ON t_astro.robot_id = r_astro.robot_id \
                                                            JOIN \
                                                        Trajectories t_human ON t_astro.timestamp = t_human.timestamp \
                                                            JOIN \
                                                        Robots r_human ON t_human.robot_id = r_human.robot_id \
                                                   WHERE r_astro.name = 'Astro' \
                                                     AND r_human.name = 'IamHuman' \
                                                     AND t_astro.robot_id \
                              != t_human.robot_id
                              AND ABS(t_astro.x_coord - t_human.x_coord) \
                             < 1
                              AND ABS(t_astro.y_coord - t_human.y_coord) \
                             < 1
                              ) \
                             , GroupedCloseEvents AS (
                          SELECT
                              timestamp, astro_x, astro_y,
                              -- Create groups for consecutive timestamps
                              timestamp - ROW_NUMBER() OVER (ORDER BY timestamp) as grp
                          FROM CloseTimestamps
                              )
                          SELECT MIN(timestamp) AS region_start_time, \
                                 MAX(timestamp) AS region_end_time, \
                                 MIN(astro_x)   AS astro_region_x_min, \
                                 MAX(astro_x)   AS astro_region_x_max, \
                                 MIN(astro_y)   AS astro_region_y_min, \
                                 MAX(astro_y)   AS astro_region_y_max
                          FROM GroupedCloseEvents
                          GROUP BY grp
                          ORDER BY region_start_time; \
                          '''
    execute_query_and_print(conn, query_close_regions_desc, query_close_regions)

    # 2. How many secs Astro and IamHuman are close
    query_close_duration_desc = "2. Duration (secs) Astro and IamHuman are close"
    query_close_duration = '''
                           SELECT COUNT(DISTINCT t_astro.timestamp) AS total_close_duration_secs
                           FROM Trajectories t_astro \
                                    JOIN \
                                Robots r_astro ON t_astro.robot_id = r_astro.robot_id \
                                    JOIN \
                                Trajectories t_human ON t_astro.timestamp = t_human.timestamp \
                                    JOIN \
                                Robots r_human ON t_human.robot_id = r_human.robot_id
                           WHERE r_astro.name = 'Astro' \
                             AND r_human.name = 'IamHuman'
                             AND t_astro.robot_id != t_human.robot_id 
            AND ABS(t_astro.x_coord - t_human.x_coord) < 1
            AND ABS(t_astro.y_coord - t_human.y_coord) < 1; \
                           '''
    execute_query_and_print(conn, query_close_duration_desc, query_close_duration)


def task4_bonus_query(conn):
    print("\n" + "=" * 10 + " TASK 4 (BONUS): AVERAGE ROBOT MOVING SPEED " + "=" * 10)
    cursor = conn.cursor()

    cursor.execute("SELECT interval_id, start_time, end_time, event_type FROM TargetIntervals ORDER BY interval_id")
    intervals = cursor.fetchall()

    cursor.execute("SELECT robot_id, name FROM Robots")
    robots_info = {r[0]: r[1] for r in cursor.fetchall()}  # Store as dict for easy name lookup

    results_table_header = ["Interval ID", "Event Type", "Robot Name", "Avg Speed (cm/s)", "Is Slower (<0.2 cm/s)?"]
    results_data = []

    for interval_id, start_time, end_time, event_type in intervals:
        robots_in_interval_met_criteria = 0  # Count robots meeting criteria for "overall" assessment

        for robot_id, robot_name in robots_info.items():
            # Query to get points for a specific robot within the interval
            # Lag function to get previous coordinates for speed calculation
            query = '''
                    WITH RobotPoints AS (SELECT
                        timestamp \
                       , x_coord \
                       , y_coord \
                       , LAG(x_coord \
                       , 1 \
                       , NULL) OVER (ORDER BY timestamp) AS prev_x \
                       , LAG(y_coord \
                       , 1 \
                       , NULL) OVER (ORDER BY timestamp) AS prev_y \
                       , LAG(timestamp \
                       , 1 \
                       , NULL) OVER (ORDER BY timestamp) AS prev_ts
                    FROM Trajectories
                    WHERE robot_id = ? AND timestamp BETWEEN ? AND ?
                    ORDER BY timestamp ASC
                        )
                    SELECT SUM(SQRT(POWER(x_coord - prev_x, 2) + POWER(y_coord - prev_y, 2))) AS total_distance, \
                           SUM(timestamp - prev_ts)                                           AS total_duration_segments
                    FROM RobotPoints
                    WHERE prev_x IS NOT NULL \
                      AND prev_y IS NOT NULL \
                      AND prev_ts IS NOT NULL; \
                    '''
            # Note: SUM(timestamp - prev_ts) is equivalent to (last_ts - first_ts_in_segment_calc)
            # if all segments are 1s, it's (number of points - 1)

            cursor.execute(query, (robot_id, start_time, end_time))
            result = cursor.fetchone()

            total_distance_robot = result[0]
            total_duration_segments = result[1]  # This is the number of 1-second segments

            if total_distance_robot is not None and total_duration_segments is not None and total_duration_segments > 0:
                avg_speed_robot = total_distance_robot / total_duration_segments
                is_slower = "Yes" if avg_speed_robot < 0.2 else "No"
                results_data.append([f"{interval_id}", event_type, robot_name, f"{avg_speed_robot:.4f}", is_slower])
            else:
                # Robot had no movement or only one point in this interval
                results_data.append([f"{interval_id}", event_type, robot_name, "N/A (no movement/data)", "N/A"])

    # Print the results table
    # Calculate column widths for better formatting
    if results_data:
        col_widths = [len(str(x)) for x in results_table_header]
        for row_data in results_data:
            for i, cell in enumerate(row_data):
                col_widths[i] = max(col_widths[i], len(str(cell)))

        format_str = " | ".join([f"{{:<{w}}}" for w in col_widths])

        print(format_str.format(*results_table_header))
        print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)))  # Separator line
        for row in results_data:
            print(format_str.format(*row))
    else:
        print("No interval data to process for the bonus task.")
    print("-" * (sum(col_widths) + 3 * (len(col_widths) - 1)) if results_data else "-" * 70)


if __name__ == '__main__':
    if not os.path.exists(DB_NAME):
        print(f"Database '{DB_NAME}' not found. Please run setup_database.py first to create and populate it.")
    else:
        conn = sqlite3.connect(DB_NAME)

        task3_queries(conn)
        task4_queries(conn)
        task4_bonus_query(conn)

        conn.close()