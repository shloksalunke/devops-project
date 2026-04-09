# CampusRide Database Schema

## Database: campusride

### Users Table

```sql
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(20) NOT NULL DEFAULT 'student',
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS users_email_idx ON users(email);
CREATE INDEX IF NOT EXISTS users_is_active_idx ON users(is_active);
```

### Drivers Table

```sql
CREATE TABLE drivers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name VARCHAR(100) NOT NULL,
    phone VARCHAR(20) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    vehicle_type VARCHAR(20) NOT NULL,
    vehicle_details VARCHAR(200),
    service_area VARCHAR(200),
    photo_url VARCHAR(500),
    is_available BOOLEAN DEFAULT TRUE,
    is_active BOOLEAN DEFAULT TRUE,
    
    -- RTO Verification Fields (CRITICAL)
    verification_status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    verification_notes VARCHAR(1000),
    verified_at TIMESTAMPTZ,
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    
    avg_rating NUMERIC(3,2) DEFAULT 0.0,
    total_ratings INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS drivers_email_idx ON drivers(email);
CREATE INDEX IF NOT EXISTS drivers_vehicle_type_idx ON drivers(vehicle_type);
CREATE INDEX IF NOT EXISTS drivers_verification_status_idx ON drivers(verification_status);
CREATE INDEX IF NOT EXISTS drivers_is_active_idx ON drivers(is_active);
```

### Driver Documents Table

```sql
CREATE TABLE driver_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    document_type VARCHAR(20) NOT NULL,
    file_path VARCHAR(500) NOT NULL,
    file_name VARCHAR(255) NOT NULL,
    file_size INTEGER NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    
    -- Document Verification
    status VARCHAR(20) NOT NULL DEFAULT 'PENDING',
    rejection_reason VARCHAR(500),
    verified_by UUID REFERENCES users(id) ON DELETE SET NULL,
    expiry_date DATE,
    
    uploaded_at TIMESTAMPTZ DEFAULT NOW(),
    verified_at TIMESTAMPTZ
);

CREATE INDEX IF NOT EXISTS driver_documents_driver_id_idx ON driver_documents(driver_id);
CREATE INDEX IF NOT EXISTS driver_documents_status_idx ON driver_documents(status);
CREATE INDEX IF NOT EXISTS driver_documents_document_type_idx ON driver_documents(document_type);
```

### Ratings Table

```sql
CREATE TABLE ratings (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    rating INTEGER NOT NULL CHECK (rating >= 1 AND rating <= 5),
    comment VARCHAR(500),
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ratings_driver_id_idx ON ratings(driver_id);
CREATE INDEX IF NOT EXISTS ratings_student_id_idx ON ratings(student_id);
CREATE UNIQUE INDEX IF NOT EXISTS ratings_unique_idx ON ratings(driver_id, student_id);
```

### Ride Contacts Table

```sql
CREATE TABLE ride_contacts (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    student_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    driver_id UUID NOT NULL REFERENCES drivers(id) ON DELETE CASCADE,
    contacted_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE INDEX IF NOT EXISTS ride_contacts_student_id_idx ON ride_contacts(student_id);
CREATE INDEX IF NOT EXISTS ride_contacts_driver_id_idx ON ride_contacts(driver_id);
```

---

## Data Relationships

```
Users (Students/Admins)
├── verified_by ──→ Drivers.verified_by
├── rating.student_id ──→ Ratings
└── ride_contact.student_id ──→ Ride Contacts

Drivers
├── verified_by ──→ Users (Admin)
├── driver_documents ──→ Driver Documents (1:N)
├── ratings ──→ Ratings (1:N)
└── ride_contacts ──→ Ride Contacts (1:N)

Driver Documents
└── verified_by ──→ Users (Admin)
```

---

## Sample Seed Data

### Users (Students)

```sql
INSERT INTO users (name, email, hashed_password, role, is_active) VALUES
('Aarav Mehta', 'aarav@student.edu', 'bcrypt_hash', 'student', true),
('Priya Sharma', 'priya@student.edu', 'bcrypt_hash', 'student', true),
('Admin User', 'admin@campusride.com', 'bcrypt_hash', 'admin', true);
```

### Drivers (PENDING)

```sql
INSERT INTO drivers (
    name, phone, email, hashed_password, vehicle_type,
    vehicle_details, service_area, verification_status,
    is_active, is_available
) VALUES
('Suresh Pawar', '9876543210', 'suresh@campusride.com', 'bcrypt_hash',
 'auto', 'MH-15 AG 1234', 'Nashik Road', 'PENDING', false, false),
('Raj Kumar', '9234567890', 'raj@campusride.com', 'bcrypt_hash',
 'bike', 'MH-02 AB 5678', 'Pune Road', 'PENDING', false, false);
```

### Admin User

```sql
INSERT INTO users (name, email, hashed_password, role)
VALUES ('Admin', 'admin@campusride.com', 
        '$2b$12$...[bcrypt_hash]...', 'admin');
```

Credentials: `admin@campusride.com` / `Admin@123`

---

## Data Flow

### Driver Registration Flow

1. **Driver registers** via `/auth/register-driver`
   - Driver created with `verification_status = 'PENDING'`
   - `is_active = false`
   - Documents stored in `driver_documents` table

2. **Admin reviews** via `/admin/drivers/pending`
   - Admin can view pending drivers and their documents
   - Admin can approve/reject specific documents

