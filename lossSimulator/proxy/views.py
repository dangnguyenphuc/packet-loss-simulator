from django.views.decorators.csrf import csrf_exempt
from utils.utils import AtcClient


@csrf_exempt
def proxy_handler(request):
    return AtcClient.handle_request(request)
