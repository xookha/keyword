import datetime

from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now


class User(AbstractUser):

    @property
    def has_perm(self) -> bool:
        """Check if user has perm to create url."""
        if not hasattr(self, 'urlperm'):
            return True
        if hasattr(self, 'urlperm') and (
                self.urlperm.is_payed or
                self.urlperm.updated + datetime.timedelta(
                    days=settings.LIMIT_HOURS
                ) < now()
        ):
            return True
        return False
