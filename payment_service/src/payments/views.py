import json
import base64

from drf_yasg.utils import swagger_auto_schema
from rest_framework.generics import CreateAPIView, GenericAPIView
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Payment
from .tasks import send_callback
from .swagger import payment_info_response
from .serializers import PaymentSerializer


class PayView(APIView):
    """
    Info about payment.
    Accepts next GET attrs: `amount`, `info`, `pay_id`, `callback_url`.
    """

    @swagger_auto_schema(responses={'200': payment_info_response})
    def get(self, request, *args, **kwargs):
        param = request.GET.get('data')
        if not param:
            return Response({'data': 'data should be provided.'}, status=400)
        data = json.loads(base64.urlsafe_b64decode(param.encode()).decode())
        serializer = PaymentSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_data = serializer.data
        response_data.update({
            'link': f'http://payment-service:8081/api/payment/create/{serializer.data["id"]}',
            'instruction': 'To pay send POST request by link.'
        })
        return Response(response_data, status=200)


class PaymentCreateView(GenericAPIView):
    """Make payment. Send hook to callback_url."""
    queryset = Payment.objects.all()

    def post(self, request, *args, **kwargs):
        """Update payment. Send callback if callback_url was provided."""
        payment = self.get_object()
        payment.status = Payment.SUCCESS
        payment.save()
        if payment.callback_url:
            send_callback.delay(payment.id)
        return Response(status=200)
