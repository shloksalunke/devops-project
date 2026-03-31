"""
Detailed test of driver registration to identify 400 error source.
This replicates EXACTLY what the frontend FormData sends.
"""
import requests
from pathlib import Path
import io

BASE_URL = "http://localhost:8000"

# Test data - matching what frontend sends
test_data = {
    'name': 'Test Driver',
    'phone': '9876543210',
    'email': f'testdriver_{Path.cwd().stat().st_mtime:.0f}@test.com',
    'password': 'Driver@123',
    'vehicle_type': 'auto',
    'vehicle_details': 'Hyundai i20, White',
    'service_area': 'Bangalore',
}

# Create minimal test files
print("=" * 60)
print("DETAILED DRIVER REGISTRATION TEST")
print("=" * 60)

print("\n1. TEST DATA TO SEND:")
for k, v in test_data.items():
    print(f"   {k}: {v}")

# Create fake PDF files
id_pdf = io.BytesIO(b"%PDF-1.4\n%fake pdf content\n")
id_pdf.name = "government_id.pdf"

license_pdf = io.BytesIO(b"%PDF-1.4\n%fake pdf content\n")
license_pdf.name = "driving_license.pdf"

rc_pdf = io.BytesIO(b"%PDF-1.4\n%fake pdf content\n")
rc_pdf.name = "rc_certificate.pdf"

print("\n2. FILES TO UPLOAD:")
print(f"   ID Document: {id_pdf.name} ({len(id_pdf.getvalue())} bytes)")
print(f"   License Document: {license_pdf.name} ({len(license_pdf.getvalue())} bytes)")
print(f"   RC Document: {rc_pdf.name} ({len(rc_pdf.getvalue())} bytes)")

# Reset file pointers
id_pdf.seek(0)
license_pdf.seek(0)
rc_pdf.seek(0)

# Prepare files dict - EXACTLY like frontend FormData
files = {
    'id_document': ('government_id.pdf', id_pdf, 'application/pdf'),
    'license_document': ('driving_license.pdf', license_pdf, 'application/pdf'),
    'rc_document': ('rc_certificate.pdf', rc_pdf, 'application/pdf'),
}

# Prepare data dict
data = test_data

print("\n3. MAKING REQUEST:")
print(f"   URL: {BASE_URL}/auth/register-driver")
print(f"   Method: POST")
print(f"   Content-Type: multipart/form-data (will be set by requests library)")

try:
    # Send request WITHOUT specifying Content-Type - let requests set it
    # This is how axios should work after our fix
    response = requests.post(
        f"{BASE_URL}/auth/register-driver",
        data=data,
        files=files,
        timeout=10
    )
    
    print(f"\n4. RESPONSE:")
    print(f"   Status Code: {response.status_code}")
    print(f"   Headers: {dict(response.headers)}")
    print(f"   Body: {response.text}")
    
    if response.status_code == 201:
        print("\n✅ SUCCESS! Registration worked!")
        result = response.json()
        print(f"   Driver ID: {result.get('driver_id')}")
        print(f"   Status: {result.get('status')}")
    else:
        print(f"\n❌ FAILED with status {response.status_code}")
        try:
            error = response.json()
            print(f"   Error details: {error}")
        except:
            print(f"   Raw response: {response.text}")

except Exception as e:
    print(f"\n❌ ERROR: {str(e)}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 60)
