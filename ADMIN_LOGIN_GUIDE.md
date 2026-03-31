# Admin Login & Verification System Guide

## Quick Start - Admin Login

### Admin Credentials
```
Email:    admin@campusride.com
Password: Admin@123
```

### Login Steps

1. **Go to Login Page**
   - Navigate to: `http://localhost:3000/login`

2. **Enter Admin Credentials**
   - Email: `admin@nm-ride.com`
   - Password: `Admin@123`

3. **Click "Login"**
   - You'll be automatically redirected to `/admin` dashboard

4. **Verify Login Success**
   - See "Admin Panel" sidebar
   - Access to all admin tabs

---

## Admin Dashboard Tabs

### 1. Dashboard (Home)
- 📊 Total Drivers count
- ✅ Active (Approved) drivers count
- ⏳ Pending Verification count
- ⭐ Total ratings across all drivers

### 2. Pending Verification (NEW)
- 👁️ View all drivers awaiting approval
- 📄 Document count for each driver
- 🔍 Click "Review" to see driver details & documents
- ✅ Approve driver (only if all required docs approved)
- ❌ Reject driver with mandatory reason

### 3. All Drivers
- 📋 View all registered drivers
- 🚗 Vehicle type & status
- ⭐ Driver ratings
- ✏️ Edit driver information
- 🗑️ Deactivate driver

### 4. Users (Coming Soon)
- User management module
- Student account management

---

## Complete Verification Workflow

### Step 1: Driver Registration (As a Driver)
```
1. Go to: http://localhost:3000/register-driver
2. Fill form with:
   - Name, Phone, Email
   - Password
   - Vehicle type, details, service area
3. Upload REQUIRED documents:
   ✓ Government ID (Aadhar/Passport)
   ✓ Driving License (Valid per RTO)
   ✓ Vehicle RC (Optional but recommended)
4. Submit
5. See "Verification Status: PENDING"
```

### Step 2: Admin Reviews Documents
```
1. Login as Admin (admin@nm-ride.com / Admin@123)
2. Go to "Pending Verification" tab
3. See newly registered driver with document count
4. Click "Review" button
5. View all uploaded documents in modal
```

### Step 3: Approve or Reject
```
APPROVE PATH:
- Verify all documents are genuine
- Check Driving License is valid per RTO
- Check RC if provided
- Click "Approve" button
- (Optional) Add verification notes
- Driver is now APPROVED

REJECT PATH:
- If any document invalid/expired
- Click "Reject" button
- Modal opens for mandatory reason
- Enter reason (min 10 characters)
- Click "Reject Driver"
- Driver notified of rejection
```

### Step 4: Student Sees Approved Driver
```
1. Login as Student (aarav@student.edu / Student@123)
2. Go to http://localhost:3000/home
3. View available drivers
4. Only APPROVED drivers visible
5. Can contact driver for rides
```

---

## Demo Credentials

### 🎓 Student
```
Email:    aarav@student.edu
Password: Student@123
Role:     student
Path:     /home - Browse available drivers
```

### 🚗 Driver
```
Email:    suresh@driver.com
Password: Driver@123
Role:     driver
Path:     /driver/dashboard
Status:   Already APPROVED (use for testing)
```

### 🔐 Admin
```
Email:    admin@campusride.com
Password: Admin@123
Role:     admin
Path:     /admin - Complete verification control
```

---

## Admin Features in Detail

### Document Review Modal

**Shows for each driver:**
- ✅ Government ID (document name, upload date, status)
- ✅ Driving License (with "Valid per RTO" check)
- ✅ Vehicle RC (if provided)
- 🟨 Approval status for each document
- 🔴 Rejection reason if rejected

**Status Indicators:**
- 🟡 PENDING - Awaiting admin review
- 🟢 APPROVED - Document verified
- 🔴 REJECTED - Document invalid with reason

### Bulk Actions (Coming Soon)
- Approve multiple drivers at once
- Batch verification for efficiency
- Export verification reports

### Verification Rules

