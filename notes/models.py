from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

class WatchItem(models.Model):
    DIRECTION_CHOICES = [
        ("above", "Acima do alvo"),
        ("below", "Abaixo do alvo"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="watchitems")
    ticker = models.CharField(max_length=32)
    target_price = models.DecimalField(max_digits=16, decimal_places=4)
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES, default="above")
    notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    last_trigger_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "ticker")  # 1 watch por ticker p/ usuário 
    def __str__(self):
        return f"{self.user} - {self.ticker} ({self.direction} {self.target_price})"
