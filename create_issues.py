#!/usr/bin/env python3
"""
Script para crear issues en el repositorio de GitHub
Usa PyGithub para crear issues basados en características faltantes
"""

from github import Github
import os

# Obtener token de GitHub desde variable de entorno
TOKEN = os.getenv('GITHUB_TOKEN')
if not TOKEN:
    print("Error: GITHUB_TOKEN no está definido")
    print("Por favor, establece: export GITHUB_TOKEN=your_token")
    exit(1)

# Datos de autenticación y repo
REPO_OWNER = "JBeumala-Dignitae"
REPO_NAME = "mcp-with-copilot"

# Lista de issues a crear
ISSUES = [
    {
        "title": "Add Coach/Instructor Information",
        "body": "Add support for coach/instructor profiles with contact information for each activity"
    },
    {
        "title": "Add Announcements & Updates System",
        "body": "Implement announcements and news updates specific to each activity"
    },
    {
        "title": "Add Media Gallery for Activities",
        "body": "Allow uploading and displaying photos and event documentation for activities"
    },
    {
        "title": "Add Student Profiles",
        "body": "Create individual student profile pages to manage personal information and activity history"
    },
    {
        "title": "Add Participation History Tracking",
        "body": "Track and display students' historical participation across activities"
    },
    {
        "title": "Add Calendar System",
        "body": "Implement a calendar view for activities with enrollment deadlines"
    },
    {
        "title": "Add Venue/Location Information",
        "body": "Display venue and location details for each activity"
    },
    {
        "title": "Add Search & Filter Functionality",
        "body": "Implement search and filtering capabilities for discovering activities"
    },
    {
        "title": "Add Role-Based Access Control",
        "body": "Implement different user roles (student, coach, admin) with appropriate permissions"
    },
    {
        "title": "Add Authentication System",
        "body": "Implement user authentication with secure login and email verification"
    },
    {
        "title": "Migrate to Persistent Database (SQLite/PostgreSQL)",
        "body": "Replace in-memory storage with a persistent database solution using SQLite or PostgreSQL"
    },
    {
        "title": "Add Activity Administration Panel",
        "body": "Create admin interface for managing activities, coaches, and participants"
    },
    {
        "title": "Add Email Verification",
        "body": "Implement email verification for student signups to prevent abuse"
    },
    {
        "title": "Enforce Activity Capacity Limits",
        "body": "Properly enforce maximum participant limits for activities"
    }
]

def create_issues():
    """Crea todos los issues en el repositorio"""
    try:
        # Conectar a GitHub
        g = Github(TOKEN)
        repo = g.get_user(REPO_OWNER).get_repo(REPO_NAME)
        
        print(f"Creando issues en {REPO_OWNER}/{REPO_NAME}...\n")
        
        created_count = 0
        for issue_data in ISSUES:
            try:
                issue = repo.create_issue(
                    title=issue_data["title"],
                    body=issue_data["body"]
                )
                print(f"✓ Creado: #{issue.number} - {issue.title}")
                created_count += 1
            except Exception as e:
                print(f"✗ Error al crear '{issue_data['title']}': {str(e)}")
        
        print(f"\n✓ {created_count}/{len(ISSUES)} issues creados exitosamente")
        
    except Exception as e:
        print(f"Error de conexión: {str(e)}")
        print("Verifica que GITHUB_TOKEN sea válido")
        exit(1)

if __name__ == "__main__":
    create_issues()
