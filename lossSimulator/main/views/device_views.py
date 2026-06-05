from django.http import JsonResponse
from django.conf import settings
from django.views import View

from utils.utils import FileUtils, AdbUtils, AudioUtils
from utils.constants import DESKTOP_STATIC_FOLDER


class UsernameView(View):
    def get(self, request):
        return JsonResponse({"username": FileUtils.get_username()}, status=200)


class JsonFileListView(View):
    def get(self, request):
        try:
            files = FileUtils.list_all_json_files()
            return JsonResponse({"files": files}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class JsonFileDetailView(View):
    def get(self, request, filename):
        try:
            data = FileUtils.get_json_content(filename)
            return JsonResponse({"data": data}, status=200)
        except FileNotFoundError:
            return JsonResponse({"error": "File not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class DeviceListView(View):
    def get(self, request):
        devices = AdbUtils.get_connected_devices()
        return JsonResponse({"data": devices}, status=200)


class DeviceIpView(View):
    def get(self, request, device_id):
        ips = AdbUtils.get_device_ips(device_id)
        return JsonResponse({"data": ips}, status=200)


class InfoView(View):
    def get(self, request):
        device_id = request.GET.get("deviceId")
        zrtc_demo_app = AdbUtils.get_zrtc_demo_app()

        return JsonResponse({
            "pc": {
                "audio": AudioUtils.get_audio_file_with_durations(),
                "recordFolder": f"{settings.BASE_DIR}/{DESKTOP_STATIC_FOLDER}",
            },
            "android": {
                "uploadAudioFolder": AdbUtils.get_app_path(),
                "recordAudioFolder": AdbUtils.get_app_path(),
                "histogramStorePath": AdbUtils.get_histogram_path(device_id),
                "appPackage": zrtc_demo_app if AdbUtils.is_contain_zrtc_demo_app(device_id) else "",
                "activity": AdbUtils.get_zrtc_demo_app_target_activities(device_id),
            },
        }, status=200)
