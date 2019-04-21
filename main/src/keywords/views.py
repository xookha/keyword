import base64
import json

from django.utils.decorators import method_decorator
from django.conf import settings

from rest_framework.generics import (
    CreateAPIView,
    DestroyAPIView,
    UpdateAPIView,
    get_object_or_404,
    GenericAPIView,
)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ReadOnlyModelViewSet
from drf_yasg.utils import swagger_auto_schema

from .decorators import KWServicePerm, PayServicePerm
from .models import Address, UserPayment, UrlPerm
from .serializers import (
    AddressSerializer,
    AddressDetailSerializer,
    AddressUpdateSerializer,
    UserPaymentSerializer,
)
from .tasks import update_keywords


class AddressCreateView(CreateAPIView):
    """Add new URL Address."""
    permission_classes = (IsAuthenticated,)
    serializer_class = AddressSerializer

    def perform_create(self, serializer):
        """Create address, call updating keywords."""
        ins = serializer.save()
        if self.request.user.has_perm:
            update_keywords.delay(ins.id, ins.url)

    def post(self, request, *args, **kwargs):
        """
        If user used free limit, return payment.
        If user still has perms create url obj.
        :param request:
        :param args:
        :param kwargs:
        :return:
        """
        if not request.user.has_perm:
            serializer = self.get_serializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            address = serializer.save()
            payment = UserPayment.objects.create(
                user=request.user,
                amount=settings.DEFAULT_PAY_AMOUNT,
                info=settings.DEFAULT_PAY_INFO,
                status=UserPayment.IN_PROGRESS,
                address=address
            )
            data = UserPaymentSerializer(payment).data

            response_data = serializer.data
            encoded_string = base64.urlsafe_b64encode(json.dumps(data).encode()).decode()
            response_data.update({
                'payment': f'{settings.PAYMENT_SERVICE_URL}payment/info?data={encoded_string}',
                'url': address.get_absolute_url()
            })
            return Response(response_data, status=200)
        UrlPerm.objects.update_or_create(
            user=request.user,
            defaults={'is_payed': False}
        )
        return super().post(request, *args, **kwargs)


class UpdateAddressKeywordsView(APIView):
    """Update URL keywords."""

    @swagger_auto_schema(
        operation_description="Ask to update URL keywords.",
        responses={204: ''}
    )
    def post(self, request, *args, **kwargs):
        """Update processing status of address. Call updating keywords."""
        address = get_object_or_404(Address, id=self.kwargs.get('pk'))
        address.is_processed = False
        address.save()
        # Update keywords.
        update_keywords.delay(address.id, address.url)
        return Response(status=204)


@method_decorator(name='list', decorator=swagger_auto_schema(
    operation_description="Get Address URLs with keywords. "
    "Field `is_processed` shows progress status of generating keywords, "
    "returns `True` if process finished."
))
@method_decorator(name='retrieve', decorator=swagger_auto_schema(
    operation_description="Get detail Address URL with keywords. "
    "Field `is_processed` shows progress status of generating keywords, "
    "returns `True` if process finished."
))
class AddressViewSet(ReadOnlyModelViewSet):
    """Url Addresses management."""
    serializer_class = AddressDetailSerializer
    queryset = Address.objects.all()


class AddressDestroyView(DestroyAPIView):
    """Delete Address URL."""
    queryset = Address.objects.all()


@KWServicePerm
class AddressKeywordsCallbackView(UpdateAPIView):
    """Callback to update address with found keywords."""
    allowed_methods = ['put']
    serializer_class = AddressUpdateSerializer
    queryset = Address.objects.all()

    def perform_update(self, serializer):
        serializer.save(is_processed=True)


@PayServicePerm
class PaymentCallbackView(GenericAPIView):
    """Callback to update access to creating urls."""
    queryset = UserPayment.objects.all()
    # needs some check

    def post(self, request, *args, **kwargs):
        payment = self.get_object()
        payment.status = UserPayment.SUCCESS
        payment.save()
        perm = UrlPerm.objects.get(user=payment.user)
        perm.is_payed = True
        perm.save()
        ins = payment.address
        if ins:
            update_keywords.delay(ins.id, ins.url)
        return Response(status=200)
