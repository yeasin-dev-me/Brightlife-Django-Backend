from django.contrib import admin
from .models import MembershipApplication, Nominee, ApplicationStatusHistory


# Minimal admin registration for Python 3.14 compatibility
# Removed all customizations to avoid template context issues

@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = ['proposal_number', 'first_name', 'last_name', 'status', 'created_at']
    search_fields = ['proposal_number', 'first_name', 'last_name']


@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ['name', 'relationship', 'share_percentage']
    search_fields = ['name']


@admin.register(ApplicationStatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['previous_status', 'new_status', 'changed_by', 'timestamp']
    search_fields = ['changed_by']
