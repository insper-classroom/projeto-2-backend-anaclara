from rest_framework import serializers
from ..models import WatchItem

class WatchItemSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(write_only=True, required=False)
    targetPrice = serializers.DecimalField(
        write_only=True, required=False, max_digits=12, decimal_places=2
    )

    class Meta:
        model = WatchItem
        fields = [
            "id",
            "ticker",
            "target_price",
            "notes",
            "direction",
            "is_active",
            "created_at",
            "updated_at",
            "symbol",
            "targetPrice",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate(self, attrs):
        sym = attrs.pop("symbol", None)
        if sym and not attrs.get("ticker"):
            attrs["ticker"] = sym

        tp = attrs.pop("targetPrice", None)
        if tp is not None and attrs.get("target_price") is None:
            attrs["target_price"] = tp
        return attrs
