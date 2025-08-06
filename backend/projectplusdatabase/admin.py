from django.contrib import admin
from .models import EATemplate, UserEAInstance, EAPerformance

@admin.register(EATemplate)
class EATemplateAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at", "updated_at")
    search_fields = ("name",)
    readonly_fields = ("id", "created_at", "updated_at")

@admin.register(UserEAInstance)
class UserEAInstanceAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "ea_template", "mt5_account", "is_active", "created_at")
    search_fields = ("user__email", "ea_template__name", "mt5_login")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user", "ea_template", "mt5_account")

@admin.register(EAPerformance)
class EAPerformanceAdmin(admin.ModelAdmin):
    list_display = ("id", "user_ea_instance", "created_at", "updated_at")
    search_fields = ("user_ea_instance__user__email", "user_ea_instance__ea_template__name")
    readonly_fields = ("id", "created_at", "updated_at")
    raw_id_fields = ("user_ea_instance",)
