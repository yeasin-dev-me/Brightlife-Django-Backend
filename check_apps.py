from apps.membership.models import MembershipApplication

apps = MembershipApplication.objects.all()
print(f'Total applications: {apps.count()}')

for app in apps:
    print(f'{app.proposal_number} - {app.first_name} {app.last_name} - Status: {app.status}')
