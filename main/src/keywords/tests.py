from unittest import mock

from django.conf import settings

from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase
from rest_framework_jwt.serializers import (
    jwt_payload_handler,
    jwt_encode_handler
)

from accounts.models import User
from keywords.serializers import UserPaymentSerializer
from .models import Address, UrlPerm, UserPayment
from . import serializers

TEST_URL_ADDR = 'http://www.imdb.com/title/tt0108778/'


def get_token(user):
    """
    Create token (for tests).
    :param user:
    :return:
    """
    payload = jwt_payload_handler(user)
    token = jwt_encode_handler(payload)
    auth = 'JWT {0}'.format(token)
    return auth


@mock.patch('keywords.tasks.update_keywords.delay', return_value=None)
class AddressCreateViewTest(APITestCase):
    """Tests for AddressCreateView."""

    def setUp(self):
        """Base data for tests."""
        self.url = reverse('create_address')
        self.user = User.objects.create(username='user')

    def test_auth(self, update_keywords_mock):
        """Test creating address with valid data."""
        response = self.client.post(
            self.url,
            {'url': TEST_URL_ADDR}
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_success_create(self, update_keywords_mock):
        """Test creating address with valid data."""
        response = self.client.post(
            self.url,
            {'url': TEST_URL_ADDR},
            HTTP_AUTHORIZATION=get_token(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(
            response.data,
            serializers.AddressSerializer(
                Address.objects.get(id=response.data.get('id'))
            ).data
        )

    def test_invalid_url(self, update_keywords_mock):
        """Test creating address with invalid url."""
        response = self.client.post(
            self.url,
            {'url': 'some string'},
            HTTP_AUTHORIZATION=get_token(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(
            response.data['url'],
            ['some string is not a valid url to parse.', 'Enter a valid URL.']
        )

    def test_expire_perm(self, update_keywords_mock):
        """Test creating address if user used free limit."""
        UrlPerm.objects.create(user=self.user)
        response = self.client.post(
            self.url,
            {'url': TEST_URL_ADDR},
            HTTP_AUTHORIZATION=get_token(self.user)
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)


@mock.patch('keywords.tasks.update_keywords.delay', return_value=None)
class UpdateAddressKeywordsViewTest(APITestCase):
    """Tests for UpdateAddressKeywordsView."""

    def setUp(self):
        """Base data for tests."""
        self.address = Address.objects.create(url=TEST_URL_ADDR)
        self.url = reverse('update_address_keywords', args=[self.address.id])

    def test_success_update(self, update_keywords_mock):
        """Test calling update address keywords."""
        response = self.client.post(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)


class AddressDestroyViewTest(APITestCase):
    """Tests for AddressDestroyView."""

    def setUp(self):
        """Base data for tests."""
        self.address = Address.objects.create(url=TEST_URL_ADDR)
        self.url = reverse('delete_address', args=[self.address.id])

    def test_delete_address(self):
        """Test delete address."""
        response = self.client.delete(self.url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Address.objects.filter(id=self.address.id).count(), 0)


class AddressViewSetTest(APITestCase):
    """Tests for AddressViewSet."""

    def setUp(self):
        """Base data for test."""
        self.address = Address.objects.create(url=TEST_URL_ADDR)
        self.url_list = reverse('addresses-list')
        self.url_detail = reverse('addresses-detail', args=[self.address.id])

    def test_address_list(self):
        """Test address list."""
        response = self.client.get(self.url_list)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.AddressDetailSerializer(
                Address.objects.all(), many=True
            ).data
        )

    def test_address_detail(self):
        """Test address detail."""
        response = self.client.get(self.url_detail)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(
            response.data,
            serializers.AddressDetailSerializer(self.address).data
        )


class AddressKeywordsCallbackViewTest(APITestCase):
    """Tests for AddressKeywordsCallbackView."""

    def setUp(self):
        """Base data for tests."""
        self.address = Address.objects.create(url=TEST_URL_ADDR)
        self.url = reverse(
            'update_address_keywords_callback',
            args=[self.address.id]
        )
        self.data = {'keywords': ['some', 'title']}

    def test_success_update(self):
        """Test update address keywords."""
        response = self.client.put(
            self.url,
            self.data,
            HTTP_KW_SERVICE=f'{settings.KW_SERVICE_TOKEN}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.address.refresh_from_db()
        self.assertEqual(
            response.data,
            serializers.AddressUpdateSerializer(self.address).data
        )

    def test_perms(self):
        """Test update address without token."""
        response = self.client.put(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_perms_wrong_token(self):
        """Test update address with wrong token."""
        response = self.client.put(
            self.url,
            self.data,
            HTTP_KW_SERVICE='Token 0'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PaymentCallbackViewTest(APITestCase):
    """Tests for PaymentCallbackView."""

    def setUp(self):
        """Base data for tests."""
        self.user = User.objects.create(username='user')
        self.payment = UserPayment.objects.create(
            user=self.user,
            amount=settings.DEFAULT_PAY_AMOUNT,
            info=settings.DEFAULT_PAY_INFO
        )
        UrlPerm.objects.create(user=self.user)
        self.url = reverse(
            'update_payment_callback',
            args=[self.payment.id]
        )
        self.data = {
            'amount': '10',
            'info': 'info',
            'status': 'success',
            'pay_id': 1
        }

    def test_success_update_payment(self):
        """Test update payment."""
        response = self.client.post(
            self.url,
            self.data,
            HTTP_PAY_SERVICE=f'{settings.PAYMENT_SERVICE_TOKEN}'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.payment.refresh_from_db()
        self.assertEqual(self.payment.status, UserPayment.SUCCESS)
        self.user.refresh_from_db()
        self.assertTrue(self.user.urlperm.is_payed)

    def test_perms(self):
        """Test update payment without token."""
        response = self.client.post(self.url, self.data)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_perms_wrong_token(self):
        """Test update payment with wrong token."""
        response = self.client.post(
            self.url,
            self.data,
            HTTP_KW_SERVICE='Token 0'
        )
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
