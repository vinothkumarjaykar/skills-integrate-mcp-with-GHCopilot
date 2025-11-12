"""
High School Management System API

A FastAPI application that now persists activities and enrollments to SQLite via SQLModel.
"""

from fastapi import FastAPI, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
from pathlib import Path

from sqlmodel import select
from .db import init_db, get_session
from .models import Activity, Student, Enrollment

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Initialize DB and create tables
init_db()

# Seed activities on first run if empty
with get_session() as session:
    count = session.exec(select(Activity)).all()
    if not count:
        activities_seed = [
            Activity(name="Chess Club", description="Learn strategies and compete in chess tournaments",
                     schedule="Fridays, 3:30 PM - 5:00 PM", max_participants=12),
            Activity(name="Programming Class", description="Learn programming fundamentals and build software projects",
                     schedule="Tuesdays and Thursdays, 3:30 PM - 4:30 PM", max_participants=20),
            Activity(name="Gym Class", description="Physical education and sports activities",
                     schedule="Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", max_participants=30),
            Activity(name="Soccer Team", description="Join the school soccer team and compete in matches",
                     schedule="Tuesdays and Thursdays, 4:00 PM - 5:30 PM", max_participants=22),
            Activity(name="Basketball Team", description="Practice and play basketball with the school team",
                     schedule="Wednesdays and Fridays, 3:30 PM - 5:00 PM", max_participants=15),
            Activity(name="Art Club", description="Explore your creativity through painting and drawing",
                     schedule="Thursdays, 3:30 PM - 5:00 PM", max_participants=15),
            Activity(name="Drama Club", description="Act, direct, and produce plays and performances",
                     schedule="Mondays and Wednesdays, 4:00 PM - 5:30 PM", max_participants=20),
            Activity(name="Math Club", description="Solve challenging problems and participate in math competitions",
                     schedule="Tuesdays, 3:30 PM - 4:30 PM", max_participants=10),
            Activity(name="Debate Team", description="Develop public speaking and argumentation skills",
                     schedule="Fridays, 4:00 PM - 5:30 PM", max_participants=12),
        ]
        session.add_all(activities_seed)
        session.commit()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    with get_session() as session:
        activities = session.exec(select(Activity)).all()
        result = {}
        for a in activities:
            # count participants via query
            pcount = session.exec(select(Enrollment).where(Enrollment.activity_id == a.id)).count()
            result[a.name] = {
                "description": a.description,
                "schedule": a.schedule,
                "max_participants": a.max_participants,
                "participants": [] if pcount == 0 else [e.student_email for e in session.exec(select(Enrollment).where(Enrollment.activity_id == a.id)).all()]
            }
        return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    with get_session() as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        # check duplicates
        existing = session.exec(select(Enrollment).where(Enrollment.activity_id == activity.id).where(Enrollment.student_email == email)).first()
        if existing:
            raise HTTPException(status_code=400, detail="Student is already signed up")

        pcount = session.exec(select(Enrollment).where(Enrollment.activity_id == activity.id)).count()
        if activity.max_participants and pcount >= activity.max_participants:
            raise HTTPException(status_code=409, detail="Activity is full")

        # ensure student exists
        student = session.exec(select(Student).where(Student.email == email)).first()
        if not student:
            student = Student(email=email)
            session.add(student)
            session.commit()

        enroll = Enrollment(student_email=email, activity_id=activity.id)
        session.add(enroll)
        session.commit()
        return {"message": f"Signed up {email} for {activity_name}"}


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    with get_session() as session:
        activity = session.exec(select(Activity).where(Activity.name == activity_name)).first()
        if not activity:
            raise HTTPException(status_code=404, detail="Activity not found")

        enroll = session.exec(select(Enrollment).where(Enrollment.activity_id == activity.id).where(Enrollment.student_email == email)).first()
        if not enroll:
            raise HTTPException(status_code=400, detail="Student is not signed up for this activity")

        session.delete(enroll)
        session.commit()
        return {"message": f"Unregistered {email} from {activity_name}"}
