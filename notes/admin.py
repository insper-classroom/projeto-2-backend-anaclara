from django.contrib import admin
from .models import WatchItem

@admin.register(WatchItem)
class WatchItemAdmin(admin.ModelAdmin):
    list_display = ("ticker", "target_price", "direction", "is_active", "updated_at")
    search_fields = ("ticker", "notes")
    list_filter = ("direction", "is_active")
    ordering = ("-updated_at",)
    readonly_fields = ("created_at", "updated_at", "last_trigger_at")
