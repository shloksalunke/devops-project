# End-to-End Testing Guide - RTO Verification System

## Pre-Testing Checklist

### ✅ Services Running
- [ ] Backend running: `http://localhost:8000`
- [ ] Frontend running: `http://localhost:3000`
- [ ] PostgreSQL running and accessible
- [ ] Database migration completed: `alembic upgrade head`
- [ ] Seed data loaded: `python scripts/seed.py` (if needed)

### ✅ Tools Ready
- [ ] Browser (Chrome/Firefox)
- [ ] Terminal/PowerShell for logs
- [ ] Network tab open (F12) for API calls
- [ ] Create test files for document upload

---

## Test Scenario: Complete Verification Flow

### Phase 1: Driver Registration

**Time: ~5 mins**

#### Step 1: Prepare Test Documents
```bash
# Create dummy test files for upload
# Windows:
new-item -path "C:\temp" -name "dummy_id.jpg" -itemtype file
new-item -path "C:\temp" -name "dummy_license.pdf" -itemtype file
new-item -path "C:\temp" -name "dummy_rc.jpg" -itemtype file

# Or use actual image/PDF files
```

#### Step 2: Driver Self-Registration
```
1. Open browser: http://localhost:3000/register-driver
2. Fill out form:
   - Name: "Test Driver 001"
   - Phone: "9999988888"
   - Email: "testdriver001@example.com"
   - Password: "TestPass@123"
   - Confirm: "TestPass@123"
   
3. Vehicle Info:
   - Type: "Auto"
   - Details: "Auto 123, Yellow"
   - Service Area: "Test Area"

4. Upload Documents:
   - Government ID: Upload dummy_id.jpg
   - Driving License: Upload dummy_license.pdf
   - Vehicle RC: Upload dummy_rc.jpg (optional)
   
5. Click "Submit Registration for Verification"

Expected Result:
✅ Success page shows "Registration Submitted!"
✅ Status shows "PENDING"
✅ All 3 documents listed with checkmarks
✅ 4-step process displayed
✅ "Check your email" message visible
```

#### Step 3: Verify Backend Records
```bash
# Connect to database and verify
psql -U postgres -d campusride

# Check driver created with PENDING status
SELECT id, name, email, verification_status, is_active FROM drivers 
WHERE email = 'testdriver001@example.com';
# Should show: verification_status='PENDING', is_active=FALSE

# Check documents uploaded
SELECT id, driver_id, document_type, status FROM driver_documents 
WHERE driver_id = (SELECT id FROM drivers WHERE email = 'testdriver001@example.com');
# Should show 3 rows: ID, LICENSE, RC all with status='PENDING'
```

---

### Phase 2: Admin Review & Approval

**Time: ~3 mins**

#### Step 1: Admin Login
```
1. Open new browser tab (or window)
2. Go to: http://localhost:3000/login

3. Enter credentials:
   - Email: admin@nm-ride.com
   - Password: Admin@123

4. Click "Login"

Expected Result:
✅ Redirected to http://localhost:3000/admin
✅ Sidebar shows "Admin Panel"
✅ Dashboard tab shows stats
✅ Red badge on "Pending Verification" showing "1" pending drivers
```

#### Step 2: View Dashboard Stats
```
On Dashboard tab, verify:
✅ Total Drivers: Shows count
✅ Active Drivers: Shows count (at least 1)
✅ Pending Verification: Shows "1" (our test driver)
✅ Total Ratings: Shows count
```

#### Step 3: Review Pending Driver
```
1. Click "Pending Verification" tab (left sidebar)

Expected Result:
✅ See list with "Test Driver 001"
✅ Email shows: "testdriver001@example.com"
✅ Vehicle badge shows: "Auto"
✅ Document count shows: "3 documents"
✅ "Review" button visible

2. Click "Review" button

Expected Result:
✅ Document Viewer modal opens
✅ Title shows: "Review: Test Driver 001"
✅ Shows "Driver Information"
✅ Shows "Uploaded Documents" section
✅ Lists 3 documents:
   - Government ID (PENDING status)
   - Driving License (PENDING status)
   - Vehicle RC (PENDING status)
✅ Green check: "All required documents are approved" (should be FALSE initially)
```

#### Step 4: Approve Documents in Modal
```
Option A - APPROVE WORKFLOW:
1. In Document Viewer modal:
   - Add optional notes: "All documents verified, driving license valid per RTO"
   
2. Click "Approve" button

Expected Result:
✅ Success toast: "Driver approved successfully!"
✅ Modal closes
✅ Driver removed from pending list
✅ Backend creates records:
   - Driver: verification_status='APPROVED', is_active=TRUE
   - All documents: status='APPROVED'
   - Timestamps: verified_at, verified_by set
```