3. **All documents approved** 
   - Admin clicks approve via `/admin/drivers/{driver_id}/approve`
   - Driver `verification_status` → `'APPROVED'`
   - Driver `is_active` → `true`

4. **Driver visible to students**
   - Students see driver in `/drivers` listing
   - Students can rate driver

### Rating Flow

1. **Student logs contact** via `/drivers/{driver_id}/contacts`
   - Entry in `ride_contacts` table

2. **Student submits rating** via `/drivers/{driver_id}/ratings`
   - Entry in `ratings` table
   - Driver's `avg_rating` and `total_ratings` updated

3. **Driver ratings visible**
   - At `/drivers/{driver_id}` with all ratings

---

## Query Examples

### Get all APPROVED drivers

```sql
SELECT * FROM drivers 
WHERE is_active = true 
AND verification_status = 'APPROVED'
ORDER BY avg_rating DESC;
```

### Get pending drivers for admin review

```sql
SELECT d.*, COUNT(dd.id) as doc_count
FROM drivers d
LEFT JOIN driver_documents dd ON d.id = dd.driver_id
WHERE d.verification_status = 'PENDING'
GROUP BY d.id
ORDER BY d.created_at DESC;
```

### Get driver with ratings

```sql
SELECT 
    d.*,
    COUNT(r.id) as rating_count,
    AVG(r.rating) as avg_rating_calc
FROM drivers d
LEFT JOIN ratings r ON d.id = r.driver_id
WHERE d.id = $1
GROUP BY d.id;
```

### Get student ride contacts

```sql
SELECT rc.*, d.name, d.vehicle_type, d.phone
FROM ride_contacts rc
JOIN drivers d ON rc.driver_id = d.id
WHERE rc.student_id = $1
ORDER BY rc.contacted_at DESC;
```

### Count statistics

```sql
SELECT 
    COUNT(DISTINCT CASE WHEN u.role = 'student' THEN u.id END) as total_students,
    COUNT(DISTINCT CASE WHEN d.verification_status = 'APPROVED' THEN d.id END) as approved_drivers,
    COUNT(DISTINCT CASE WHEN d.verification_status = 'PENDING' THEN d.id END) as pending_drivers,
    COUNT(r.id) as total_ratings
FROM users u
FULL OUTER JOIN drivers d ON TRUE
LEFT JOIN ratings r ON TRUE;
```

---

## Backup & Recovery

### Backup

```bash
# Full backup
pg_dump -U postgres campusride > campusride_backup.sql

# Compressed backup
pg_dump -U postgres campusride | gzip > campusride_backup.sql.gz
```

### Restore

```bash
# From SQL file
psql -U postgres -d campusride -f campusride_backup.sql

# From compressed file
gunzip -c campusride_backup.sql.gz | psql -U postgres -d campusride
```

---

## Performance Optimization

### Indexes Created
- ✅ `users.email` - For login lookups
- ✅ `users.is_active` - For filtering active users
- ✅ `drivers.email` - For driver login
- ✅ `drivers.vehicle_type` - For filtering drivers
- ✅ `drivers.verification_status` - For admin filtering
- ✅ `drivers.is_active` - For visibility filtering
- ✅ `driver_documents.driver_id` - For document lookups
- ✅ `driver_documents.status` - For filtering documents
- ✅ `ratings.driver_id` - For driver ratings
- ✅ `ratings.student_id` - For student ratings
- ✅ `ratings.(driver_id, student_id)` - UNIQUE for duplicate prevention
- ✅ `ride_contacts.student_id` - For student contacts
- ✅ `ride_contacts.driver_id` - For contact tracking

### Query Optimization
- ✅ Composite indexes for frequently joined tables
- ✅ UNIQUE constraint on ratings to prevent duplicates
- ✅ Foreign key cascades for data integrity
- ✅ Timezone-aware timestamps

---

## Migration Strategy (Alembic)

### Create migration
```bash
cd backend
alembic revision --autogenerate -m "Add new field"
```

### Apply migration
```bash
alembic upgrade head
```

### Rollback migration
```bash
alembic downgrade -1
```

### View migration history
```bash
alembic current
alembic history
```

---

## Data Validation Rules

### Users
- ✅ Email must be unique and valid
- ✅ Name: 1-100 characters
- ✅ Password: minimum 8 characters (bcrypt hashed)
- ✅ Role: 'student', 'driver', or 'admin'

### Drivers
- ✅ Email must be unique
- ✅ Phone: 10-20 digits
- ✅ Vehicle type: must be specified
- ✅ Verification status: PENDING, APPROVED, REJECTED, SUSPENDED
- ✅ Rating: 1-5 stars

### Documents
- ✅ Document type: ID, LICENSE, RC
- ✅ Max file size: 5MB
- ✅ Allowed formats: PDF, JPG, JPEG, PNG

---

## Constraints & Triggers

### Constraints
- ✅ PRIMARY KEY on all tables (UUID)
- ✅ UNIQUE on emails
- ✅ FOREIGN KEY relationships with CASCADE deletes
- ✅ CHECK constraint on ratings (1-5)
- ✅ DEFAULT values for timestamps and booleans
- ✅ UNIQUE index on (driver_id, student_id) for ratings

### Automatic Updates
- ✅ `updated_at` timestamp auto-updates on record modification
- ✅ `created_at` timestamp auto-set on row creation
- ✅ Driver rating stats updated after each rating

---

## Transactions

### Critical Operations
- ✅ Driver approval (atomic status + is_active update)
- ✅ Rating submission (rating creation + stats update)
- ✅ Document verification (document status + timestamp update)
