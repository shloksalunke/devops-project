# NM-Ride Architecture Overview

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (Port 3000)                     │
│                  React + TypeScript + Vite + Tailwind           │
│  ┌──────────────┬──────────────┬──────────────┬──────────────┐   │
│  │  Student     │   Driver     │    Admin     │  Components  │   │
│  │   Portal     │   Portal     │   Dashboard  │  & Pages     │   │
│  └──────────────┴──────────────┴──────────────┴──────────────┘   │
└────────────┬────────────────────────────────────────────────────┘
             │ HTTP/REST/JSON
             ↓
┌─────────────────────────────────────────────────────────────────┐
│                    API Gateway (Port 8000)                       │
│                  FastAPI Application Server                      │
│  ┌────────────────────────────────────────────────────────────┐ │
│  │ CORS │ Auth │ Validation │ Error Handling │ Rate Limiting │ │
│  └────────┬──────────────────────────────────────────────────┘ │
│           │                                                     │
│  ┌────────┴──────────────────────────────────────────────────┐ │
│  │              Router Layer (5 Routers)                     │ │
│  │  ┌──────────┬──────────┬──────────┬──────────┬──────────┐ │ │
│  │  │  Auth    │  Users   │ Drivers  │  Driver  │  Admin   │ │ │
│  │  │ Router   │ Router   │ Router   │  Portal  │ Router   │ │ │
│  │  └──────────┴──────────┴──────────┴──────────┴──────────┘ │ │
│  │                                                             │ │
│  │  ┌──────────────────────────────────────────────────────┐ │ │
│  │  │         Service Layer (3 Services)                  │ │ │
│  │  │  ┌──────────┬──────────────┬──────────────────────┐ │ │ │
│  │  │  │   Auth   │    Driver    │      Rating        │ │ │ │
│  │  │  │ Service  │   Service    │     Service        │ │ │ │
│  │  │  └──────────┴──────────────┴──────────────────────┘ │ │ │
│  │  │                                                      │ │ │
│  │  │  ┌──────────────────────────────────────────────────┐ │ │
│  │  │  │    Repository Layer (5 Repositories)           │ │ │
│  │  │  │  ┌────────┬────────┬────────┬────────┬─────────┐│ │ │
│  │  │  │  │ User   │ Driver │ Driver │ Rating │ Driver  ││ │ │
│  │  │  │  │ Repo   │ Repo   │ Doc    │ Repo   │ Doc     ││ │ │
│  │  │  │  │        │        │ Repo   │        │ Repo    ││ │ │
│  │  │  │  └────────┴────────┴────────┴────────┴─────────┘│ │ │
│  │  │  └──────────────────────────────────────────────────┘ │ │
│  └───────────┬──────────────────────────────────────────────┘ │
│              │ SQLAlchemy ORM                                 │
│              ↓                                                 │
│  ┌────────────────────────────────────────────────────────┐ │
│  │         Model Layer (5 SQLAlchemy Models)             │ │
│  │  ┌──────────┬──────────┬──────────┬────────┬──────────┐ │ │
│  │  │  User    │  Driver  │ Driver   │Rating  │ Ride     │ │ │
│  │  │  Model   │  Model   │ Document │ Model  │ Contact  │ │ │
│  │  │          │          │  Model   │        │ Model    │ │ │
│  │  └──────────┴──────────┴──────────┴────────┴──────────┘ │ │
│  └────────────────────────────────────────────────────────┘ │
└─────────────────┬────────────────────────────────────────────┘
                  │ PostgreSQL Protocol
                  ↓
        ┌─────────────────────────┐
        │  PostgreSQL 15          │
        │  Database (nmride)      │
        │  ┌─────────────────────┐│
        │  │  5 Tables           ││
        │  │  12 Indexes         ││
        │  │  Foreign Keys       ││
        │  │  Constraints        ││
        │  └─────────────────────┘│
        │  ┌─────────────────────┐│
        │  │  Volume Storage     ││
        │  │  pgdata/            ││
        │  └─────────────────────┘│
        └─────────────────────────┘
                  ↓
        ┌─────────────────────────┐
        │  Redis 7 (Cache)        │
        │  Session Storage        │
        │  Rate Limiting Counters │
        └─────────────────────────┘
```

---

## API Flow Diagram

```
┌────────────────────────────────────────────────────────────────┐
│                      Student User                               │
└────────────────────┬─────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ↓                         ↓
    Register            Login
    (Student)           (Student/Driver)
        │                    │
        └────────┬───────────┘
                 │
            GET JWT Tokens
         (Access + Refresh)
                 │
        ┌────────┴────────────────────────┐
        │                                 │
        ↓                                 ↓
    Student                        Driver
    Services                       Services
        │                              │
    ├── View Drivers            ├── Manage Profile
    ├── Rate Drivers            ├── Set Availability
    ├── View Ratings            ├── View Ratings
    ├── Log Contacts            └── View Contacts
    └── Profile Management      
        │                                 │
        └─────────────┬────────────────────┘
                      │
              ┌───────┴───────┐
              │               │
              ↓               ↓
         Admin Login      Admin Services
              │               │
              └───────────────┴───────────────┐
                                             │
         ├── Verify Drivers                 │
         ├── Review Documents               │
         ├── Approve/Reject Drivers    Admin
         ├── Suspend Drivers           Panel
         ├── View Statistics           │
         └── Manage all Users          │
                                       ↓