#### Step 5: Verify in Database
```bash
# Check driver is now APPROVED
SELECT id, name, email, verification_status, is_active, verified_at, verified_by 
FROM drivers WHERE email = 'testdriver001@example.com';
# Should show: verification_status='APPROVED', is_active=TRUE, verified_at (current time)

# Check document status
SELECT document_type, status, verified_at FROM driver_documents 
WHERE driver_id = (SELECT id FROM drivers WHERE email = 'testdriver001@example.com');
# All should show: status='APPROVED', verified_at (current time)
```

---

### Phase 3: Student Views Approved Driver

**Time: ~2 mins**

#### Step 1: Student Login
```
1. Open NEW browser tab/window (to isolate sessions)
2. Go to: http://localhost:3000/login

3. Enter credentials:
   - Email: aarav@student.edu
   - Password: Student@123

4. Click "Login"

Expected Result:
✅ Redirected to http://localhost:3000/home
✅ See list of available drivers
✅ NEW DRIVER "Test Driver 001" visible in list
✅ Can see driver card with:
   - Name: "Test Driver 001"
   - Vehicle: "Auto"
   - Rating: "0.0" (new driver)
   - "Contact Driver" button visible
```

#### Step 2: Verify Driver NOT Visible Before Approval
```
To verify the filtering works:

1. Go back to admin tab
2. Before clicking approve, if you look at database:
   SELECT * FROM drivers WHERE verification_status = 'PENDING' AND is_active = FALSE;
   # Should show unverified drivers

3. On student tab, refresh /home
   # Should NOT see PENDING drivers

4. After approval (which you just did), refresh
   # NOW should see the approved driver
```

---

### Phase 4: Test Rejection Workflow (Optional)

**Time: ~2 mins**

#### Register Another Test Driver
```
1. Open new browser tab
2. Go to: http://localhost:3000/register-driver
3. Register with:
   - Name: "Test Driver 002"
   - Email: "testdriver002@example.com"
   - Other details similar
4. Upload documents
5. Expect: "PENDING" status
```

#### Admin Rejects Driver
```
1. Go to admin tab (login if needed)
2. Click "Pending Verification" tab
3. Click "Review" on "Test Driver 002"
4. Click "Reject" button
5. Modal opens: "Reject Driver Application"
6. Enter reason: "Driving license photo not clear, cannot verify RTO compliance"
7. Click "Reject Driver"

Expected Result:
✅ Success toast: "Driver rejected"
✅ Driver removed from pending list
✅ Driver verification_status='REJECTED' in database
✅ Rejection reason stored in driver_documents
✅ Driver NOT visible to students
```

---

### Phase 5: Test "All Drivers" Tab

**Time: ~2 mins**

#### As Admin:
```
1. Click "All Drivers" tab (left sidebar)

Expected Result:
✅ See table with all drivers
✅ Columns: Name, Vehicle, Status, Verification, Rating, Actions
✅ Test Driver 001: verification_status="APPROVED", is_active shown
✅ Test Driver 002: verification_status="REJECTED"
✅ Can click Edit button on drivers
✅ Can click Delete button to deactivate drivers
```

---

## API Testing (Advanced)

### Get Pending Drivers
```bash
# Get token from admin login
TOKEN="your_admin_jwt_token"

curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/drivers/pending
```

Expected Response:
```json
{
  "data": [
    {
      "id": "uuid",
      "name": "Test Driver 001",
      "email": "testdriver001@example.com",
      "vehicle_type": "auto",
      "documents_count": 3,
      "documents_uploaded": true
    }
  ]
}
```

### Get Verification Status
```bash
curl -H "Authorization: Bearer $TOKEN" \
  http://localhost:8000/admin/drivers/{driver_id}/verification-status
```

Expected Response:
```json
{
  "driver_id": "uuid",
  "driver_name": "Test Driver 001",
  "verification_status": "PENDING",
  "documents": [
    {
      "id": "uuid",
      "document_type": "ID",
      "file_name": "dummy_id.jpg",
      "status": "PENDING"
    }
  ],
  "all_required_approved": false
}
```

### Approve Driver (via API)
```bash
curl -X PUT \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"notes": "Verified via API"}' \
  http://localhost:8000/admin/drivers/{driver_id}/approve
```

---

## Performance Testing

Check these metrics:

| Operation | Expected Time | How to Measure |
|-----------|---|---|
| Admin login | < 2 seconds | Time in browser |
| Load pending drivers | < 1 second | Network tab F12 |
| Document viewer opens | < 500ms | Network tab |
| Approve driver | < 2 seconds | See toast message |
| Student list updates | < 1 second | Refresh /home |

---

## Error Handling Tests

### Test 1: Invalid Credentials
```
1. Try: admin@nm-ride.com / WrongPassword
Expected: ❌ "Login failed" error shown
```

### Test 2: Unauthorized Document Approval
```
1. Student tries to access /admin
Expected: ❌ Redirected to /home (role check works)
```

### Test 3: Missing Required Documents
```
1. Register driver with only ID doc (no License)
2. Admin tries to approve
Expected: ❌ Approve button disabled (yellow warning about incomplete docs)
```

### Test 4: Short Rejection Reason
```
1. Click Reject on a pending driver
2. Enter reason less than 10 chars: "bad"
3. Try to submit
Expected: ❌ Button stays disabled (validation works)
```

---

## Checklist - All Tests Complete

### ✅ Phase 1: Registration
- [ ] Driver self-registration form works
- [ ] All 3 document types upload successfully
- [ ] Success screen shows PENDING status
- [ ] Database records created correctly
- [ ] is_active=FALSE for pending drivers

### ✅ Phase 2: Admin Review
- [ ] Admin login works and redirects to /admin
- [ ] Pending Verification tab shows new driver
- [ ] Document viewer modal displays all docs
- [ ] Approval button works and changes status
- [ ] Database updated with APPROVED status

### ✅ Phase 3: Student View
- [ ] Student login works and redirects to /home
- [ ] APPROVED driver visible in list
- [ ] PENDING drivers NOT visible
- [ ] REJECTED drivers NOT visible
- [ ] Can contact approved drivers

### ✅ Phase 4: Rejection
- [ ] Rejection modal appears
- [ ] Reason validation works (min 10 chars)
- [ ] Rejected driver removed from pending
- [ ] Rejected driver NOT visible to students

### ✅ Phase 5: Dashboard
- [ ] Stats cards show correct counts
- [ ] Badge shows pending count
- [ ] All tabs accessible and functional

### ✅ Advanced Tests
- [ ] API endpoints return correct responses
- [ ] Role-based access control working
- [ ] Error messages clear and helpful
- [ ] Performance acceptable (< 2s for all operations)

---

## Debugging Tips

### If something fails:

1. **Check Backend Logs**
   ```bash
   # Terminal where backend runs
   # Look for error messages
   # Should show 200 status codes for successful requests
   ```

2. **Check Frontend Console**
   ```bash
   # F12 → Console tab
   # Look for JavaScript errors
   # Check Network tab for failed API calls (should be 200/201)
   ```

3. **Verify Database State**
   ```bash
   psql -U postgres -d campusride
   
   # Quick verification queries:
   SELECT COUNT(*) FROM drivers;
   SELECT COUNT(*) FROM driver_documents;
   SELECT verification_status, COUNT(*) FROM drivers GROUP BY verification_status;
   SELECT status, COUNT(*) FROM driver_documents GROUP BY status;
   ```

4. **Check File Uploads**
   ```bash
   # Windows PowerShell
   # Files should be in: backend/uploads/drivers/
   ls backend/uploads/drivers/
   ```

5. **Verify Migration Ran**
   ```bash
   # Backend directory
   alembic current
   # Should show: 001_add_rto_verification
   ```

---

## Success Criteria ✅

The verification system is **working correctly** when:

✅ Driver registers with documents → Status: PENDING  
✅ Driver hidden from student list (not visible)  
✅ Admin sees driver in Pending Verification tab  
✅ Admin can view and review documents  
✅ Admin approves driver → Status: APPROVED  
✅ Driver now visible to all students  
✅ Admin can reject with reason → Status: REJECTED  
✅ Rejected driver not visible to students  
✅ All role-based redirects work  

---

## Quick Command Reference

```bash
# Backend setup
cd backend
python -m venv venv      # Create environment
source venv/bin/activate # Activate (Linux/Mac)
venv\Scripts\activate     # Activate (Windows)
pip install -r requirements.txt
alembic upgrade head      # Run migration
python scripts/seed.py    # Load demo data
python -m uvicorn app.main:app --reload --port 8000

# Frontend setup
cd frontend
npm install
npm run dev

# Database checks
psql -U postgres -d campusride
\dt                       # List tables
\d drivers                # Show drivers table
\d driver_documents       # Show documents table
```

---

**Ready to test? Follow the phases above and report results!** 🚀
