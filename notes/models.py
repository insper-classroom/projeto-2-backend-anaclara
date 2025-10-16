from django.db import models

class WatchItem(models.Model):
    DIRECTION_CHOICES = [
        ("above", "Acima do alvo"),
        ("below", "Abaixo do alvo"),
    ]

    # sem usuário
    ticker = models.CharField(max_length=32, unique=True, db_index=True)
    target_price = models.DecimalField(max_digits=16, decimal_places=4)
    direction = models.CharField(max_length=8, choices=DIRECTION_CHOICES, default="above")
    notes = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    last_trigger_at = models.DateTimeField(null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)

    def __str__(self):
        return f"{self.ticker} ({self.direction} {self.target_price})"
