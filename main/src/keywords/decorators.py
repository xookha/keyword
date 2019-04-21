from django.http import HttpResponse
from django.conf import settings


def KWServicePerm(APIView):
    """
    Decorator to check perms to views for KW Service.
    Regular users shouldn't have access to KW Service views.
    """

    class Wrapper(APIView):

        def dispatch(self, request, *args, **kwargs):
            """Extra hook for checking header."""
            kw_auth_header = request.META.get('HTTP_KW_SERVICE')

            if kw_auth_header and kw_auth_header == settings.KW_SERVICE_TOKEN:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse('Authorization Error', status=401)

    return Wrapper


def PayServicePerm(APIView):
    """
    Decorator to check perms to views for Payment Service.
    Regular users shouldn't have access to Payment Service views.
    """

    class Wrapper(APIView):

        def dispatch(self, request, *args, **kwargs):
            """Extra hook for checking header."""
            pay_auth_header = request.META.get('HTTP_PAY_SERVICE')
            if pay_auth_header and pay_auth_header == settings.PAYMENT_SERVICE_TOKEN:
                return super().dispatch(request, *args, **kwargs)
            else:
                return HttpResponse('Authorization Error', status=401)

    return Wrapper
