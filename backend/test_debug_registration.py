import requests
import os
from PIL import Image

BASE_URL = "http://localhost:8000"

# Create test files
test_dir = "/tmp/test_driver_reg"
os.makedirs(test_dir, exist_ok=True)

# Create valid PNG images
def create_test_image(path):
    img = Image.new('RGB', (100, 100), color='blue')
    img.save(path, 'PNG')

id_path = f"{test_dir}/id.png"
license_path = f"{test_dir}/license.png"

create_test_image(id_path)
create_test_image(license_path)

print("🧪 Testing Driver Registration")
print("=" * 50)

# Test 1: Minimal registration
print("\n1️⃣ Test: Minimal Registration (ID + License only)")
data = {
    'name': 'New Driver 1',
    'phone': '9999999999',
    'email': f'driver{os.urandom(4).hex()}@test.com',
    'password': 'Driver@123',
    'vehicle_type': 'auto',
}

files = {
    'id_document': open(id_path, 'rb'),
    'license_document': open(license_path, 'rb'),
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register-driver",
        data=data,
        files=files,
        timeout=10
    )
    
    if response.status_code == 201:
        print(f"✅ Success! Status: {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error! Status: {response.status_code}")
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")
finally:
    files['id_document'].close()
    files['license_document'].close()

# Test 2: With optional fields
print("\n2️⃣ Test: With Optional Fields")
data = {
    'name': 'New Driver 2',
    'phone': '8888888888',
    'email': f'driver{os.urandom(4).hex()}@test.com',
    'password': 'Driver@123',
    'vehicle_type': 'taxi',
    'vehicle_details': 'MH-15 AB 1234',
    'service_area': 'Central',
}

files = {
    'id_document': open(id_path, 'rb'),
    'license_document': open(license_path, 'rb'),
}

try:
    response = requests.post(
        f"{BASE_URL}/auth/register-driver",
        data=data,
        files=files,
        timeout=10
    )
    
    if response.status_code == 201:
        print(f"✅ Success! Status: {response.status_code}")
        print(f"Response: {response.json()}")
    else:
        print(f"❌ Error! Status: {response.status_code}")
        print(f"Response: {response.json()}")
except Exception as e:
    print(f"❌ Exception: {str(e)}")
finally:
    files['id_document'].close()
    files['license_document'].close()

# Cleanup
import shutil
shutil.rmtree(test_dir, ignore_errors=True)

print("\n" + "=" * 50)
print("Testing complete!")
