from django.contrib import admin
from django.utils.html import format_html
from .models import MembershipApplication, Nominee, ApplicationStatusHistory


class NomineeInline(admin.TabularInline):
    model = Nominee
    extra = 0
    fields = ['name', 'relationship', 'mobile_number', 'share_percentage', 'id_proof']
    readonly_fields = []


class StatusHistoryInline(admin.TabularInline):
    model = ApplicationStatusHistory
    extra = 0
    readonly_fields = ['previous_status', 'new_status', 'changed_by', 'notes', 'timestamp']
    can_delete = False


@admin.register(MembershipApplication)
class MembershipApplicationAdmin(admin.ModelAdmin):
    list_display = [
        'proposal_number', 'full_name', 'membership_type', 
        'status_badge', 'email', 'mobile_number', 'created_at'
    ]
    list_filter = ['status', 'membership_type', 'gender', 'created_at']
    search_fields = [
        'proposal_number', 'first_name', 'last_name', 
        'email', 'mobile_number', 'nid_number'
    ]
    readonly_fields = [
        'id', 'proposal_number', 'age', 'created_at', 
        'updated_at', 'declaration_date'
    ]

    fieldsets = (
        ('Application Info', {
            'fields': ('id', 'proposal_number', 'status', 'created_at', 'updated_at')
        }),
        ('Personal Information', {
            'fields': (
                'membership_type', 'first_name', 'middle_name', 'last_name',
                'date_of_birth', 'age', 'gender', 'marital_status'
            )
        }),
        ('Contact Information', {
            'fields': (
                'mobile_number', 'email', 
                'emergency_contact_name', 'emergency_contact_number'
            )
        }),
        ('Identification', {
            'fields': ('nid_number', 'passport_number')
        }),
        ('Occupation', {
            'fields': ('occupation', 'organization_name', 'monthly_income')
        }),
        ('Family Details', {
            'fields': (
                'spouse_name', 'number_of_children', 
                'father_name', 'mother_name'
            )
        }),
        ('Address', {
            'fields': ('present_address', 'permanent_address')
        }),
        ('Physical Measurements', {
            'fields': ('weight', 'height', 'blood_group', 'surgery_history')
        }),
        ('Documents', {
            'fields': (
                'photo', 'age_proof', 'driving_license',
                'medical_records', 'prescription'
            )
        }),
        ('Declaration', {
            'fields': ('terms_accepted', 'declaration_date')
        }),
    )

    inlines = [NomineeInline, StatusHistoryInline]

    def full_name(self, obj):
        """Display full name"""
        return f"{obj.first_name} {obj.last_name}"
    full_name.short_description = 'Name'

    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#FFA500',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'under_review': '#17a2b8'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'

    actions = ['mark_approved', 'mark_rejected', 'mark_under_review']

    def mark_approved(self, request, queryset):
        """Bulk approve applications"""
        for app in queryset:
            ApplicationStatusHistory.objects.create(
                application=app,
                previous_status=app.status,
                new_status='approved',
                changed_by=request.user.username,
                notes='Bulk approved by admin'
            )
        queryset.update(status='approved')
        self.message_user(request, f'{queryset.count()} applications marked as approved')
    mark_approved.short_description = 'Mark selected as Approved'

    def mark_rejected(self, request, queryset):
        """Bulk reject applications"""
        for app in queryset:
            ApplicationStatusHistory.objects.create(
                application=app,
                previous_status=app.status,
                new_status='rejected',
                changed_by=request.user.username,
                notes='Bulk rejected by admin'
            )
        queryset.update(status='rejected')
        self.message_user(request, f'{queryset.count()} applications marked as rejected')
    mark_rejected.short_description = 'Mark selected as Rejected'

    def mark_under_review(self, request, queryset):
        """Bulk mark as under review"""
        for app in queryset:
            ApplicationStatusHistory.objects.create(
                application=app,
                previous_status=app.status,
                new_status='under_review',
                changed_by=request.user.username,
                notes='Bulk marked under review by admin'
            )
        queryset.update(status='under_review')
        self.message_user(request, f'{queryset.count()} applications marked as under review')
    mark_under_review.short_description = 'Mark selected as Under Review'


@admin.register(Nominee)
class NomineeAdmin(admin.ModelAdmin):
    list_display = ['name', 'application_proposal', 'relationship', 'share_percentage', 'mobile_number']
    list_filter = ['relationship']
    search_fields = ['name', 'nid_number', 'application__proposal_number']

    def application_proposal(self, obj):
        return obj.application.proposal_number
    application_proposal.short_description = 'Proposal Number'


@admin.register(ApplicationStatusHistory)
class StatusHistoryAdmin(admin.ModelAdmin):
    list_display = ['application_proposal', 'previous_status', 'new_status', 'changed_by', 'timestamp']
    list_filter = ['new_status', 'timestamp']
    search_fields = ['application__proposal_number', 'changed_by']
    readonly_fields = ['application', 'previous_status', 'new_status', 'changed_by', 'notes', 'timestamp']

    def application_proposal(self, obj):
        return obj.application.proposal_number
    application_proposal.short_description = 'Proposal Number'
