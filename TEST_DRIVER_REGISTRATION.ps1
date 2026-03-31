# Test driver registration with file upload
$url = "http://localhost:8000/auth/register-driver"

# Create test files
$idContent = "Test Government ID Document"
$licenseContent = "Test Driving License"
$rcContent = "Test RC Document"

# Write to temporary files
$tmpDir = "$env:TEMP\nmride_test"
mkdir -Force $tmpDir | Out-Null

$idFile = "$tmpDir\id.txt"
$licenseFile = "$tmpDir\license.txt"
$rcFile = "$tmpDir\rc.txt"

Set-Content -Path $idFile -Value $idContent
Set-Content -Path $licenseFile -Value $licenseContent
Set-Content -Path $rcFile -Value $rcContent

$form = @{
    name = "Test Driver"
    phone = "9876543210"
    email = "testdriver@nm-ride.com"
    password = "Driver@123"
    vehicle_type = "auto"
    vehicle_details = "DL-01-AB-1234"
    service_area = "Test Area"
    id_document = (Get-Item $idFile)
    license_document = (Get-Item $licenseFile)
    rc_document = (Get-Item $rcFile)
}

Write-Host "🧪 Testing Driver Registration Endpoint" -ForegroundColor Cyan
Write-Host "URL: $url" -ForegroundColor Gray
Write-Host ""

try {
    $response = Invoke-WebRequest -Uri $url `
        -Method Post `
        -Form $form `
        -TimeoutSec 10 `
        -ErrorAction Stop
    
    Write-Host "✅ Registration succeeded!" -ForegroundColor Green
    $response.Content | ConvertFrom-Json | ConvertTo-Json | Write-Host -ForegroundColor Green
} catch {
    Write-Host "❌ Registration failed!" -ForegroundColor Red
    Write-Host ""
    
    if ($_.Response.StatusCode -eq 422) {
        Write-Host "Error Type: Validation Error (422)" -ForegroundColor Yellow
        Write-Host ""
        Write-Host "Response Body:" -ForegroundColor Yellow
        $errorResponse = $_.ErrorDetails.Message | ConvertFrom-Json
        $errorResponse | ConvertTo-Json -Depth 5 | Write-Host -ForegroundColor Yellow
    } else {
        Write-Host "Status Code: $($_.Response.StatusCode)" -ForegroundColor Yellow
        Write-Host "Message: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# Cleanup
Remove-Item -Path $tmpDir -Recurse -Force -ErrorAction SilentlyContinue
