# RTO Verification System Migration Guide

## Overview

This document guides you through applying the database migration for the RTO Verification System. This migration adds:

1. **Driver Verification Fields** - Status tracking for driver approval
2. **Driver Documents Table** - Centralized storage for driver documents (ID, License, RC, Insurance)
3. **Performance Indexes** - Optimized queries for verification workflow

## Prerequisites

- PostgreSQL database running and accessible
- Backend environment properly configured (`.env` or environment variables)
- Alembic installed (included in `requirements.txt`)
- Database user with CREATE/ALTER table permissions

## Migration Steps

### Option 1: Using Alembic (Recommended)

#### Step 1: Verify Alembic Configuration
```bash
cd backend
# Check alembic.ini is configured correctly
cat alembic.ini
```

#### Step 2: Run the Migration
```bash
# Apply the migration to your database
alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl with PostgreSQL 12.x dialect
INFO  [alembic.runtime.migration] Will assume transactional DDL is supported by the database
INFO  [alembic.runtime.migration] Running upgrade  -> 001, add rto verification
```

#### Step 3: Verify Migration Success
```bash
# Check migration history
alembic current

# Connect to your database and verify tables exist
psql -U postgres -d your_db_name
\dt  # List all tables
\d driver_documents  # Check driver_documents table structure
\d drivers  # Verify drivers table has new columns
```

### Option 2: Manual SQL Execution

If Alembic is not available, run the SQL directly:

```bash
psql -U postgres -d your_db_name < backend/scripts/schema.sql
```

### Option 3: Docker Database Migration

If running PostgreSQL in Docker:

```bash
# Copy migration script into container
docker cp backend/scripts/schema.sql container_name:/tmp/

# Execute migration inside container
docker exec container_name psql -U postgres -d your_db_name -f /tmp/schema.sql
```

## Database Changes

### New Columns in `drivers` Table

| Column | Type | Default | Details |
|--------|------|---------|---------|
| `verification_status` | VARCHAR(20) | 'PENDING' | PENDING, APPROVED, REJECTED, SUSPENDED |
| `verification_notes` | VARCHAR(1000) | NULL | Admin notes on verification decision |
| `verified_at` | TIMESTAMPTZ | NULL | Timestamp when driver was verified |
| `verified_by` | UUID | NULL | Reference to admin user who verified |

### New Table: `driver_documents`

```
Columns:
- id (UUID, Primary Key)
- driver_id (UUID, Foreign Key to drivers)
- document_type (VARCHAR) - ID, LICENSE, RC, INSURANCE
- file_path (VARCHAR) - Server file path
- file_name (VARCHAR) - Original filename
- file_size (INTEGER) - File size in bytes
- file_type (VARCHAR) - MIME type (pdf, jpeg, etc.)
- status (VARCHAR) - PENDING, APPROVED, REJECTED
- rejection_reason (VARCHAR) - Why document was rejected
- uploaded_at (TIMESTAMPTZ) - When uploaded
- verified_at (TIMESTAMPTZ) - When verified by admin
- verified_by (UUID) - Admin who verified
- expiry_date (TIMESTAMPTZ) - Document expiry if applicable
```

### New Indexes

```
idx_drivers_verification_status       - Query drivers by verification status
idx_driver_documents_driver_id        - Lookup documents for a driver
idx_driver_documents_document_type    - Find all documents of specific type
idx_driver_documents_status           - Find documents by approval status
```

## Verification Steps

### 1. Check Migration Applied
```sql
-- Connect to your database
psql -U postgres -d your_db_name

-- Check drivers table has new columns
\d drivers

-- Should show columns like:
-- verification_status | character varying(20)
-- verification_notes | character varying(1000)
-- verified_at | timestamp with time zone
-- verified_by | uuid
```

### 2. Verify driver_documents Table
```sql
-- List all tables
\dt

-- Should include: driver_documents

-- Check table structure
\d driver_documents

-- List indexes
\di
```

### 3. Check Constraints
```sql
-- Verify check constraints exist
SELECT constraint_name, constraint_type 
FROM information_schema.table_constraints 
WHERE table_name = 'driver_documents';
```