```

---

## Database Relationship Diagram

```
Users (Students/Admins)
├─ id (UUID, PK)
├─ name
├─ email (UNIQUE)
├─ hashed_password
├─ role ('student', 'driver', 'admin')
├─ is_active
├─ created_at
└─ updated_at

    ↑ (verified_by)
    │
    │
    ↓ (1:Many)

Drivers
├─ id (UUID, PK)
├─ name
├─ email (UNIQUE)
├─ hashed_password
├─ phone
├─ vehicle_type
├─ vehicle_details
├─ service_area
├─ is_available
├─ is_active
├─ verification_status (PENDING/APPROVED/REJECTED/SUSPENDED)
├─ verification_notes
├─ verified_at
├─ verified_by (FK → Users)
├─ avg_rating
├─ total_ratings

    ├─↓ (1:Many)
    │
    ├── Driver_Documents
    │   ├─ id (UUID, PK)
    │   ├─ driver_id (FK)
    │   ├─ document_type (ID/LICENSE/RC)
    │   ├─ file_path
    │   ├─ file_name
    │   ├─ file_size
    │   ├─ status (PENDING/APPROVED/REJECTED)
    │   ├─ verified_by (FK → Users)
    │   ├─ uploaded_at
    │   └─ verified_at
    │
    ├── Ratings (1:Many)
    │   ├─ id (UUID, PK)
    │   ├─ driver_id (FK)
    │   ├─ student_id (FK → Users)
    │   ├─ rating (1-5)
    │   ├─ comment
    │   └─ created_at
    │   (UNIQUE Constraint: driver_id + student_id)
    │
    └── Ride_Contacts (1:Many)
        ├─ id (UUID, PK)
        ├─ driver_id (FK)
        ├─ student_id (FK → Users)
        └─ contacted_at
```

---

## Authentication Flow

```
Client Request
     │
     ├─ POST /auth/register
     │   └─ Create User
     │       └─ Generate Tokens
     │
     ├─ POST /auth/register-driver
     │   └─ Create Driver (PENDING)
     │       └─ Store Documents
     │           └─ Generate Tokens
     │
     └─ POST /auth/login
         └─ Verify Email + Password
             └─ Generate Tokens

Generated Tokens:
├─ Access Token
│   ├─ Expires: 30 minutes
│   ├─ Contains: user_id, type, exp
│   └─ Algorithm: HS256
│
└─ Refresh Token
    ├─ Expires: 7 days
    ├─ Contains: user_id, type, exp
    └─ Algorithm: HS256

Every Protected Endpoint:
├─ Extract token from Authorization header
├─ Decode and verify JWT
├─ Check token expiry
├─ Get user from database
├─ Verify role permissions
└─ Allow/Deny access
```

---

## Driver Verification Workflow

```
Driver Registers
     │
     ├── POST /auth/register-driver
     │   ├── Create Driver (is_active=false)
     │   ├── verification_status = "PENDING"
     │   └── Store Documents in driver_documents
     │
     └─→ Driver Inactive
         └─→ Not visible to students
             └─→ Can't receive ratings

Admin Reviews
     │
     ├── GET /admin/drivers/pending
     │   └── See all PENDING drivers
     │
     ├── GET /admin/drivers/{id}/verification-status
     │   └── View driver details + documents
     │
     └─→ Review each document
         └─→ Approve or Reject

Document Review
     ├─ ID Document (Aadhaar/PAN)
     ├─ Driving License
     └─ Vehicle RC (Registration Certificate)

All Documents APPROVED?
     │
     ├─ YES → PUT /admin/drivers/{id}/approve
     │   ├── verification_status = "APPROVED"
     │   ├── is_active = true
     │   ├── verified_at = NOW()
     │   └── verified_by = admin_id
     │
     └─ NO → PUT /admin/drivers/{id}/reject
         ├── verification_status = "REJECTED"
         ├── is_active = false
         └── Send rejection reason

Driver Approved!
     └─→ Becomes visible to students
         └─→ Can be viewed, rated, contacted
             └─→ Appears in driver list
                 └─→ Can receive ride requests
```

---

## Request-Response Cycle

```
Client Browser              API Server              Database
     │                           │                       │
     │─ GET /drivers ───────────→│                       │
     │   (With Bearer Token)     │                       │
     │                           ├─ Validate Token      │
     │                           ├─ Check CORS          │
     │                           ├─ Check Rate Limit    │
     │                           │                       │
     │                           ├─ Query Drivers ──────→│
     │                           │ (APPROVED, is_active) │
     │                           │                       │
     │                           │←─ Return Data ────────┤
     │                           │                       │
     │                           ├─ Add Headers:        │
     │                           │  X-Request-ID        │
     │                           │  X-Process-Time      │
     │                           │                       │
     │←──── 200 OK Response ─────│                       │
     │ [Drivers Array]           │                       │
     │ Headers: CORS + Timing    │                       │

