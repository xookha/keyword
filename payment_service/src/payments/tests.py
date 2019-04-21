import base64
import json

from django.conf import settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

from .models import Payment


class PayViewTest(APITestCase):
    """Tests for PayView."""

    def test_success_get(self):
        """Test successful get info."""
        data = {
            'amount': '10',
            'info': 'info',
            'link': f'{settings.PAYMENT_SERVICE_URL}{reverse("payment_create", args=[1])}',
            'pay_id': '1'
        }
        pay_data = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
        url = f"{reverse('payment_info')}?data={pay_data}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_failure_get(self):
        """Test with empty amount."""
        url = f"{reverse('payment_info')}"
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['data'], 'data should be provided.')


class PaymentCreateViewTest(APITestCase):
    """Tests for PaymentCreateView."""

    def setUp(self):
        """Base data for tests."""
        self.data = {
            'amount': '10',
            'info': 'info',
            'pay_id': '1'
        }
        self.request_data = {
            'data': base64.urlsafe_b64encode(json.dumps(self.data).encode()).decode()
        }
        self.payment = Payment.objects.create(**self.data)
        self.url = reverse('payment_create', args=[self.payment.id])

    def test_success_create(self):
        """Test successful payment."""
        response = self.client.post(self.url, self.request_data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)

