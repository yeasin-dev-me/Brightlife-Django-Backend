# Quick Setup Script
Write-Host "BrightLife Django Backend - Setup" -ForegroundColor Green
Write-Host "=================================" -ForegroundColor Green
Write-Host ""

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Cyan
& .\.venv\Scripts\Activate.ps1

# Check PostgreSQL connection
Write-Host ""
Write-Host "Make sure PostgreSQL is running and database 'brightlife_db' exists" -ForegroundColor Yellow
Write-Host "To create database, run: psql -U postgres -c 'CREATE DATABASE brightlife_db;'" -ForegroundColor Yellow
Write-Host ""

# Run migrations
Write-Host "Running migrations..." -ForegroundColor Cyan
python manage.py makemigrations
python manage.py migrate

# Create superuser prompt
Write-Host ""
Write-Host "Do you want to create a superuser? (Y/N)" -ForegroundColor Yellow
$response = Read-Host
if ($response -eq 'Y' -or $response -eq 'y') {
    python manage.py createsuperuser
}

Write-Host ""
Write-Host "Setup complete!" -ForegroundColor Green
Write-Host "Run 'python manage.py runserver' to start the development server" -ForegroundColor Cyan
Write-Host "API will be available at: http://localhost:8000/api/v1/" -ForegroundColor Cyan
Write-Host "API Documentation: http://localhost:8000/api/schema/swagger-ui/" -ForegroundColor Cyan
