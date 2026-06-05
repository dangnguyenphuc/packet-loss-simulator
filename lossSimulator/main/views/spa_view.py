from django.http import HttpResponse, Http404
from django.views import View
from django.conf import settings


class SpaView(View):
    def get(self, request):
        index_path = settings.BASE_DIR / "static" / "vue" / "index.html"
        try:
            with open(index_path, "rb") as f:
                return HttpResponse(f.read(), content_type="text/html")
        except FileNotFoundError:
            raise Http404("Vue app not built. Run: make build-frontend")
