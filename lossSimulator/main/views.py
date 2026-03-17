from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import FileUtils, AdbUtils, AudioUtils
from utils.android import AndroidAppController
import json
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER, DEFAULT_AUDIO_DURATION, DEFAULT_AUDIO_DURATION_OFFSET
from django.conf import settings
import threading, uuid
from django.core.cache import cache
import time
from threading import Lock
from django.views import View
from django.utils.decorators import method_decorator


runningTasks = {}
tasksLock = Lock()

class JsonFileListView(View):
    def get(self, request):
        try:
            files = FileUtils.listAllJsonFiles()
            return JsonResponse({"files": files}, status=200)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)


class JsonFileDetailView(View):
    def get(self, request, filename):
        try:
            data = FileUtils.getJsonContent(filename)
            return JsonResponse({"data": data}, status=200)
        except FileNotFoundError:
            return JsonResponse({"error": "File not found"}, status=404)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

class DeviceListView(View):
    def get(self, request):
        devices = AdbUtils.getConnectedDevices()
        return JsonResponse({"data": devices}, status=200)


class DeviceIpView(View):
    def get(self, request, device_id):
        ips = AdbUtils.getDeviceIps(device_id)
        return JsonResponse({"data": ips}, status=200)

class InfoView(View):
    def get(self, request):
        device_id = request.GET.get("deviceId")

        app_path = AdbUtils.getAppPath()
        zrtc_demo_app = AdbUtils.getZrtcDemoApp()

        return JsonResponse({
            "pc": {
                "audio": AudioUtils.getAudioFileWithDurations(),
                "recordFolder": f"{settings.BASE_DIR}/{DESKTOP_STATIC_FOLDER}",
            },
            "android": {
                "uploadAudioFolder": app_path,
                "recordAudioFolder": app_path,
                "histogramStorePath": AdbUtils.getHistogramPath(device_id),
                "appPackage": (
                    zrtc_demo_app if AdbUtils.isContainZrtcDemoApp(device_id) else ""
                ),
                "activity": AdbUtils.getZrtcDemoAppTargetActivities(device_id),
            }
        }, status=200)

@method_decorator(csrf_exempt, name="dispatch")
class TaskRunView(View):
    def post(self, request):
        with tasksLock:
            runningTasks.clear()

        try:
            data = json.loads(request.body.decode("utf-8"))
            device_id = data.get("deviceId")

            if not device_id:
                raise ValueError("Missing deviceId")

        except Exception as e:
            return JsonResponse({
                "error": "Invalid JSON payload",
                "details": str(e)
            }, status=400)

        timeout = data.get("time", DEFAULT_EVAL_TIMEOUT)
        enable_opus_plc = data.get("enableOpusPlc", True)
        enable_opus_dred = data.get("enableOpusDred", False)
        complexity = data.get("complexity", 5)
        folder_name = data.get("folderName")

        task_id = str(uuid.uuid4())
        start_event = threading.Event()
        stop_event = threading.Event()

        thread = threading.Thread(
            target=runApp,
            args=(
                task_id, device_id,
                enable_opus_plc, enable_opus_dred,
                timeout, start_event, stop_event,
                complexity, folder_name
            )
        )

        with tasksLock:
            runningTasks[task_id] = {
                "thread": thread,
                "stopEvent": stop_event
            }

        thread.start()
        start_event.wait()

        return JsonResponse({
            "status": "started",
            "taskId": task_id
        }, status=202)

