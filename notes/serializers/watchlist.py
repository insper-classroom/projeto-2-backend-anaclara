from rest_framework import serializers
from notes.models import WatchItem

class WatchItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = WatchItem
        fields = [
            "id", "ticker", "target_price", "direction", "notes",
            "is_active", "last_trigger_at", "created_at", "updated_at"
        ]
        read_only_fields = ["last_trigger_at", "created_at", "updated_at"]
