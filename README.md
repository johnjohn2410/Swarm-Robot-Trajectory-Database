# Swarm Robot Trajectory Database

CSCI4333 Database Project for analyzing swarm robot trajectories. This project involves designing a relational database, populating it with data from CSV files, and performing SQL-based analysis to understand robot behavior.

## Project Structure


## Task 1: ER Diagram and Relational Schema

### ER Diagram

The Entity-Relationship Diagram for this database is provided as a separate file in the `screenshots/` directory: `task1_ERD.png` (or your chosen filename for the diagram).

*A brief note on the diagram: The `Robot` and `Trajectory` tables have a direct one-to-many relationship enforced by a foreign key. The `TargetInterval` table is used to logically filter `Trajectory` data based on time ranges in queries, rather than through a direct foreign key from `Trajectory` to `TargetInterval` in this schema.*

### Relational Schema (SQL DDL)

The database schema is defined by the following SQL `CREATE TABLE` statements:

1.  **Robots Table:**
    ```sql
    CREATE TABLE Robots (
        robot_id INTEGER PRIMARY KEY,
        name TEXT NOT NULL UNIQUE
    );
    ```

2.  **Trajectories Table:**
    ```sql
    CREATE TABLE Trajectories (
        trajectory_id INTEGER PRIMARY KEY AUTOINCREMENT,
        robot_id INTEGER NOT NULL,
        timestamp INTEGER NOT NULL,
        x_coord REAL NOT NULL,
        y_coord REAL NOT NULL,
        FOREIGN KEY (robot_id) REFERENCES Robots(robot_id),
        UNIQUE (robot_id, timestamp)
    );
    ```

3.  **TargetIntervals Table:**
    ```sql
    CREATE TABLE TargetIntervals (
        interval_id INTEGER PRIMARY KEY AUTOINCREMENT,
        start_time INTEGER NOT NULL,
        end_time INTEGER NOT NULL,
        event_type TEXT
    );
    ```

### Design Rationale

The original storage format (multiple CSVs for trajectories with implicit robot IDs and timestamps) is not optimal for database operations. The redesign involves:
*   **Consolidation:** All robot trajectory data from `t1.csv` to `t5.csv` is consolidated into a single `Trajectories` table.
*   **Explicit Information:** Implicit `robot_id` (from filename) and `timestamp` (from row number) are made explicit columns in the `Trajectories` table.
*   **Relationships:** A clear foreign key relationship is established between `Robots` and `Trajectories`.
*   **Structured Tables:** All data is formalized into tables with appropriate primary keys, data types, and constraints (like `NOT NULL`, `UNIQUE`) to ensure data integrity and query efficiency.
*   The `TargetIntervals` table is designed as a separate entity, as intervals are general periods of interest. Its connection to trajectory data is logical, made by filtering `Trajectories.timestamp` based on `TargetIntervals.start_time` and `TargetIntervals.end_time` in analytical queries.

## Task 2: Database Creation and Data Import

This task is performed by the `task2_setup_database.py` script. It creates an SQLite database named `robot.db`, defines the schema based on Task 1, and imports data from the provided CSV files.

**To run:**
```bash
python3 task2_setup_database.py
```
## Task 3: Meta-Info Queries
This task is performed by the task3_meta_info.py script, which queries the robot.db database to retrieve:
A table of robot names with their maximal and minimum x-axis values.
A table of robot names with their maximal and minimum y-axis values.
To run (after running task2_setup_database.py):
```bash
python3 task3_meta_info.py
```

## Task 4: Trajectory Analysis & Bonus
This task (including the bonus) is performed by the task4_trajectory_analysis.py script. It analyzes the robot trajectory data to:
Return regions (defined by Astro's bounding box during close periods) where "Astro" and "IamHuman" are close (x and y axis difference < 1 cm).
Measure the total duration (in seconds) these two robots are close.
(Bonus) For all target intervals, calculate each robot's average moving speed and determine if it's less than 0.2 cm/s.
To run (after running task2_setup_database.py):
```bash
python3 task4_trajectory_analysis.py
```
