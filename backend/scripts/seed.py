r"""
CampusRide Seed Script
Run from D:\Devops_project\backend with:
  python scripts/seed.py
"""

import os
import sys
import uuid
from pathlib import Path
from dotenv import load_dotenv
from passlib.context import CryptContext
import psycopg2
from psycopg2.extras import execute_values

# Load .env from backend root
load_dotenv(Path(__file__).parent.parent / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash_password(plain: str) -> str:
    """Hash a password using bcrypt."""
    return pwd_context.hash(plain)


ADMIN = {
    "name": "Admin User",
    "email": "admin@campusride.com",
    "password": "Admin@123",
    "role": "admin"
}

STUDENTS = [
    {"name": "Aarav Mehta", "email": "aarav@student.edu", "password": "Student@123"},
    {"name": "Priya Sharma", "email": "priya@student.edu", "password": "Student@123"},
    {"name": "Rahul Desai", "email": "rahul@student.edu", "password": "Student@123"},
]

DRIVERS = [
    {
        "name": "Suresh Pawar",
        "phone": "+91 98220 11111",
        "email": "suresh@driver.com",
        "password": "Driver@123",
        "vehicle_type": "auto",
        "vehicle_details": "MH-15 AG 1234, Yellow Auto",
        "service_area": "Nashik Road"
    },
    {
        "name": "Ramesh Jadhav",
        "phone": "+91 98220 22222",
        "email": "ramesh@driver.com",
        "password": "Driver@123",
        "vehicle_type": "auto",
        "vehicle_details": "MH-15 BT 5678, Yellow Auto",
        "service_area": "CBS to College Road"
    },
    {
        "name": "Dinesh Bagul",
        "phone": "+91 98220 77777",
        "email": "dinesh@driver.com",
        "password": "Driver@123",
        "vehicle_type": "auto",
        "vehicle_details": "MH-15 KL 6789, Yellow Auto",
        "service_area": "Panchvati"
    },
    {
        "name": "Manoj Shirke",
        "phone": "+91 98220 33333",
        "email": "manoj@driver.com",
        "password": "Driver@123",
        "vehicle_type": "taxi",
        "vehicle_details": "MH-15 CD 9012, White Sedan",
        "service_area": "Gangapur Road"
    },
    {
        "name": "Santosh Kale",
        "phone": "+91 98220 44444",
        "email": "santosh@driver.com",
        "password": "Driver@123",
        "vehicle_type": "taxi",
        "vehicle_details": "MH-15 EF 3456, White Sedan",
        "service_area": "Dwarka Circle"
    },
    {
        "name": "Prakash More",
        "phone": "+91 98220 88888",
        "email": "prakash@driver.com",
        "password": "Driver@123",
        "vehicle_type": "taxi",
        "vehicle_details": "MH-15 MN 0123, White Innova",
        "service_area": "College Road"
    },
    {
        "name": "Vijay Patil",
        "phone": "+91 98220 55555",
        "email": "vijay@driver.com",
        "password": "Driver@123",
        "vehicle_type": "car",
        "vehicle_details": "MH-15 GH 7890, Silver Swift",
        "service_area": "Trimbak Road"
    },
    {
        "name": "Anil Sonawane",
        "phone": "+91 98220 66666",
        "email": "anil@driver.com",
        "password": "Driver@123",
        "vehicle_type": "car",
        "vehicle_details": "MH-15 IJ 2345, White i20",
        "service_area": "Satpur MIDC"
    },
]

SAMPLE_RATINGS = [
    {"rating": 5, "comment": "Very punctual and polite."},
    {"rating": 4, "comment": "Good service, comfortable ride."},
    {"rating": 3, "comment": "Reached on time but took longer route."},
    {"rating": 5, "comment": "Excellent driver, highly recommend!"},
    {"rating": 4, "comment": "Clean vehicle, fair price."},
]


def main():
    """Seed the database with sample data."""
    try:
        # Parse DATABASE_URL
        # Format: postgresql://user:password@host:port/database
        from urllib.parse import urlparse
        parsed = urlparse(DATABASE_URL)
        
        conn = psycopg2.connect(
            database=parsed.path.lstrip('/'),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432
        )
        cur = conn.cursor()

        # Insert admin
        admin_id = str(uuid.uuid4())
        cur.execute(
            """
            INSERT INTO users (id, name, email, hashed_password, role, is_active)
            VALUES (%s, %s, %s, %s, %s, %s)
            ON CONFLICT (email) DO NOTHING
            """,
            (admin_id, ADMIN["name"], ADMIN["email"], hash_password(ADMIN["password"]), ADMIN["role"], True)
        )
        print(f"[OK] Created: {ADMIN['name']}")

        # Insert students
        student_ids = []
        for student in STUDENTS:
            student_id = str(uuid.uuid4())
            student_ids.append(student_id)
            cur.execute(
                """
                INSERT INTO users (id, name, email, hashed_password, role, is_active)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                """,
                (student_id, student["name"], student["email"], hash_password(student["password"]), "student", True)
            )
            print(f"[OK] Created: {student['name']}")

        # Insert drivers
        driver_ids = []
        for driver in DRIVERS:
            driver_id = str(uuid.uuid4())
            driver_ids.append(driver_id)
            cur.execute(
                """
                INSERT INTO drivers (id, name, phone, email, hashed_password, vehicle_type, vehicle_details, service_area, is_available, is_active)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (email) DO NOTHING
                """,
                (driver_id, driver["name"], driver["phone"], driver["email"], hash_password(driver["password"]), 
                 driver["vehicle_type"], driver["vehicle_details"], driver["service_area"], True, True)
            )
            print(f"[OK] Created: {driver['name']}")

        # Insert sample ratings
        import random
        rating_count = 0
        for driver_id in driver_ids:
            for _ in range(2):  # 2 ratings per driver
                if student_ids:
                    student_id = random.choice(student_ids)
                    sample_rating = random.choice(SAMPLE_RATINGS)
                    
                    cur.execute(
                        """
                        INSERT INTO ratings (driver_id, student_id, rating, comment)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (driver_id, student_id) DO NOTHING
                        """,
                        (driver_id, student_id, sample_rating["rating"], sample_rating["comment"])
                    )
                    rating_count += 1

        # Update driver rating stats
        for driver_id in driver_ids:
            cur.execute(
                """
                UPDATE drivers
                SET avg_rating = COALESCE((SELECT ROUND(AVG(rating)::numeric, 2) FROM ratings WHERE driver_id = %s), 0.0),
                    total_ratings = COALESCE((SELECT COUNT(*) FROM ratings WHERE driver_id = %s), 0)
                WHERE id = %s
                """,
                (driver_id, driver_id, driver_id)
            )

        conn.commit()
        print(f"\nSeeding complete. {len(STUDENTS) + 1} users, {len(DRIVERS)} drivers, {rating_count} ratings inserted.")
        cur.close()
        conn.close()

    except psycopg2.Error as e:
        print(f"Database error: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
