from django.contrib import admin
from .models import WatchItem

@admin.register(WatchItem)
class WatchItemAdmin(admin.ModelAdmin):
    list_display = ("user", "ticker", "target_price", "direction", "is_active", "last_trigger_at", "updated_at")
    list_filter = ("direction", "is_active")
    search_fields = ("ticker", "user__username")
