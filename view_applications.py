#!/usr/bin/env python
"""
View membership applications with file URLs
Workaround for Python 3.14 admin compatibility issue
"""
import django
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.membership.models import MembershipApplication

apps = MembershipApplication.objects.all().order_by('-created_at')

print(f'\n{"="*80}')
print(f'MEMBERSHIP APPLICATIONS - Total: {apps.count()}')
print(f'{"="*80}\n')

for i, app in enumerate(apps, 1):
    print(f'{i}. Proposal: {app.proposal_number}')
    print(f'   Name: {app.first_name} {app.middle_name} {app.last_name}')
    print(f'   Mobile: {app.mobile_number}')
    print(f'   Email: {app.email}')
    print(f'   Status: {app.status.upper()}')
    print(f'   Membership Type: {app.membership_type}')
    
    # File URLs
    print(f'\n   📁 Uploaded Files:')
    if app.photo:
        print(f'      Photo: http://localhost:8000{app.photo.url}')
    else:
        print(f'      Photo: Not uploaded')
        
    if app.age_proof:
        print(f'      Age Proof: http://localhost:8000{app.age_proof.url}')
    else:
        print(f'      Age Proof: Not uploaded')
        
    if app.driving_license:
        print(f'      Driving License: http://localhost:8000{app.driving_license.url}')
    else:
        print(f'      Driving License: Not uploaded')
    
    # Nominees
    nominees = app.nominees.all()
    if nominees.exists():
        print(f'\n   👥 Nominees ({nominees.count()}):')
        for j, nominee in enumerate(nominees, 1):
            print(f'      {j}. {nominee.name} - {nominee.relationship} ({nominee.share_percentage}%)')
            print(f'         Mobile: {nominee.mobile_number}, NID: {nominee.nid_number}')
    
    print(f'\n   Created: {app.created_at}')
    print(f'   Updated: {app.updated_at}')
    print(f'\n{"-"*80}\n')

print(f'\n{"="*80}')
print(f'View files in browser: http://localhost:8000/media/...')
print(f'{"="*80}\n')
