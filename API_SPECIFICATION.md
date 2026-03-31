# NM-Ride API Specification

**Base URL:** `http://localhost:8000`
**API Version:** 1.0.0
**Documentation:** `/docs` (Swagger UI) | `/redoc` (ReDoc)

---

## Authentication

All protected endpoints require a Bearer token in the `Authorization` header:
```
Authorization: Bearer {access_token}
```

### Token Structure
- **Access Token:** Expires in 30 minutes
- **Refresh Token:** Expires in 7 days
- **Algorithm:** HS256

---

## API Endpoints

### 1. Health Check
#### `GET /health`
**Description:** Check API health status

**Response:** 200 OK
```json
{
  "status": "ok",
  "env": "development"
}
```

---

### 2. Authentication Endpoints

#### `POST /auth/register`
**Description:** Register a new student

**Request Body:**
```json
{
  "name": "Aarav Mehta",
  "email": "aarav@student.edu",
  "password": "Student@123"
}
```

**Response:** 201 Created
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- 409 Conflict: Email already registered

---

#### `POST /auth/login`
**Description:** Login as student or driver

**Request Body:**
```json
{
  "email": "aarav@student.edu",
  "password": "Student@123"
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- 401 Unauthorized: Invalid credentials or inactive user

---

#### `POST /auth/register-driver`
**Description:** Register a driver with RTO verification documents

**Request:** Form Data
```
- name: "Suresh Pawar" (required)
- phone: "9876543210" (required)
- email: "driver@nm-ride.com" (required)
- password: "Driver@123" (required, min 8 chars)
- vehicle_type: "auto" (required)
- vehicle_details: "MH-15 AG 1234" (optional)
- service_area: "Nashik Road" (optional)
- id_document: <file> (optional, PDF/JPG/PNG, max 5MB)
- license_document: <file> (optional)
- rc_document: <file> (optional)
```

**Response:** 201 Created
```json
{
  "message": "Driver registration submitted for verification. Await admin approval.",
  "driver_id": "550e8400-e29b-41d4-a716-446655440001",
  "status": "PENDING"
}
```

**Errors:**
- 400 Bad Request: Invalid file format or size
- 409 Conflict: Email already registered

---

#### `POST /auth/refresh`
**Description:** Refresh access token

**Request Body:**
```json
{
  "refresh_token": "eyJhbGc..."
}
```

**Response:** 200 OK
```json
{
  "access_token": "eyJhbGc...",
  "refresh_token": "eyJhbGc...",
  "token_type": "bearer"
}
```

**Errors:**
- 401 Unauthorized: Invalid or expired refresh token

---

### 3. User Endpoints

#### `GET /users/me`
**Description:** Get current authenticated user

**Headers:** `Authorization: Bearer {token}`

**Response:** 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440002",
  "name": "Aarav Mehta",
  "email": "aarav@student.edu",
  "role": "student",
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-15T10:30:00Z"
}
```

**Errors:**
- 401 Unauthorized: Invalid or missing token

---

#### `PUT /users/me`
**Description:** Update current user profile

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "name": "Aarav Mehta Updated"
}
```

**Response:** 200 OK (Updated user object)

---

#### `GET /users/me/contacts`
**Description:** Get ride contacts for current student

**Headers:** `Authorization: Bearer {token}`

**Response:** 200 OK
```json
[
  {
    "driver_name": "Suresh Pawar",
    "vehicle_type": "auto",
    "contacted_at": "2024-01-15T14:30:00Z"
  }
]
```

---

### 4. Driver Endpoints

#### `GET /drivers`
**Description:** List all APPROVED drivers (students only)

**Query Parameters:**
- `vehicle_type` (optional): Filter by vehicle type (auto, bike, cab)

**Headers:** `Authorization: Bearer {token}`

**Response:** 200 OK
```json
[
  {
    "id": "550e8400-e29b-41d4-a716-446655440001",
    "name": "Suresh Pawar",
    "vehicle_type": "auto",
    "vehicle_details": "MH-15 AG 1234, Yellow Auto",
    "service_area": "Nashik Road",
    "is_available": true,
    "avg_rating": 4.5,
    "total_ratings": 10
  }
]
```

**Errors:**
- 401 Unauthorized: Student must be logged in

---

#### `GET /drivers/{driver_id}`
**Description:** Get driver details with ratings

**Headers:** `Authorization: Bearer {token}`

**Response:** 200 OK
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440001",
  "name": "Suresh Pawar",
  "phone": "+91 98220 11111",
  "vehicle_type": "auto",
  "vehicle_details": "MH-15 AG 1234, Yellow Auto",
  "service_area": "Nashik Road",
  "is_available": true,
  "avg_rating": 4.5,
  "total_ratings": 10,
  "ratings": [
    {
      "id": "request-uuid",
      "rating": 5,
      "comment": "Excellent service!",
      "student_id": "uuid",
      "created_at": "2024-01-15T15:00:00Z"
    }
  ]
}
```

