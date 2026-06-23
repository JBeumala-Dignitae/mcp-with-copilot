# Mergington High School Activities API

A super simple FastAPI application that allows students to view and sign up for extracurricular activities.

## Features

- View all available extracurricular activities
- Sign up for activities

## Getting Started

1. Install the dependencies:

   ```
   pip install fastapi uvicorn
   ```

2. Run the application:

   ```
   python app.py
   ```

3. Open your browser and go to:
   - API documentation: http://localhost:8000/docs
   - Alternative documentation: http://localhost:8000/redoc

## API Endpoints

| Method | Endpoint                                                          | Description                                                         |
| ------ | ----------------------------------------------------------------- | ------------------------------------------------------------------- |
| GET    | `/activities`                                                     | Get all activities with their details and current participant count |
| POST   | `/activities/{activity_name}/signup?email=student@mergington.edu` | Sign up for an activity                                             |

## Data Model

The application uses SQLite for persistent data storage with the following schema:

**Activities Table:**
- `id` (INTEGER PRIMARY KEY)
- `name` (TEXT UNIQUE) - Activity name
- `description` (TEXT) - What the activity is about
- `schedule` (TEXT) - Meeting times
- `max_participants` (INTEGER) - Capacity limit

**Participants Table:**
- `id` (INTEGER PRIMARY KEY)
- `activity_id` (FOREIGN KEY) - References activities table
- `email` (TEXT) - Student email address
- UNIQUE constraint on (activity_id, email) to prevent duplicate signups

## Database

- **Location:** `activities.db` (stored in the project root directory)
- **Type:** SQLite3 (built-in with Python, no additional dependencies)
- **Persistence:** All data persists across application restarts
- **Initialization:** Database is automatically created and seeded on first run

The database is initialized automatically when the application starts. If the database file already exists, it will reuse it and skip seeding duplicate data.
