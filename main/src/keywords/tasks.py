import requests

from celery import task

from django.conf import settings


@task
def update_keywords(address_id, address_url):
    """Call service to get title."""
    requests.post(
        f'{settings.KW_SERVICE_URL}{address_id}',
        json={'url': address_url}
    )
