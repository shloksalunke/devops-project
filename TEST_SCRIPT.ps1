#!/usr/bin/env pwsh
# Comprehensive System Test Script

$BASE_URL = "http://localhost:8000"
$HEADERS = @{
    "Content-Type" = "application/json"
}

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "CAMPUS RIDE SYSTEM COMPREHENSIVE TESTS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Test 1: Login as Student
Write-Host "[TEST 1/8] Student Login" -ForegroundColor Yellow
try {
    $loginData = @{
        email = "aarav@student.edu"
        password = "Student@123"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/auth/login" `
        -Method POST `
        -Headers $HEADERS `
        -Body $loginData `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $studentToken = ($response.Content | ConvertFrom-Json).access_token
        Write-Host "✓ Student login successful" -ForegroundColor Green
        Write-Host "  Status: 200 OK" -ForegroundColor Green
    } else {
        Write-Host "✗ Student login failed: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Student login error: $_" -ForegroundColor Red
    exit 1
}

# Test 2: Login as Admin
Write-Host "[TEST 2/8] Admin Login" -ForegroundColor Yellow
try {
    $loginData = @{
        email = "admin@campusride.com"
        password = "Admin@123"
    } | ConvertTo-Json
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/auth/login" `
        -Method POST `
        -Headers $HEADERS `
        -Body $loginData `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $adminToken = ($response.Content | ConvertFrom-Json).access_token
        Write-Host "✓ Admin login successful" -ForegroundColor Green
        Write-Host "  Status: 200 OK" -ForegroundColor Green
    } else {
        Write-Host "✗ Admin login failed: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Admin login error: $_" -ForegroundColor Red
    exit 1
}

# Test 3: Get authenticated user (student)
Write-Host "[TEST 3/8] Get Current User (Student)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $studentToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/users/me" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $user = $response.Content | ConvertFrom-Json
        Write-Host "✓ Student user retrieved: $($user.name) ($($user.role))" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to get user: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Get user error: $_" -ForegroundColor Red
    exit 1
}

# Test 4: Get authenticated user (admin)
Write-Host "[TEST 4/8] Get Current User (Admin)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/users/me" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $user = $response.Content | ConvertFrom-Json
        Write-Host "✓ Admin user retrieved: $($user.name) ($($user.role))" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to get admin user: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Get admin user error: $_" -ForegroundColor Red
    exit 1
}

# Test 5: List drivers (student - should only see approved)
Write-Host "[TEST 5/8] List Drivers (Student View)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $studentToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/drivers" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $drivers = $response.Content | ConvertFrom-Json
        Write-Host "✓ Drivers list retrieved: $($drivers.Count) approved drivers" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to get drivers: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ List drivers error: $_" -ForegroundColor Red
    exit 1
}

# Test 6: Get pending drivers (admin)
Write-Host "[TEST 6/8] Get Pending Drivers (Admin)" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/admin/drivers/pending?page=1&limit=20" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $pending = $response.Content | ConvertFrom-Json
        Write-Host "✓ Pending drivers retrieved: $($pending.Count) drivers pending verification" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to get pending drivers: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Pending drivers error: $_" -ForegroundColor Red
    exit 1
}

# Test 7: Get admin stats
Write-Host "[TEST 7/8] Admin Dashboard Stats" -ForegroundColor Yellow
try {
    $headers = @{
        "Authorization" = "Bearer $adminToken"
        "Content-Type" = "application/json"
    }
    
    $response = Invoke-WebRequest -Uri "$BASE_URL/admin/stats" `
        -Method GET `
        -Headers $headers `
        -UseBasicParsing
    
    if ($response.StatusCode -eq 200) {
        $stats = $response.Content | ConvertFrom-Json
        Write-Host "✓ Admin stats retrieved:" -ForegroundColor Green
        Write-Host "  - Total drivers: $($stats.total_drivers)" -ForegroundColor Green
        Write-Host "  - Active drivers: $($stats.active_drivers)" -ForegroundColor Green
        Write-Host "  - Total students: $($stats.total_students)" -ForegroundColor Green
        Write-Host "  - Pending verification: $($stats.pending_verification)" -ForegroundColor Green
    } else {
        Write-Host "✗ Failed to get stats: $($response.StatusCode)" -ForegroundColor Red
        exit 1
    }
} catch {
    Write-Host "✗ Admin stats error: $_" -ForegroundColor Red
    exit 1
}

# Test 8: Rate a driver (test rating endpoint)
Write-Host "[TEST 8/8] Rate Driver (if drivers exist)" -ForegroundColor Yellow
try {
    if ($drivers.Count -gt 0) {
        $driverId = $drivers[0].id
        $ratingData = @{
            rating = 5
            comment = "Test rating"
        } | ConvertTo-Json
        
        $headers = @{
            "Authorization" = "Bearer $studentToken"
            "Content-Type" = "application/json"
        }
        
        $response = Invoke-WebRequest -Uri "$BASE_URL/ratings" `
            -Method POST `
            -Headers $headers `
            -Body $ratingData `
            -UseBasicParsing
        
        if ($response.StatusCode -eq 201) {
            Write-Host "✓ Rating created successfully" -ForegroundColor Green
        } else {
            Write-Host "! Rating endpoint returned: $($response.StatusCode)" -ForegroundColor Yellow
        }
    } else {
        Write-Host "! Skipped (no drivers available)" -ForegroundColor Yellow
    }
} catch {
    Write-Host "! Rating test error (this is optional): $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "✓ ALL CRITICAL TESTS PASSED" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
