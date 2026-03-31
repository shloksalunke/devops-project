# System Health Check Script
Write-Host "=== CAMPUS RIDE SYSTEM HEALTH CHECK ===" -ForegroundColor Cyan
Write-Host ""

# 1. Backend Health
Write-Host "1. Backend API Health" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/docs" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Backend running on port 8000" -ForegroundColor Green
} catch {
    Write-Host "❌ Backend not responding" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)"
}

# 2. Frontend Health
Write-Host ""
Write-Host "2. Frontend Health" -ForegroundColor Yellow
try {
    $response = Invoke-WebRequest -Uri "http://localhost:3001" -UseBasicParsing -TimeoutSec 3 -ErrorAction Stop
    Write-Host "✅ Frontend running on port 3001" -ForegroundColor Green
} catch {
    Write-Host "❌ Frontend not responding on port 3001" -ForegroundColor Red
}

# 3. Test Login Endpoint
Write-Host ""
Write-Host "3. Testing Login Endpoint" -ForegroundColor Yellow
try {
    $loginData = @{
        email = "admin@nm-ride.com"
        password = "Admin@123"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" `
        -UseBasicParsing `
        -Method Post `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $loginData `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $data = $response.Content | ConvertFrom-Json
    Write-Host "✅ Login endpoint working" -ForegroundColor Green
    Write-Host "   Token: $($data.access_token.Substring(0, 20))..." -ForegroundColor Gray
} catch {
    Write-Host "❌ Login endpoint failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 4. Test Get Drivers (student)
Write-Host ""
Write-Host "4. Testing Get Drivers Endpoint" -ForegroundColor Yellow
try {
    $studentLoginData = @{
        email = "aarav@student.edu"
        password = "Student@123"
    } | ConvertTo-Json
    
    $login = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" `
        -UseBasicParsing `
        -Method Post `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $studentLoginData `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $token = ($login.Content | ConvertFrom-Json).access_token
    
    $drivers = Invoke-WebRequest -Uri "http://localhost:8000/drivers" `
        -UseBasicParsing `
        -Headers @{"Authorization" = "Bearer $token"} `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $driverList = $drivers.Content | ConvertFrom-Json
    Write-Host "✅ Get drivers working" -ForegroundColor Green
    Write-Host "   Found $($driverList.data.Count) approved drivers" -ForegroundColor Gray
} catch {
    Write-Host "❌ Get drivers failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 5. Test Admin Endpoints
Write-Host ""
Write-Host "5. Testing Admin Pending Drivers Endpoint" -ForegroundColor Yellow
try {
    $adminLoginData = @{
        email = "admin@nm-ride.com"
        password = "Admin@123"
    } | ConvertTo-Json
    
    $login = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" `
        -UseBasicParsing `
        -Method Post `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $adminLoginData `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $token = ($login.Content | ConvertFrom-Json).access_token
    
    $pending = Invoke-WebRequest -Uri "http://localhost:8000/admin/drivers/pending?page=1&limit=20" `
        -UseBasicParsing `
        -Headers @{"Authorization" = "Bearer $token"} `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $pendingList = $pending.Content | ConvertFrom-Json
    Write-Host "✅ Admin pending drivers endpoint working" -ForegroundColor Green
    Write-Host "   Found $($pendingList.data.Count) pending drivers" -ForegroundColor Gray
} catch {
    Write-Host "❌ Admin pending drivers failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

# 6. Test Database Connection
Write-Host ""
Write-Host "6. Database Status" -ForegroundColor Yellow
try {
    # Try to get any user to verify DB connection
    $adminLoginData = @{
        email = "admin@nm-ride.com"
        password = "Admin@123"
    } | ConvertTo-Json
    
    $login = Invoke-WebRequest -Uri "http://localhost:8000/auth/login" `
        -UseBasicParsing `
        -Method Post `
        -Headers @{"Content-Type" = "application/json"} `
        -Body $adminLoginData `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $token = ($login.Content | ConvertFrom-Json).access_token
    
    $me = Invoke-WebRequest -Uri "http://localhost:8000/users/me" `
        -UseBasicParsing `
        -Headers @{"Authorization" = "Bearer $token"} `
        -TimeoutSec 5 `
        -ErrorAction Stop
    
    $user = $me.Content | ConvertFrom-Json
    Write-Host "✅ Database connection working" -ForegroundColor Green
    Write-Host "   Authenticated as: $($user.email)" -ForegroundColor Gray
} catch {
    Write-Host "❌ Database connection failed" -ForegroundColor Red
    Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
}

Write-Host ""
Write-Host "=== HEALTH CHECK COMPLETE ===" -ForegroundColor Cyan