**Errors:**
- 404 Not Found: Driver not found or not approved

---

#### `POST /drivers/{driver_id}/contacts`
**Description:** Log a ride contact with a driver

**Headers:** `Authorization: Bearer {token}`

**Response:** 200 OK
```json
{
  "message": "Contact logged"
}
```

---

#### `POST /drivers/{driver_id}/ratings`
**Description:** Submit a rating for a driver (students only)

**Headers:** `Authorization: Bearer {token}`

**Request Body:**
```json
{
  "rating": 5,
  "comment": "Great service, very helpful!"
}
```

**Response:** 201 Created
```json
{
  "id": "rating-uuid",
  "driver_id": "driver-uuid",
  "student_id": "student-uuid",
  "rating": 5,
  "comment": "Great service, very helpful!",
  "created_at": "2024-01-15T15:00:00Z"
}
```

**Errors:**
- 409 Conflict: Already rated this driver
- 403 Forbidden: Only students can rate

---

### 5. Driver Portal Endpoints

#### `GET /driver/me`
**Description:** Get current driver profile

**Headers:** `Authorization: Bearer {driver_token}`

**Response:** 200 OK (Full driver object with verification status)

---

#### `PUT /driver/me`
**Description:** Update driver profile

**Headers:** `Authorization: Bearer {driver_token}`

**Request Body:**
```json
{
  "vehicle_details": "MH-15 AG 5678",
  "service_area": "Nashik"
}
```

**Response:** 200 OK (Updated driver object)

---

#### `PUT /driver/me/availability`
**Description:** Set driver availability

**Headers:** `Authorization: Bearer {driver_token}`

**Request Body:**
```json
{
  "is_available": true
}
```

**Response:** 200 OK
```json
{
  "is_available": true
}
```

---

#### `GET /driver/me/ratings`
**Description:** Get ratings for current driver

**Headers:** `Authorization: Bearer {driver_token}`

**Response:** 200 OK
```json
[
  {
    "id": "rating-uuid",
    "rating": 5,
    "comment": "Excellent!",
    "student_id": "student-uuid",
    "created_at": "2024-01-15T15:00:00Z"
  }
]
```

---

### 6. Admin Endpoints

#### `GET /admin/stats`
**Description:** Get admin dashboard statistics

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK
```json
{
  "total_students": 45,
  "total_approved_drivers": 12,
  "total_pending_drivers": 3,
  "total_ratings": 156,
  "avg_driver_rating": 4.3
}
```

---

#### `GET /admin/drivers/pending`
**Description:** List drivers pending verification

**Query Parameters:**
- `page` (default: 1): Page number
- `limit` (default: 20, max: 100): Items per page

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK
```json
[
  {
    "id": "driver-uuid",
    "name": "Raj Kumar",
    "email": "raj@nm-ride.com",
    "phone": "9876543210",
    "vehicle_type": "auto",
    "vehicle_details": "MH-01 AB 1234",
    "service_area": "Nashik",
    "verification_status": "PENDING",
    "created_at": "2024-01-15T10:00:00Z",
    "documents_uploaded": true,
    "documents_count": 3
  }
]
```

---

#### `GET /admin/drivers/{driver_id}/verification-status`
**Description:** Get driver verification status with documents

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK
```json
{
  "driver_id": "driver-uuid",
  "driver_name": "Raj Kumar",
  "verification_status": "PENDING",
  "verification_notes": null,
  "verified_at": null,
  "verified_by": null,
  "documents": [
    {
      "id": "doc-uuid",
      "document_type": "ID",
      "file_name": "id_document.pdf",
      "file_size": 145320,
      "file_type": "pdf",
      "status": "PENDING",
      "uploaded_at": "2024-01-15T10:00:00Z",
      "verified_at": null,
      "expiry_date": "2025-12-31"
    }
  ],
  "all_required_approved": false
}
```

---

#### `PUT /admin/drivers/{driver_id}/approve`
**Description:** Approve a driver

**Headers:** `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "notes": "All documents verified successfully"
}
```

