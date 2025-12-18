from django.contrib import admin

from .models import AgentApplication


@admin.register(AgentApplication)
class AgentApplicationAdmin(admin.ModelAdmin):
	list_display = (
		"agent_id",
		"full_name",
		"applicant_role",
		"status",
		"submitted_at",
	)
	list_filter = ("status", "applicant_role", "submitted_at")
	search_fields = ("agent_id", "full_name", "email", "phone")
	readonly_fields = ("submitted_at", "updated_at", "user_agent", "ip_address")