### 4. Test Insertion
```sql
-- Verify you can insert with correct verification_status
INSERT INTO drivers (name, phone, email, hashed_password, vehicle_type, verification_status)
VALUES ('Test Driver', '9876543210', 'test@example.com', 'hashed_pwd', 'auto', 'PENDING');

-- Verify constraint works (this should fail)
INSERT INTO drivers (name, phone, email, hashed_password, vehicle_type, verification_status)
VALUES ('Bad Driver', '9876543211', 'bad@example.com', 'hashed_pwd', 'auto', 'INVALID_STATUS');
-- Error: new row for relation "drivers" violates check constraint (expected)
```

## Rollback Instructions

### If Using Alembic
```bash
# Downgrade to previous version
alembic downgrade -1

# Or downgrade all migrations
alembic downgrade base
```

### Manual Rollback (Advanced)
```sql
-- DROP driver_documents table
DROP TABLE IF EXISTS driver_documents CASCADE;

-- Remove columns from drivers
ALTER TABLE drivers DROP COLUMN IF EXISTS verification_status;
ALTER TABLE drivers DROP COLUMN IF EXISTS verification_notes;
ALTER TABLE drivers DROP COLUMN IF EXISTS verified_at;
ALTER TABLE drivers DROP COLUMN IF EXISTS verified_by;

-- Remove indexes
DROP INDEX IF EXISTS idx_drivers_verification_status;
```

## Backend Integration

The migration is automatically integrated with:

1. **app/models/driver.py** - Updated Driver ORM model
2. **app/models/driver_document.py** - New DriverDocument model
3. **app/repositories/driver_repo.py** - New query methods for verification
4. **app/repositories/driver_document_repo.py** - Document CRUD operations
5. **app/services/driver_service.py** - Verification business logic
6. **app/routers/admin.py** - New verification endpoints

After migration, restart the backend:
```bash
cd backend
python main.py
# or
uvicorn app.main:app --reload
```

## Frontend Integration

The migration enables these new frontend features:

1. **Admin Dashboard** - "Pending Verification" tab shows drivers awaiting approval
2. **Document Viewer** - Admin can review uploaded documents
3. **Approval Workflow** - Admin can approve/reject with notes
4. **Driver Registration** - Shows PENDING status after registration

No frontend migration needed - all changes are automatic.

## Testing the Complete Flow

### 1. Driver Registration
```bash
# Register as a driver at:
http://localhost:3000/driver-register

# Fill form and upload ID + License
# Should show "Verification Status: PENDING" on success
```

### 2. Admin Verification
```bash
# Login as admin at:
http://localhost:3000/admin

# Go to "Pending Verification" tab
# Should show registered driver
# Click "Review" to see documents
# Click "Approve" or "Reject"
```

### 3. Driver Visibility
```bash
# Login as student
# View available drivers at: http://localhost:3000

# Should show ONLY drivers with verification_status = 'APPROVED'
# Pending drivers should NOT appear
```

## Troubleshooting

### Migration Fails with "Column Already Exists"
- Database may have partial migration
- Drop the entire database and re-run migration, OR
- Manually remove conflicting columns first

### Foreign Key Constraint Errors  
- Ensure users table exists first
- Check that all referenced UUIDs exist

### Alembic "No Migrations Created"
- Verify alembic/versions/ directory exists
- Check alembic.ini has correct sqlalchemy.url
- Try: `alembic upgrade head`

### Driver Documents Not Showing in Admin
- Check migration ran: `SELECT * FROM driver_documents;`
- Verify documents were uploaded: `SELECT * FROM driver_documents WHERE driver_id = '...'`
- Check file_path exists on server

## Support

If you encounter issues:

1. Check PostgreSQL logs: `/var/log/postgresql/`
2. Verify Alembic current version: `alembic current`
3. Check migration history: `alembic history --verbose`
4. Review backend logs for API errors
5. Test database connectivity: `psql -U postgres -d db_name -c "SELECT version();"`
