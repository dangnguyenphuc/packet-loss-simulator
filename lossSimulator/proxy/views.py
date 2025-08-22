from django.views.decorators.csrf import csrf_exempt
from utils.utils import RequestUtils

# Create your views here.
@csrf_exempt
def proxyHandler(request):
    return RequestUtils.atcRequest(request)