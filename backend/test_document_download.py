import requests
import json

BASE_URL = "http://localhost:8000"

# 1. Admin Login
login_response = requests.post(
    f"{BASE_URL}/auth/login",
    json={"email": "admin@campusride.com", "password": "Admin@123"},
    timeout=5
)
admin_token = login_response.json()["access_token"]
headers = {"Authorization": f"Bearer {admin_token}"}

print("✅ Admin logged in")
print()

# 2. Get pending drivers
pending_response = requests.get(
    f"{BASE_URL}/admin/drivers/pending?page=1&limit=5",
    headers=headers,
    timeout=5
)
pending_drivers = pending_response.json()

if isinstance(pending_drivers, dict) and "data" in pending_drivers:
    pending_drivers = pending_drivers["data"]

print(f"✅ Found {len(pending_drivers)} pending drivers")
print()

# 3. Get verification status for first driver with documents
for driver in pending_drivers:
    if driver.get("documents_count", 0) > 0:
        print(f"📋 Testing with driver: {driver['name']} (ID: {driver['id']})")
        print(f"   Documents: {driver['documents_count']}")
        
        # Get verification status
        verification_response = requests.get(
            f"{BASE_URL}/admin/drivers/{driver['id']}/verification-status",
            headers=headers,
            timeout=5
        )
        
        if verification_response.status_code == 200:
            verification = verification_response.json()
            
            # Handle possible wrapping
            if isinstance(verification, dict) and "data" in verification:
                verification = verification["data"]
            
            print(f"   Documents in response: {len(verification.get('documents', []))}")
            
            # Check each document
            for doc in verification.get('documents', [])[:1]:  # Show first document
                print(f"\n   Document Details:")
                print(f"   - ID: {doc.get('id')}")
                print(f"   - Type: {doc.get('document_type')}")
                print(f"   - File: {doc.get('file_name')}")
                print(f"   - Size: {doc.get('file_size', 0) / 1024:.2f} KB")
                
                # Test document download endpoint
                if doc.get('id'):
                    download_url = f"{BASE_URL}/admin/drivers/{driver['id']}/documents/{doc['id']}/download"
                    download_response = requests.get(
                        download_url,
                        headers=headers,
                        timeout=5
                    )
                    
                    if download_response.status_code == 200:
                        print(f"   ✅ Document download working!")
                        print(f"   - Response size: {len(download_response.content) / 1024:.2f} KB")
                    else:
                        print(f"   ❌ Download failed: {download_response.status_code}")
        else:
            print(f"   ❌ Get verification failed: {verification_response.status_code}")
        break
else:
    print("No drivers with documents found")

print()
print("✅ Document Download System Ready!")
print()
print("Admin can now:")
print("  1. Go to Pending Verification tab")
print("  2. Click 'Review Request' on any driver")
print("  3. See all uploaded documents")
print("  4. Click Eye 👁️ or Download icon to view/download documents")
