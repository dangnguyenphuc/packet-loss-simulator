from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from utils.utils import AdbUtils, FileUtils
from utils.constants import STATIC_FOLDER


@method_decorator(csrf_exempt, name="dispatch")
class FileView(View):
    def delete(self, request, folder_name):
        FileUtils.remove_storing_folder(folder_name)
        return JsonResponse({"status": "deleted"}, status=200)


class StatView(View):
    def get(self, request):
        stat_type = request.GET.get("type")
        device_id = request.GET.get("id")

        match stat_type:
            case "start":
                FileUtils.remove_stat_file("cpu", STATIC_FOLDER)
                FileUtils.remove_stat_file("mem", STATIC_FOLDER)
                return JsonResponse({"status": "started"})

            case "cpu":
                cpu = AdbUtils.get_cpu_usage(device_id)
                FileUtils.write_stat(STATIC_FOLDER, "cpu", cpu)
                return JsonResponse({"data": cpu})

            case "mem":
                mem = AdbUtils.get_mem_usage(device_id) / 1000.0
                FileUtils.write_stat(STATIC_FOLDER, "mem", mem)
                return JsonResponse({"data": mem})

            case "stop":
                AdbUtils.reset_android(device_id=device_id)
                return JsonResponse({"status": "stopped"})

            case _:
                return JsonResponse({"error": "Invalid type"}, status=400)
