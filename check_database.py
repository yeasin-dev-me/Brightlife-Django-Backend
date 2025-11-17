#!/usr/bin/env python
"""
Database inspection script - Check all tables and data
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from apps.membership.models import MembershipApplication, Nominee
from apps.users.models import User

print('\n' + '='*80)
print('DATABASE INSPECTION')
print('='*80 + '\n')

# Get database name
with connection.cursor() as cursor:
    cursor.execute("SELECT current_database()")
    db_name = cursor.fetchone()[0]
    print(f'Database: {db_name}')
    
    # Get all tables
    cursor.execute("""
        SELECT table_name 
        FROM information_schema.tables 
        WHERE table_schema = 'public' 
        ORDER BY table_name
    """)
    tables = cursor.fetchall()
    print(f'Total Tables: {len(tables)}\n')
    
    print('Tables:')
    for i, (table,) in enumerate(tables, 1):
        print(f'  {i}. {table}')

print('\n' + '-'*80 + '\n')

# Check Users
users = User.objects.all()
print(f'USERS: {users.count()} records')
for user in users:
    print(f'  - {user.email} ({user.get_full_name()}) - Active: {user.is_active}')

print('\n' + '-'*80 + '\n')

# Check Membership Applications
apps = MembershipApplication.objects.all().order_by('-created_at')
print(f'MEMBERSHIP APPLICATIONS: {apps.count()} records\n')

for i, app in enumerate(apps, 1):
    print(f'{i}. {app.proposal_number}')
    print(f'   Name: {app.first_name} {app.middle_name} {app.last_name}')
    print(f'   Type: {app.membership_type}')
    print(f'   Mobile: {app.mobile_number}')
    print(f'   Email: {app.email}')
    print(f'   Status: {app.status.upper()}')
    print(f'   DOB: {app.date_of_birth} (Age: {app.age})')
    print(f'   Gender: {app.gender}')
    print(f'   Marital Status: {app.marital_status}')
    print(f'   NID: {app.nid_number}')
    print(f'   Occupation: {app.occupation}')
    
    # Files
    files_uploaded = []
    if app.photo:
        files_uploaded.append(f'Photo: {app.photo.name}')
    if app.age_proof:
        files_uploaded.append(f'Age Proof: {app.age_proof.name}')
    if app.driving_license:
        files_uploaded.append(f'Driving License: {app.driving_license.name}')
    
    if files_uploaded:
        print(f'   Files: {", ".join(files_uploaded)}')
    else:
        print(f'   Files: None')
    
    # Nominees
    nominees = app.nominees.all()
    if nominees.exists():
        print(f'   Nominees: {nominees.count()}')
        for j, nom in enumerate(nominees, 1):
            print(f'     {j}. {nom.name} ({nom.relationship}) - {nom.share_percentage}%')
    else:
        print(f'   Nominees: None')
    
    print(f'   Created: {app.created_at}')
    print(f'   Updated: {app.updated_at}')
    print()

print('-'*80 + '\n')

# Check Nominees separately
all_nominees = Nominee.objects.all()
print(f'NOMINEES (Total): {all_nominees.count()} records')
for nom in all_nominees:
    print(f'  - {nom.name} for {nom.application.proposal_number}')

print('\n' + '='*80)
print('DATABASE INSPECTION COMPLETE')
print('='*80 + '\n')
