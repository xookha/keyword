from django.db import models


class Payment(models.Model):
    """Model for payments."""

    SUCCESS = 'success'
    IN_PROGRESS = 'in_progress'
    STATUSES = (
        (SUCCESS, 'success'),
        (IN_PROGRESS, 'in progress'),
    )

    amount = models.DecimalField(max_digits=20, decimal_places=2)
    info = models.CharField(max_length=50)
    pay_id = models.CharField(max_length=60, unique=True)
    callback_url = models.URLField(null=True, blank=True)
    status = models.CharField(
        max_length=20,
        choices=STATUSES,
        default=IN_PROGRESS
    )

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return self.pay_id
