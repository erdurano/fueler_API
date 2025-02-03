from django.views import View
from django.conf import settings
from django.http import Http404, HttpResponse
import pathlib

# Create your views here.


class MapView(View):
    def get(self, request, map_id):
        map_path = pathlib.Path(settings.MAPS_DIRECTORY) / f"{map_id}.html"

        if not map_path.exists():
            raise Http404("Map not found")

        with open(map_path, "r") as map_file:
            html_content = map_file.read()

        return HttpResponse(html_content, content_type="text/html")
