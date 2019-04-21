import base64
import json
import requests

from celery import task

from django.conf import settings

from .models import Payment


@task
def send_callback(payment_id: int) -> None:
    """Send callback about payment."""
    payment = Payment.objects.get(id=payment_id)
    json_data = {
            'status': 'success',
            'pay_id': payment.pay_id,
            'amount': payment.amount,
            'info': payment.info,
        }
    requests.post(
        payment.callback_url,
        json={'data': base64.urlsafe_b64encode(json.dumps(json_data).encode()).decode()},
        headers={'pay-service': settings.PAYMENT_SERVICE_TOKEN}
    )
