from rest_framework import serializers
from ..models import WatchItem

class WatchItemSerializer(serializers.ModelSerializer):
    symbol = serializers.CharField(write_only=True, required=False)
    targetPrice = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False)
    target = serializers.DecimalField(max_digits=12, decimal_places=2, write_only=True, required=False)

    class Meta:
        model = WatchItem
        fields = (
            "id",
            "ticker",        # nome canônico no modelo
            "symbol",        # alias de entrada
            "target_price",  # canônico
            "targetPrice",   # alias de entrada
            "target",        # alias de entrada
            "direction",
            "notes",
            "is_active",
            "created_at",
            "updated_at",
        )
        read_only_fields = ("id", "created_at", "updated_at")

    def to_internal_value(self, data):
        # Trabalhar numa cópia
        data = {**data}

        # symbol -> ticker (se vier)
        if "symbol" in data and "ticker" not in data:
            data["ticker"] = data.pop("symbol")

        # targetPrice/target -> target_price (se vier)
        if "target_price" not in data:
            if "targetPrice" in data:
                data["target_price"] = data.pop("targetPrice")
            elif "target" in data:
                data["target_price"] = data.pop("target")

        return super().to_internal_value(data)

    def validate(self, attrs):
        # default pra direction se não vier (acima do alvo)
        if not attrs.get("direction"):
            attrs["direction"] = "above"
        return attrs