**Response:** 200 OK
```json
{
  "message": "Driver approved successfully",
  "driver_id": "driver-uuid",
  "status": "APPROVED"
}
```

---

#### `PUT /admin/drivers/{driver_id}/reject`
**Description:** Reject a driver

**Headers:** `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "reason": "License document expired. Please provide updated license."
}
```

**Response:** 200 OK
```json
{
  "message": "Driver rejected",
  "driver_id": "driver-uuid",
  "status": "REJECTED"
}
```

---

#### `PUT /admin/drivers/{driver_id}/suspend`
**Description:** Suspend a driver

**Headers:** `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "reason": "Multiple customer complaints regarding behavior"
}
```

**Response:** 200 OK
```json
{
  "message": "Driver suspended",
  "driver_id": "driver-uuid",
  "status": "SUSPENDED"
}
```

---

#### `GET /admin/drivers/{driver_id}/documents`
**Description:** Get all documents for a driver

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK
```json
[
  {
    "id": "doc-uuid",
    "document_type": "ID",
    "file_name": "id_document_123abc.pdf",
    "file_size": 145320,
    "file_type": "pdf",
    "status": "PENDING",
    "uploaded_at": "2024-01-15T10:00:00Z",
    "verified_at": null,
    "expiry_date": "2025-12-31"
  }
]
```

---

#### `GET /admin/drivers`
**Description:** List all drivers (paginated)

**Query Parameters:**
- `page` (default: 1): Page number
- `limit` (default: 20, max: 100): Items per page

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK (Array of driver objects)

---

#### `POST /admin/drivers`
**Description:** Create a new driver (admin only, auto-approved)

**Headers:** `Authorization: Bearer {admin_token}`

**Request Body:**
```json
{
  "name": "Admin Created Driver",
  "phone": "9876543210",
  "email": "admin.driver@nm-ride.com",
  "password": "Driver@123",
  "vehicle_type": "auto",
  "vehicle_details": "MH-15 AG 1234",
  "service_area": "Nashik"
}
```

**Response:** 201 Created

---

#### `PUT /admin/drivers/{driver_id}`
**Description:** Update driver information

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK

---

#### `DELETE /admin/drivers/{driver_id}`
**Description:** Deactivate a driver

**Headers:** `Authorization: Bearer {admin_token}`

**Response:** 200 OK
```json
{
  "message": "Driver deactivated successfully"
}
```

---

## Response Headers

All responses include:
- `X-Request-ID`: Unique request identifier (UUID)
- `X-Process-Time`: Request processing time in seconds

---

## Error Responses

All errors follow this format:

```json
{
  "error": "ERROR_CODE",
  "message": "Human readable error message",
  "status_code": 400
}
```

### Error Codes
- `NOT_FOUND` (404): Resource not found
- `UNAUTHORIZED` (401): Authentication failed
- `FORBIDDEN` (403): Permission denied
- `CONFLICT` (409): Resource conflict
- `BAD_REQUEST` (400): Invalid request
- `DATABASE_ERROR` (500): Database operation failed
- `INTERNAL_ERROR` (500): Unexpected server error

---

## Request/Response Validation

### Field Validation
- **Email**: Must be valid email format
- **Password**: Minimum 8 characters
- **Phone**: 10-20 digits
- **Rating**: 1-5 stars
- **Name**: 1-100 characters

### File Upload
- **Allowed types**: PDF, JPG, JPEG, PNG
- **Max size**: 5MB per file
- **Content-Type**: auto-detected from file extension

---

## Authentication States

### User Types
1. **Student** (`role: "student")`
   - Can register, login
   - Can view approved drivers
   - Can rate drivers
   - Can access `/users/*` endpoints

2. **Driver** (`role: "driver")`
   - Can register, login
   - Can view own profile
   - Can set availability
   - Can view own ratings
   - Can access `/driver/*` endpoints

3. **Admin** (`role: "admin")`
   - Can manage drivers
   - Can verify documents
   - Can approve/reject/suspend drivers
   - Can access `/admin/*` endpoints

---

## Rate Limiting

- **Limit**: 60 requests per minute
- **Header**: `X-RateLimit-*` (when implemented)

---

## CORS Configuration

**Allowed Origins:**
- http://localhost:3000
- http://127.0.0.1:3000

**Allowed Methods:** GET, POST, PUT, DELETE, OPTIONS
**Allowed Headers:** * (all)
**Credentials:** Allowed

---

## Documentation

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json