Status Codes:
├─ 200 OK - Success
├─ 201 Created - Resource created
├─ 400 Bad Request - Invalid input
├─ 401 Unauthorized - Auth failed
├─ 403 Forbidden - Permission denied
├─ 404 Not Found - Resource not found
├─ 409 Conflict - Resource conflict
└─ 500 Server Error
```

---

## Security Layers

```
Request → [CORS Middleware]
           ↓
           [Trusted Host Middleware]
           ↓
           [Auth Middleware]
           ├─ Check Authorization header
           ├─ Validate JWT Token
           ├─ Get User from Database
           └─ Attach to request context
           ↓
           [Request Validation]
           ├─ Email format
           ├─ Password strength
           ├─ File upload size
           └─ Field length
           ↓
           [Business Logic]
           ├─ Role-based access control
           ├─ Database validation
           └─ Business rules
           ↓
           [Exception Handler]
           ├─ Catch exceptions
           ├─ Format error response
           └─ Return appropriate status
           ↓
           [Response] → [Timing Middleware] → Client
```

---

## Data Flow for Rating Submission

```
Student → Frontend (React)
  ↓
  POST /drivers/{driver_id}/ratings
  {
    "rating": 5,
    "comment": "Great service!"
  }
  ↓
  [Auth Validation]
  - Check JWT token
  - Verify student user
  ↓
  [Rating Service]
  1. Check driver exists
  2. Check no duplicate rating
  3. Create rating record
  4. Update driver stats
  ↓
  [Database]
  - INSERT INTO ratings
  - UPDATE drivers SET avg_rating, total_ratings
  ↓
  [Response]
  201 Created
  {
    "id": "uuid",
    "rating": 5,
    "comment": "Great service!",
    "created_at": "2024-01-15"
  }
  ↓
  Frontend updates UI
  - Shows confirmation
  - Refreshes driver ratings
  - Updates statistics
```

---

## Deployment Architecture

```
┌─────────────────────────────────────────┐
│         Docker Compose Stack            │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────────────────────────────┐   │
│  │   nginx (Reverse Proxy)         │   │
│  │   Port 80/443                   │   │
│  └────────────┬────────────────────┘   │
│               │                        │
│    ┌──────────┴──────────┐             │
│    │                     │             │
│    ↓                     ↓             │
│  ┌──────────────┐  ┌──────────────┐   │
│  │  Frontend    │  │   Backend    │   │
│  │  Port 3000   │  │   Port 8000  │   │
│  │  React/Vite  │  │  FastAPI     │   │
│  └──────────────┘  └──────┬───────┘   │
│                           │           │
│         ┌─────────────────┼───────┐   │
│         │                 │       │   │
│         ↓                 ↓       ↓   │
│    ┌─────────────┐  ┌─────────┐ ┌───┐│
│    │ PostgreSQL  │  │ Redis   │ │...││
│    │ Port 5432   │  │ Port    │ └───┘│
│    │             │  │ 6379    │      │
│    └─────────────┘  └─────────┘      │
│                                       │
└─────────────────────────────────────────┘
```

---

## Performance Optimization

```
Query Performance:
├─ Email lookups: O(1) with index
├─ Status filtering: O(1) with index
├─ Join operations: Optimized with foreign keys
├─ Rating calculation: Atomic SQL update
└─ Connection pooling: 10-20 connections

Caching Strategy:
├─ Redis for session storage
├─ Token blacklist (for logout)
├─ Rate limiting counters
└─ Frequently accessed data

Response Optimization:
├─ Pagination (20-100 items/page)
├─ Lazy loading for relationships
├─ Selective field loading
└─ Compression enabled

Database Optimization:
├─ Connection pooling
├─ Query timeout: 5 seconds
├─ Index usage: 12 strategic indexes
└─ VACUUM maintenance schedule
```

---

## Monitoring & Logging

```
Application Logging:
├─ Request ID tracking (X-Request-ID)
├─ Processing time tracking (X-Process-Time)
├─ Error logging with stack traces
├─ Authentication events
└─ Database operations

Metrics to Track:
├─ API response times
├─ Database query times
├─ Error rates
├─ User registration trends
├─ Driver approvals
├─ Rating submissions
└─ Rate limit violations

Health Checks:
├─ GET /health endpoint
├─ Database connectivity test
├─ Redis connectivity test
└─ External service checks
```

---

## File Upload Storage

```
/uploads/drivers/
├─ {driver_id}/
│  ├── ID_{uuid}_{filename}
│  ├── License_{uuid}_{filename}
│  └── RC_{uuid}_{filename}

File Validation:
├─ Max size: 5MB
├─ Allowed: PDF, JPG, JPEG, PNG
├─ Virus scanning: (Optional)
└─ Malware detection: (Optional)

File Integrity:
├─ File hash stored in DB
├─ Version control
├─ Backup procedures
└─ Retention policy
```

This architecture ensures scalability, security, and maintainability of the NM-Ride platform.
