import requests
import os
from PIL import Image
import io

url = "http://localhost:8000/auth/register-driver"

# Create test files directory
test_dir = "/tmp/campusride_test"
os.makedirs(test_dir, exist_ok=True)

# Create simple test images (valid PNG files)
def create_test_image(path):
    img = Image.new('RGB', (100, 100), color='red')
    img.save(path, 'PNG')

id_file_path = f"{test_dir}/id.png"
license_file_path = f"{test_dir}/license.png"

create_test_image(id_file_path)
create_test_image(license_file_path)

print("🧪 Testing Driver Registration Endpoint")
print(f"URL: {url}\n")

# Prepare form data
data = {
    'name': 'Test Driver',
    'phone': '9876543210',
    'email': 'testdriver@campusride.com',
    'password': 'Driver@123',
    'vehicle_type': 'auto',
    'vehicle_details': 'DL-01-AB-1234',
    'service_area': 'Test Area',
}

# Prepare files
files = {
    'id_document': open(id_file_path, 'rb'),
    'license_document': open(license_file_path, 'rb'),
}

try:
    response = requests.post(url, data=data, files=files, timeout=10)
    
    if response.status_code == 201:
        print("✅ Registration succeeded!")
        print(response.json())
    else:
        print(f"❌ Registration failed!")
        print(f"Status Code: {response.status_code}")
        print(f"Response:\n{response.json()}")
except Exception as e:
    print(f"❌ Error: {str(e)}")
finally:
    # Close files
    for f in files.values():
        f.close()
    
    # Cleanup
    import shutil
    shutil.rmtree(test_dir, ignore_errors=True)