@method_decorator(csrf_exempt, name="dispatch")
class TaskDetailView(View):

    def get(self, request, task_id):
        return self._check_task(task_id)

    def delete(self, request, task_id):
        return self._stop_task(task_id)

    def _check_task(self, task_id):
        result = cache.get(task_id)

        if not result:
            return JsonResponse({"status": "failed"}, status=404)

        valid_audio_found = False

        for audio in result["audioFiles"]:
            try:
                if AudioUtils.isValidAudioFile(audio):
                    valid_audio_found = True
                    break
            except Exception:
                continue

        if valid_audio_found:
            result["audioFiles"] = [
                f.split("public")[-1] for f in result["audioFiles"]
            ]
            return JsonResponse({"status": "done", "result": result}, status=200)

        return JsonResponse({"status": "processing"}, status=202)

    def _stop_task(self, task_id):
        with tasksLock:
            task = runningTasks.get(task_id)
            runningTasks.clear()

        if not task:
            return JsonResponse(
                {"error": "Task not found or already finished"},
                status=404
            )

        task["stopEvent"].set()

        return JsonResponse({
            "status": "stopping",
            "taskId": task_id
        }, status=200)


def runApp(taskId, deviceId, enableOpusPlc, enableOpusDred, timeout, startEvent, stopEvent, complexity=None, folderName=None):
    controller = AndroidAppController(deviceId=deviceId)
    controller.stopAll()
    try:
        controller.boolExtras["ENABLE_OPUS_PLC"] = enableOpusPlc
        controller.boolExtras["ENABLE_OPUS_DRED"] = enableOpusDred
        controller.stringExtras["OPUS_COMPLEXITY"] = complexity
        controller.startEval(startEvent)

        startTime = time.time()
        while time.time() - startTime < timeout:
            if stopEvent.is_set():
                controller.stopApp()
                return
            time.sleep(1)
        
        controller.press("back")
        controller.press("back")
        controller.stopApp()

        staticFolder = FileUtils.getAbsPath(str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER)
        specificFolder = staticFolder + "/" + f"com{complexity}_{"plc_" if enableOpusPlc else "normal_"}{folderName + "_" if folderName is not None else ""}{controller.timestamp}"
        # pull audio files
        FileUtils.makeDir(specificFolder)
        AdbUtils.pullFiles(controller.storePath, specificFolder, deviceId)
        AdbUtils.pullFiles(
            AdbUtils.getHistogramPath(),
            specificFolder,
            deviceId
        )

        try: 
            FileUtils.moveFiles(specificFolder + "/" + "_".join(specificFolder.split("_")[-2:]), specificFolder)
        finally:
            audioFiles = FileUtils.getAudioFiles(specificFolder)
            logFiles = FileUtils.getLogFiles(specificFolder)

            result = {
                "audioFiles": audioFiles,
                "zrtcLog": logFiles,
            }
            cache.set(taskId, result, timeout=71)
            print("Set task id ", taskId)
    except Exception as e:
        cache.set(taskId, None, timeout=71)
        print(f"[runApp] Exception: {e}")
        startEvent.set()
        controller.stopAll()
        with tasksLock:
            runningTasks.pop(taskId, None)

@method_decorator(csrf_exempt, name="dispatch")
class FileView(View):
    def delete(self, request, folder_name):
        FileUtils.removeStoringFolder(folder_name)
        return JsonResponse({"status": "deleted"}, status=200)
    
class StatView(View):
    def get(self, request):
        stat_type = request.GET.get("type")
        device_id = request.GET.get("id")

        if stat_type == "start":
            FileUtils.removeStatFile("cpu")
            FileUtils.removeStatFile("mem")
            return JsonResponse({"status": "started"})

        elif stat_type == "cpu":
            cpu = AdbUtils.getCpuUsage(device_id)
            FileUtils.writeStat("cpu", cpu)
            return JsonResponse({"data": cpu})

        elif stat_type == "mem":
            mem = AdbUtils.getMemUsage(device_id) / 1000.0
            FileUtils.writeStat("mem", mem)
            return JsonResponse({"data": mem})

        elif stat_type == "stop":
            AdbUtils.resetAndroid(deviceId=device_id)
            return JsonResponse({"status": "stopped"})

        return JsonResponse({"error": "Invalid type"}, status=400)
    
def installZrtcDemo(request):
    return HttpResponse("HelloWorld")