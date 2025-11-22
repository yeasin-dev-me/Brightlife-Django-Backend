from django.contrib import admin
from django.utils.html import format_html
from .models import PaymentProof


@admin.register(PaymentProof)
class PaymentProofAdmin(admin.ModelAdmin):
    """Admin interface for PaymentProof model"""
    
    list_display = [
        'transaction_id',
        'payer_name',
        'payment_method_badge',
        'amount',
        'status_badge',
        'submitted_at',
        'has_screenshot'
    ]
    
    list_filter = [
        'status',
        'payment_method',
        'submitted_at',
        'verified_at'
    ]
    
    search_fields = [
        'transaction_id',
        'payer_name',
        'payer_contact'
    ]
    
    readonly_fields = [
        'id',
        'submitted_at',
        'updated_at',
        'ip_address',
        'user_agent',
        'screenshot_preview'
    ]
    
    fieldsets = (
        ('Payment Information', {
            'fields': (
                'transaction_id',
                'payment_method',
                'amount',
                'payer_name',
                'payer_contact'
            )
        }),
        ('Proof & Notes', {
            'fields': (
                'screenshot',
                'screenshot_preview',
                'notes'
            )
        }),
        ('Verification', {
            'fields': (
                'status',
                'verified_at',
                'verified_by',
                'rejection_reason'
            )
        }),
        ('Association', {
            'fields': ('membership_application',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'id',
                'submitted_at',
                'updated_at',
                'ip_address',
                'user_agent'
            ),
            'classes': ('collapse',)
        })
    )
    
    actions = ['verify_payments', 'mark_pending']
    
    def payment_method_badge(self, obj):
        """Display payment method with color badge"""
        colors = {
            'touch-n-go': '#00BCD4',  # Cyan
            'bkash': '#E91E63',       # Pink (bKash brand color)
            'bank-transfer': '#673AB7' # Deep Purple
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.payment_method, '#666'),
            obj.get_payment_method_display()
        )
    payment_method_badge.short_description = 'Payment Method'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'pending': '#FF9800',     # Orange
            'verified': '#4CAF50',    # Green
            'rejected': '#F44336'     # Red
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 3px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def has_screenshot(self, obj):
        """Show if screenshot is uploaded"""
        if obj.screenshot:
            return format_html('<span style="color: green;">✓</span>')
        return format_html('<span style="color: red;">✗</span>')
    has_screenshot.short_description = 'Screenshot'
    
    def screenshot_preview(self, obj):
        """Display screenshot preview"""
        if obj.screenshot:
            return format_html(
                '<a href="{}" target="_blank"><img src="{}" style="max-width: 300px; max-height: 300px;" /></a>',
                obj.screenshot.url,
                obj.screenshot.url
            )
        return '-'
    screenshot_preview.short_description = 'Screenshot Preview'
    
    def verify_payments(self, request, queryset):
        """Bulk verify payments"""
        updated = queryset.filter(status='pending').update(
            status='verified',
            verified_by=request.user
        )
        self.message_user(request, f'{updated} payment(s) verified successfully.')
    verify_payments.short_description = 'Verify selected payments'
    
    def mark_pending(self, request, queryset):
        """Mark as pending"""
        updated = queryset.update(status='pending')
        self.message_user(request, f'{updated} payment(s) marked as pending.')
    mark_pending.short_description = 'Mark as pending'
    
    def save_model(self, request, obj, form, change):
        """Auto-set verified_by when status changes to verified"""
        if change and obj.status == 'verified' and not obj.verified_by:
            obj.verified_by = request.user
        super().save_model(request, obj, form, change)
