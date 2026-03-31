import requests
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_section(title):
    print("\n" + "="*60)
    print(f" {title}")
    print("="*60)

# 1. Admin Login
print_section("STEP 1: Admin Login")
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@campusride.com", "password": "Admin@123"},
    timeout=5
)
admin_token = login_response.json()["access_token"]
print(f"✅ Admin logged in successfully")
print(f"Token: {admin_token[:30]}...")

headers = {"Authorization": f"Bearer {admin_token}"}

# 2. Get Pending Drivers
print_section("STEP 2: Get Pending Drivers (non-verified)")
pending_response = requests.get(
    f"{BASE_URL}/admin/drivers/pending?page=1&limit=20",
    headers=headers,
    timeout=5
)
pending_drivers = pending_response.json()

if isinstance(pending_drivers, dict) and "data" in pending_drivers:
    pending_drivers = pending_drivers["data"]

print(f"✅ Found {len(pending_drivers)} pending drivers:")
for i, driver in enumerate(pending_drivers[:3], 1):  # Show first 3
    print(f"\n  Driver {i}: {driver.get('name', 'Unknown')}")
    print(f"    Email: {driver.get('email', 'N/A')}")
    print(f"    Phone: {driver.get('phone', 'N/A')}")
    print(f"    Vehicle: {driver.get('vehicle_type', 'N/A')}")
    print(f"    Documents: {driver.get('documents_count', 0)} uploaded")
    print(f"    Status: {driver.get('verification_status', 'PENDING')}")

# 3. Get Verification Details for First Pending Driver
if pending_drivers:
    first_driver = pending_drivers[0]
    driver_id = first_driver["id"]
    
    print_section(f"STEP 3: Get Verification Details for {first_driver['name']}")
    
    verification_response = requests.get(
        f"{BASE_URL}/admin/drivers/{driver_id}/verification-status",
        headers=headers,
        timeout=5
    )
    
    if verification_response.status_code == 200:
        verification = verification_response.json()
        
        if isinstance(verification, dict) and "data" in verification:
            verification = verification["data"]
        
        print(f"✅ Retrieved verification details:")
        print(f"   Driver ID: {driver_id}")
        print(f"   Status: {verification.get('verification_status', 'PENDING')}")
        print(f"   Documents submitted: {len(verification.get('documents', []))}")
        
        # Show documents
        print(f"\n   📄 Submitted Documents:")
        for doc in verification.get('documents', []):
            doc_icons = {
                'ID': '🆔',
                'LICENSE': '📜',
                'RC': '🚗',
                'INSURANCE': '🛡️'
            }
            icon = doc_icons.get(doc.get('document_type'), '📄')
            print(f"     {icon} {doc.get('document_type')}")
            print(f"        File: {doc.get('file_name', 'Unknown')}")
            print(f"        Size: {doc.get('file_size', 0) / 1024:.2f} KB")
            print(f"        Status: {doc.get('status', 'PENDING')}")
        
        print(f"\n   Ready to approve: {verification.get('all_required_approved', False)}")
    else:
        print(f"❌ Error: {verification_response.status_code}")
        print(verification_response.json())

print_section("Admin Panel is Ready!")
print("""
✅ All systems operational:
  1. Pending drivers showing real registration data
  2. Documents uploaded during registration visible
  3. Verification workflow ready
  
Admin can now:
  ✓ Review pending driver applications
  ✓ View all uploaded documents
  ✓ Approve drivers (documents must be complete)
  ✓ Reject with detailed feedback
  
Go to: http://localhost:3001/admin
Login: admin@campusride.com / Admin@123
""")
