# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install -r requirements.txt
   ```

2. (Optional) Set a database file location. The default is `src/activities.db`:

   ```
   export DATABASE_PATH=./activities.db
   ```

3. Initialize the schema and default activities, then run the API from the repository root:

   ```
   python -m src.database
   uvicorn src.app:app --reload
   ```

   Schema initialization is safe to rerun and is also performed automatically when the API accesses the database.

4. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |
| DELETE | `/activities/{activity_name}/unregister?email=student@mergington.edu` | Unregister from an activity                                       |

## Data Model

The application uses a simple data model with meaningful identifiers:

1. **Activities** - Uses activity name as identifier:

   - Description
   - Schedule
   - Maximum number of participants allowed
   - List of student emails who are signed up

2. **Students** - Uses email as identifier:
   - Name
   - Grade level

Activities, students, and registrations are stored in SQLite and survive server restarts. Set `DATABASE_PATH` to choose the database file; database connection failures return HTTP 503 with setup guidance.
