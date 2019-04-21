from drf_yasg import openapi

payment_info_response = openapi.Schema(
    type=openapi.TYPE_OBJECT,
    properties={
        'amount': openapi.Schema(type=openapi.TYPE_STRING),
        'info': openapi.Schema(type=openapi.TYPE_STRING, ),
        'pay_id': openapi.Schema(type=openapi.TYPE_STRING),
        'callback_url': openapi.Schema(type=openapi.TYPE_STRING),
    }
)
