"""
High School Management System API

A super simple FastAPI application that allows students to view and sign up
for extracurricular activities at Mergington High School.
"""

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import sqlite3
from pathlib import Path

app = FastAPI(title="Mergington High School API",
              description="API for viewing and signing up for extracurricular activities")

# Mount the static files directory
current_dir = Path(__file__).parent
app.mount("/static", StaticFiles(directory=os.path.join(Path(__file__).parent,
          "static")), name="static")

# Database configuration
DB_PATH = os.path.join(Path(__file__).parent.parent, "activities.db")

def init_db():
    """Initialize the SQLite database with schema and seed data"""
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # Create activities table
    c.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE NOT NULL,
            description TEXT NOT NULL,
            schedule TEXT NOT NULL,
            max_participants INTEGER NOT NULL
        )
    ''')
    
    # Create participants table (many-to-many relationship)
    c.execute('''
        CREATE TABLE IF NOT EXISTS participants (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            activity_id INTEGER NOT NULL,
            email TEXT NOT NULL,
            FOREIGN KEY (activity_id) REFERENCES activities (id) ON DELETE CASCADE,
            UNIQUE(activity_id, email)
        )
    ''')
    
    # Check if database already has data (to avoid re-seeding on restart)
    c.execute('SELECT COUNT(*) FROM activities')
    activity_count = c.fetchone()[0]
    
    # Only seed if database is empty
    if activity_count == 0:
        # Seed initial activities
        seed_activities = [
            ("Chess Club", "Learn strategies and compete in chess tournaments", "Fridays, 3:30 PM - 5:00 PM", 12),
            ("Programming Class", "Learn programming fundamentals and build software projects", "Tuesdays and Thursdays, 3:30 PM - 4:30 PM", 20),
            ("Gym Class", "Physical education and sports activities", "Mondays, Wednesdays, Fridays, 2:00 PM - 3:00 PM", 30),
            ("Soccer Team", "Join the school soccer team and compete in matches", "Tuesdays and Thursdays, 4:00 PM - 5:30 PM", 22),
            ("Basketball Team", "Practice and play basketball with the school team", "Wednesdays and Fridays, 3:30 PM - 5:00 PM", 15),
            ("Art Club", "Explore your creativity through painting and drawing", "Thursdays, 3:30 PM - 5:00 PM", 15),
            ("Drama Club", "Act, direct, and produce plays and performances", "Mondays and Wednesdays, 4:00 PM - 5:30 PM", 20),
            ("Math Club", "Solve challenging problems and participate in math competitions", "Tuesdays, 3:30 PM - 4:30 PM", 10),
            ("Debate Team", "Develop public speaking and argumentation skills", "Fridays, 4:00 PM - 5:30 PM", 12)
        ]
        
        for name, desc, schedule, max_p in seed_activities:
            c.execute('''
                INSERT INTO activities (name, description, schedule, max_participants)
                VALUES (?, ?, ?, ?)
            ''', (name, desc, schedule, max_p))
        
        # Seed initial participants
        seed_participants = [
            ("Chess Club", "michael@mergington.edu"),
            ("Chess Club", "daniel@mergington.edu"),
            ("Programming Class", "emma@mergington.edu"),
            ("Programming Class", "sophia@mergington.edu"),
            ("Gym Class", "john@mergington.edu"),
            ("Gym Class", "olivia@mergington.edu"),
            ("Soccer Team", "liam@mergington.edu"),
            ("Soccer Team", "noah@mergington.edu"),
            ("Basketball Team", "ava@mergington.edu"),
            ("Basketball Team", "mia@mergington.edu"),
            ("Art Club", "amelia@mergington.edu"),
            ("Art Club", "harper@mergington.edu"),
            ("Drama Club", "ella@mergington.edu"),
            ("Drama Club", "scarlett@mergington.edu"),
            ("Math Club", "james@mergington.edu"),
            ("Math Club", "benjamin@mergington.edu"),
            ("Debate Team", "charlotte@mergington.edu"),
            ("Debate Team", "henry@mergington.edu")
        ]
        
        for activity_name, email in seed_participants:
            c.execute('''
                SELECT id FROM activities WHERE name = ?
            ''', (activity_name,))
            result = c.fetchone()
            if result:
                activity_id = result[0]
                c.execute('''
                    INSERT INTO participants (activity_id, email)
                    VALUES (?, ?)
                ''', (activity_id, email))
    
    conn.commit()
    conn.close()

def get_db_connection():
    """Get a connection to the SQLite database"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row  # Access columns by name
    return conn

# Initialize database on startup
init_db()


@app.get("/")
def root():
    return RedirectResponse(url="/static/index.html")


@app.get("/activities")
def get_activities():
    """Get all activities with their participants"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Get all activities
    c.execute('SELECT id, name, description, schedule, max_participants FROM activities ORDER BY name')
    activities_list = c.fetchall()
    
    result = {}
    for activity in activities_list:
        activity_id, name, desc, schedule, max_p = activity
        
        # Get participants for this activity
        c.execute('SELECT email FROM participants WHERE activity_id = ? ORDER BY email', (activity_id,))
        participants = [row[0] for row in c.fetchall()]
        
        result[name] = {
            "description": desc,
            "schedule": schedule,
            "max_participants": max_p,
            "participants": participants
        }
    
    conn.close()
    return result


@app.post("/activities/{activity_name}/signup")
def signup_for_activity(activity_name: str, email: str):
    """Sign up a student for an activity"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Validate activity exists
    c.execute('SELECT id, max_participants FROM activities WHERE name = ?', (activity_name,))
    activity_result = c.fetchone()
    
    if not activity_result:
        conn.close()
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity_id, max_participants = activity_result
    
    # Check if student is already signed up
    c.execute('SELECT id FROM participants WHERE activity_id = ? AND email = ?', (activity_id, email))
    if c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Student is already signed up"
        )
    
    # Check if activity is at capacity
    c.execute('SELECT COUNT(*) FROM participants WHERE activity_id = ?', (activity_id,))
    current_count = c.fetchone()[0]
    
    if current_count >= max_participants:
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Activity is at maximum capacity"
        )
    
    # Add student to activity
    try:
        c.execute('INSERT INTO participants (activity_id, email) VALUES (?, ?)', (activity_id, email))
        conn.commit()
        conn.close()
        return {"message": f"Signed up {email} for {activity_name}"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/activities/{activity_name}/unregister")
def unregister_from_activity(activity_name: str, email: str):
    """Unregister a student from an activity"""
    conn = get_db_connection()
    c = conn.cursor()
    
    # Validate activity exists
    c.execute('SELECT id FROM activities WHERE name = ?', (activity_name,))
    activity_result = c.fetchone()
    
    if not activity_result:
        conn.close()
        raise HTTPException(status_code=404, detail="Activity not found")
    
    activity_id = activity_result[0]
    
    # Check if student is signed up
    c.execute('SELECT id FROM participants WHERE activity_id = ? AND email = ?', (activity_id, email))
    if not c.fetchone():
        conn.close()
        raise HTTPException(
            status_code=400,
            detail="Student is not signed up for this activity"
        )
    
    # Remove student from activity
    try:
        c.execute('DELETE FROM participants WHERE activity_id = ? AND email = ?', (activity_id, email))
        conn.commit()
        conn.close()
        return {"message": f"Unregistered {email} from {activity_name}"}
    except Exception as e:
        conn.close()
        raise HTTPException(status_code=500, detail=str(e))