```python
# To APPROVE a driver:
✓ All required documents uploaded (ID + License)
✓ Documents are PENDING or APPROVED status
✓ No rejected documents
✓ Can add optional verification notes

# To REJECT a driver:
✓ Provide mandatory reason (min 10 chars)
✓ Reason is logged and visible to driver
✓ Driver can reapply after fixing issues
✓ Rejection email sent to driver
```

---

## API Endpoints (For Reference)

### Get Pending Drivers
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/admin/drivers/pending
```

### View Driver Verification Status
```bash
curl -H "Authorization: Bearer <admin_token>" \
  http://localhost:8000/admin/drivers/{driver_id}/verification-status
```

### Approve Driver
```bash
curl -X PUT \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"notes": "All documents verified"}' \
  http://localhost:8000/admin/drivers/{driver_id}/approve
```

### Reject Driver
```bash
curl -X PUT \
  -H "Authorization: Bearer <admin_token>" \
  -H "Content-Type: application/json" \
  -d '{"reason": "License expired"}' \
  http://localhost:8000/admin/drivers/{driver_id}/reject
```

---

## Troubleshooting

### Q: Admin login fails
**A:** Check:
- Email is exactly: `admin@nm-ride.com`
- Password is exactly: `Admin@123`
- Database migration ran: `alembic upgrade head`
- Backend is running on port 8000

### Q: Pending Verification tab is empty
**A:** 
- No pending drivers registered yet
- Register a new driver first at `/register-driver`
- Driver must upload documents to show in pending

### Q: Can't see documents in review modal
**A:**
- Check documents were uploaded during registration
- File size < 5MB
- File format: PDF, JPG, PNG
- Check backend file uploads directory exists

### Q: Approval button disabled
**A:**
- Not all required documents are uploaded
- At least one document has PENDING status
- Upload all required documents (ID + License minimum)

### Q: Admin dashboard not loading
**A:**
- Login token expired - logout and login again
- Backend API not running on port 8000
- Check CORS settings in backend
- Try clearing browser cache (Ctrl+Shift+Del)

---

## Testing Checklist

### ✓ Admin Login
- [ ] Can login with admin credentials
- [ ] Redirected to /admin page
- [ ] Sidebar shows "Admin Panel"
- [ ] Can logout

### ✓ Pending Verification
- [ ] Tab shows pending driver count badge
- [ ] Can see list of drivers awaiting approval
- [ ] Document count displayed for each driver
- [ ] "Review" button opens document modal

### ✓ Document Review
- [ ] All uploaded documents visible
- [ ] Document status shown (PENDING/APPROVED/REJECTED)
- [ ] Can see file names and upload dates
- [ ] Approval check shows if all required docs are approved

### ✓ Approval Workflow
- [ ] Can approve driver with optional notes
- [ ] Success message shown
- [ ] Driver removed from pending list
- [ ] Driver now visible to students

### ✓ Rejection Workflow
- [ ] Can reject driver with reason
- [ ] Reason validation (min 10 chars)
- [ ] Success message shown
- [ ] Driver removed from pending list

### ✓ Student View
- [ ] Only approved drivers visible (not pending)
- [ ] Driver appears after admin approval
- [ ] Can contact approved drivers for rides

---

## Additional Resources

- **MIGRATION_GUIDE.md** - Database migration instructions
- **IMPLEMENTATION_SUMMARY.md** - Complete system overview
- **Backend API Documentation** - See backend/README.md
- **Frontend Components** - Check src/pages/Admin.tsx

---

## Quick Reference

| Role | Email | Password | Login URL | Redirect |
|------|-------|----------|-----------|----------|
| Admin | admin@nm-ride.com | Admin@123 | /login | /admin |
| Student | aarav@student.edu | Student@123 | /login | /home |
| Driver | suresh@driver.com | Driver@123 | /driver/login | /driver/dashboard |

---

**Status:** ✅ Admin authentication **fully implemented and ready to use!**

Login now and test the complete verification workflow!
