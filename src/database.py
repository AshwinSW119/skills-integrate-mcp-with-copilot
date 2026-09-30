"""SQLite persistence for activities and student registrations."""

from contextlib import contextmanager
import os
from pathlib import Path
import sqlite3


INITIAL_ACTIVITIES = {
    "Chess Club": (
        "Learn strategies and compete in chess tournaments",
        "Fridays, 3:30 PM - 5:00 PM",
        12,
        ["michael@mergington.edu", "daniel@mergington.edu"],
    ),
    "Programming Class": (
        "Learn programming fundamentals and build software projects",
        "Tuesdays and Thursdays, 3:30 PM - 4:30 PM",
        20,
        ["emma@mergington.edu", "sophia@mergington.edu"],
    ),
    "Gym Class": (
        "Physical education and sports activities",
        "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM",
        30,
        ["john@mergington.edu", "olivia@mergington.edu"],
    ),
    "Soccer Team": (
        "Join the school soccer team and compete in matches",
        "Tuesdays and Thursdays, 4:00 PM - 5:30 PM",
        22,
        ["liam@mergington.edu", "noah@mergington.edu"],
    ),
    "Basketball Team": (
        "Practice and play basketball with the school team",
        "Wednesdays and Fridays, 3:30 PM - 5:00 PM",
        15,
        ["ava@mergington.edu", "mia@mergington.edu"],
    ),
    "Art Club": (
        "Explore your creativity through painting and drawing",
        "Thursdays, 3:30 PM - 5:00 PM",
        15,
        ["amelia@mergington.edu", "harper@mergington.edu"],
    ),
    "Drama Club": (
        "Act, direct, and produce plays and performances",
        "Mondays and Wednesdays, 4:00 PM - 5:30 PM",
        20,
        ["ella@mergington.edu", "scarlett@mergington.edu"],
    ),
    "Math Club": (
        "Solve challenging problems and participate in math competitions",
        "Tuesdays, 3:30 PM - 4:30 PM",
        10,
        ["james@mergington.edu", "benjamin@mergington.edu"],
    ),
    "Debate Team": (
        "Develop public speaking and argumentation skills",
        "Fridays, 4:00 PM - 5:30 PM",
        12,
        ["charlotte@mergington.edu", "henry@mergington.edu"],
    ),
}


class ActivityNotFound(Exception):
    """Raised when an activity name is not present in the database."""


class RegistrationAlreadyExists(Exception):
    """Raised when a student is already registered for an activity."""


class RegistrationNotFound(Exception):
    """Raised when a student is not registered for an activity."""


def _database_path():
    return os.environ.get(
        "DATABASE_PATH", str(Path(__file__).with_name("activities.db"))
    )


def _initialize_schema(connection):
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS activities (
            name TEXT PRIMARY KEY,
            description TEXT NOT NULL,
            schedule TEXT NOT NULL,
            max_participants INTEGER NOT NULL
        );
        CREATE TABLE IF NOT EXISTS students (
            email TEXT PRIMARY KEY,
            name TEXT,
            grade_level INTEGER
        );
        CREATE TABLE IF NOT EXISTS registrations (
            activity_name TEXT NOT NULL REFERENCES activities(name),
            student_email TEXT NOT NULL REFERENCES students(email),
            PRIMARY KEY (activity_name, student_email)
        );
        """
    )

    for name, (description, schedule, maximum, participants) in INITIAL_ACTIVITIES.items():
        inserted = connection.execute(
            """
            INSERT OR IGNORE INTO activities (name, description, schedule, max_participants)
            VALUES (?, ?, ?, ?)
            """,
            (name, description, schedule, maximum),
        ).rowcount
        if inserted:
            for email in participants:
                connection.execute(
                    "INSERT OR IGNORE INTO students (email) VALUES (?)", (email,)
                )
                connection.execute(
                    """
                    INSERT OR IGNORE INTO registrations (activity_name, student_email)
                    VALUES (?, ?)
                    """,
                    (name, email),
                )


@contextmanager
def _connection():
    connection = sqlite3.connect(_database_path(), timeout=5)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    try:
        _initialize_schema(connection)
        yield connection
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def initialize_database():
    """Create the schema and seed initial activities if the database is empty."""
    with _connection():
        pass


def get_activities():
    with _connection() as connection:
        rows = connection.execute(
            """
            SELECT activities.name, activities.description, activities.schedule,
                   activities.max_participants, registrations.student_email
            FROM activities
            LEFT JOIN registrations ON registrations.activity_name = activities.name
            ORDER BY activities.rowid, registrations.rowid
            """
        ).fetchall()

    activities = {}
    for row in rows:
        activity = activities.setdefault(
            row["name"],
            {
                "description": row["description"],
                "schedule": row["schedule"],
                "max_participants": row["max_participants"],
                "participants": [],
            },
        )
        if row["student_email"] is not None:
            activity["participants"].append(row["student_email"])
    return activities


def signup(activity_name, email):
    with _connection() as connection:
        activity = connection.execute(
            "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
        ).fetchone()
        if activity is None:
            raise ActivityNotFound

        registration = connection.execute(
            """
            SELECT 1 FROM registrations
            WHERE activity_name = ? AND student_email = ?
            """,
            (activity_name, email),
        ).fetchone()
        if registration is not None:
            raise RegistrationAlreadyExists

        connection.execute("INSERT OR IGNORE INTO students (email) VALUES (?)", (email,))
        connection.execute(
            "INSERT INTO registrations (activity_name, student_email) VALUES (?, ?)",
            (activity_name, email),
        )


def unregister(activity_name, email):
    with _connection() as connection:
        activity = connection.execute(
            "SELECT 1 FROM activities WHERE name = ?", (activity_name,)
        ).fetchone()
        if activity is None:
            raise ActivityNotFound

        deleted = connection.execute(
            """
            DELETE FROM registrations
            WHERE activity_name = ? AND student_email = ?
            """,
            (activity_name, email),
        ).rowcount
        if not deleted:
            raise RegistrationNotFound


if __name__ == "__main__":
    initialize_database()
    print(f"Database initialized at {_database_path()}")