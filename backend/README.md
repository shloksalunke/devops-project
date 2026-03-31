# NM-Ride Backend

FastAPI backend for the NM-Ride shared transport and ride-sharing management app.

**Frontend location:** D:\Devops_project\frontend  
**Backend location:** D:\Devops_project\backend

## Prerequisites

- Python 3.11+
- PostgreSQL 15 running on localhost:5432
- Node.js (for frontend, separate)

## Quick Start — Local (Windows)

### Step 1: Setup Python Environment

```bash
cd D:\Devops_project\backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### Step 2: Create Database

```bash
psql -U postgres -c "CREATE DATABASE nmride;"
```

### Step 3: Initialize Database (Choose One Method)

**Option A: Using raw SQL schema**
```bash
psql -U postgres -d nmride -f scripts/schema.sql
```

**Option B: Using Alembic migrations**
```bash
alembic upgrade head
```

### Step 4: Seed Sample Data

```bash
python scripts/seed.py
```

### Step 5: Start Development Server

```bash
uvicorn app.main:app --reload --port 8000
```

**API available at:** http://localhost:8000
**Swagger docs:** http://localhost:8000/docs  (only when DEBUG=True in .env)
**ReDoc docs:** http://localhost:8000/redoc

## Quick Start — Docker

```bash
cd D:\Devops_project\backend
docker-compose up --build -d
docker-compose exec api alembic upgrade head
docker-compose exec api python scripts/seed.py
```

View logs:
```bash
docker-compose logs -f api
```

Stop containers:
```bash
docker-compose down
```

## Running Tests

Run all tests:
```bash
pytest tests/ -v
```

Run with coverage:
```bash
pytest tests/ -v --cov=app --cov-report=term-missing
```

Run specific test file:
```bash
pytest tests/test_auth.py -v
```

## Project Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app factory
│   ├── config.py            # Settings from .env
│   ├── database.py          # SQLAlchemy setup
│   ├── exceptions.py        # Custom exceptions
│   ├── middleware.py        # Request/response middleware
│   ├── dependencies.py      # FastAPI dependencies
│   ├── models/              # SQLAlchemy ORM models
│   ├── schemas/             # Pydantic request/response schemas
│   ├── repositories/        # Data access layer
│   ├── services/            # Business logic
│   └── routers/             # API endpoints
├── alembic/                 # Database migrations
├── scripts/                 # Utility scripts
├── tests/                   # Pytest test cases
├── .env                     # Dev environment variables (pre-filled)
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker image config
└── docker-compose.yml       # Multi-container setup
```

## API Endpoints

### Authentication
- `POST /auth/register` — Register new student
- `POST /auth/login` — Login user/driver
- `POST /auth/refresh` — Refresh access token

### Users (Protected)
- `GET /users/me` — Get current user
- `PUT /users/me` — Update profile
- `GET /users/me/contacts` — Get ride contacts

### Drivers (Public Read, Auth Required)
- `GET /drivers` — List all drivers
- `GET /drivers/{id}` — Get driver details with ratings
- `POST /drivers/{id}/contacts` — Log driver contact
- `POST /drivers/{id}/ratings` — Submit rating

### Driver Portal (Driver Only)
- `GET /driver/me` — Get driver profile
- `PUT /driver/me` — Update profile
- `PUT /driver/me/availability` — Set availability
- `GET /driver/me/ratings` — Get driver ratings

### Admin (Admin Only)
- `GET /admin/stats` — Dashboard statistics
- `GET /admin/drivers` — List all drivers
- `POST /admin/drivers` — Create driver
- `PUT /admin/drivers/{id}` — Update driver
- `DELETE /admin/drivers/{id}` — Deactivate driver
- `GET /admin/users` — List all users

### Health
- `GET /health` — API health check

## Frontend Connection

The React frontend at D:\Devops_project\frontend connects to the backend using:

```javascript
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL;
// Value: http://localhost:8000
```

CORS is pre-configured for:
- `http://localhost:3000` (Node / React dev server)
- `http://127.0.0.1:3000`

## Default Credentials (After Seeding)

| Role  | Email                    | Password   |
|-------|--------------------------|-----------|
| Admin | admin@nm-ride.com       | Admin@123 |
| Student | aarav@student.edu      | Student@123 |
| Driver | suresh@driver.com       | Driver@123 |

## Environment Variables

See `.env` file for all configuration. Key variables:

```
APP_ENV=development|production
DEBUG=True|False
DATABASE_URL=postgresql://user:password@host:port/dbname
SECRET_KEY=your-secret-key-min-32-chars
ALLOWED_ORIGINS=["http://localhost:3000","http://127.0.0.1:3000"]
RATE_LIMIT_PER_MINUTE=60
```

## Database Schema

### Users Table
- UUID primary key
- Email (unique)
- Role: "student" | "admin"
- Timestamps (created_at, updated_at)

### Drivers Table
- UUID primary key
- Email (unique)
- Vehicle type: "auto" | "taxi" | "car"
- Average rating (calculated, 0-5)
- Total ratings count
- Availability status

### Ratings Table
- UUID primary key
- Driver ID (FK)
- Student ID (FK)
- Rating: 1-5 (with constraint)
- Comment (optional)
- Unique constraint on (driver_id, student_id)

### Ride Contacts Table
- UUID primary key
- Student ID (FK)
- Driver ID (FK)
- Contact timestamp

## Architecture

- **Routers** → Handle HTTP requests, validation, authentication
- **Services** → Business logic, data transformation
- **Repositories** → Database queries, ORM operations
- **Models** → SQLAlchemy ORM definitions
- **Schemas** → Pydantic validation and serialization

No raw SQL queries outside repositories. No business logic in routers or repositories.

## Technologies

- **Framework:** FastAPI 0.110+
- **ORM:** SQLAlchemy 2.0
- **Database:** PostgreSQL 15
- **Auth:** JWT (python-jose) + passlib bcrypt
- **Validation:** Pydantic 2.0
- **Rate Limiting:** slowapi
- **Testing:** pytest + pytest-asyncio
- **Migrations:** Alembic

## Common Issues

### Port 5432 Already in Use
```bash
# Find and stop existing PostgreSQL
netstat -ano | findstr :5432
taskkill /PID <PID> /F
```

### ModuleNotFoundError: No module named 'app'
Make sure you're running commands from the backend directory and venv is activated.

### Database Connection Error
Check `.env` file DATABASE_URL matches your PostgreSQL credentials.

### CORS Errors
Add frontend URL to `ALLOWED_ORIGINS` in `.env`.

## Troubleshooting

**Check health endpoint:**
```bash
curl http://localhost:8000/health
```

**View API documentation:**
Open http://localhost:8000/docs in browser (if DEBUG=True)

**Test database connection:**
```bash
psql -U postgres -d nmride -c "SELECT NOW();"
```

**Reset database:**
```bash
psql -U postgres -d campusride -f scripts/schema.sql
python scripts/seed.py
```

## Deployment

For production:

1. Set `DEBUG=False` in `.env`
2. Use strong `SECRET_KEY` (min 32 chars)
3. Update `DATABASE_URL` for production DB
4. Update `ALLOWED_ORIGINS` for production frontend
5. Use environment-specific `.env` file
6. Run with production ASGI server:
   ```bash
   gunicorn -w 4 -k uvicorn.workers.UvicornWorker app.main:app
   ```

## Support

For issues or questions, check:
- API docs at `/docs`
- Project README at `D:\Devops_project\README.md`
- Frontend README at `D:\Devops_project\frontend\README.md`
