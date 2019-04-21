import requests

from django.contrib.postgres.fields import ArrayField
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _


def set_expire():
    pass


def check_url(value):
    """Check if url exists."""
    error = ValidationError(
        _('%(value)s is not a valid url to parse.'),
        params={'value': value},
    )
    try:
        res = requests.get(value)
        # Check if status code is successful.
        if res.status_code // 100 != 2:
            raise error
    except Exception:
        raise error


class Address(models.Model):
    """Model to manage URLs."""

    url = models.URLField(validators=[check_url])
    keywords = ArrayField(
        models.CharField(max_length=200),
        null=True,
        blank=True
    )
    is_processed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'URL Address'
        verbose_name_plural = 'URL Addresses'
        ordering = ('url',)

    def __str__(self):
        return self.url

    def get_absolute_url(self):
        return 'http://localhost:8000/' + reverse('addresses-detail', args=[self.id])


class UrlPerm(models.Model):
    """Perms to create new urls."""
    user = models.OneToOneField('accounts.User', on_delete=models.CASCADE)
    updated = models.DateTimeField(auto_now=True)
    is_payed = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Url perm for users'
        verbose_name_plural = 'Url perms for users'

    def __str__(self):
        return str(self.user)


class UserPayment(models.Model):
    """User`s payments."""

    SUCCESS = 'success'
    IN_PROGRESS = 'in_progress'
    STATUSES = (
        (SUCCESS, 'success'),
        (IN_PROGRESS, 'in progress'),
    )

    user = models.ForeignKey('accounts.User', on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUSES)
    amount = models.DecimalField(max_digits=20, decimal_places=2)
    info = models.CharField(max_length=50)
    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)
    address = models.ForeignKey(Address, on_delete=models.SET_NULL, null=True)

    class Meta:
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return str(self.user)
