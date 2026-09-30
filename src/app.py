"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

import os
from pathlib import Path

import sqlite3
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse

from src import database

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    try:
        return database.get_activities()
    except sqlite3.Error as error:
        raise _database_unavailable(error) from error


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    try:
        database.signup(activity_name, email)
    except database.ActivityNotFound:
        raise HTTPException(status_code=404, detail="Activity not found")
    except database.RegistrationAlreadyExists:
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    except sqlite3.Error as error:
        raise _database_unavailable(error) from error
    return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    try:
        database.unregister(activity_name, email)
    except database.ActivityNotFound:
        raise HTTPException(status_code=404, detail="Activity not found")
    except database.RegistrationNotFound:
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    except sqlite3.Error as error:
        raise _database_unavailable(error) from error
    return {"message": f"Unregistered {email} from {activity_name}"}


def _database_unavailable(error):
    return HTTPException(
        status_code=503,
        detail="Database unavailable. Check DATABASE_PATH and filesystem permissions.",
    )
