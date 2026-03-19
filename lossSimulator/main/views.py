from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.conf import settings
from django.views import View
from django.utils.decorators import method_decorator

from utils.utils import FileUtils, AdbUtils, AudioUtils
from utils.android import AndroidAppController
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER, DEFAULT_AUDIO_DURATION, DEFAULT_AUDIO_DURATION_OFFSET

from multiprocessing import Process, Event, Lock, Manager
import json
import uuid
import time
import signal
import os

manager = Manager()
myCache = manager.dict()
tasks = manager.dict()

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

    MISSING_DEVICE_ID = JsonResponse({
                "error": "Invalid device id",
                "details": "device id is empty"
    }, status=400)

    INVALID_TYPE_PAYLOAD = JsonResponse({
                "error": "Invalid task type",
                "details":  "Type: run | install"
            }, status=400)

    INVALID_JSON_PAYLOAD = lambda e: JsonResponse({
                "error": "Invalid JSON payload",
                "details": str(e)
            }, status=400)
    
    APP_IS_IN_TASK = JsonResponse({
                "error": "Cannot run app",
                "details": "App is being built or running on PC"
            }, status=400)

    def validate(self, device_id) -> bool:
        return device_id and len(device_id) > 0 and AdbUtils.isDeviceExists(device_id)

    def post(self, request, device_id, type):

        if not self.validate(device_id):
            return self.MISSING_DEVICE_ID
        

        match type:
            case "install": 
                return self.install(device_id)
            case "run":
                return self.run(request, device_id)
            case _: return self.INVALID_TYPE_PAYLOAD
    

    def install(self, device_id):
        
        task_id = str(uuid.uuid4())

        p = Process(
            target=buildApp,
            args=(
                device_id,
                task_id
            )
        )

        tasks[task_id] = {
            "thread": p.pid,
            "type": "install",
            "id": device_id
        }
        
        p.start()

        return JsonResponse({
            "status": "started",
            "taskId": task_id
        }, status=202)
    

    def run(self, request, device_id):

        try:
            data = json.loads(request.body.decode("utf-8"))

        except Exception as e:
            return self.INVALID_JSON_PAYLOAD(e)

        timeout = data.get("time", DEFAULT_EVAL_TIMEOUT)
        enable_opus_plc = data.get("enableOpusPlc", True)
        enable_opus_dred = data.get("enableOpusDred", False)
        complexity = data.get("complexity", 5)
        folder_name = data.get("folderName")

        task_id = str(uuid.uuid4())
        start_event = Event()

        thread = Process(
            target=runApp,
            args=(
                task_id, device_id,
                enable_opus_plc, enable_opus_dred,
                timeout, start_event,
                complexity, folder_name
            )
        )

        thread.start()
        start_event.wait()

        tasks[task_id] ={
            "thread": thread.pid,
            "type": "run",
            "id": device_id
        }

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
        result = myCache.get(task_id)
        cur = time.time()
        for key in list(myCache.keys()):
            if cur - myCache[key]["time"] >= 71:
                myCache.pop(key, None)

        if not result:
            return JsonResponse({"status": "failed"}, status=404)

        valid_audio_found = False

        for audio in result["audioFiles"]:
            print("Check audio", audio)
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
        task = tasks.get(task_id)
        if not task:
            return JsonResponse(
                {"error": "Task not found or already finished"},
                status=404
            )

        pid = task["thread"]
        type = task["type"]
        device_id = task["id"]

        try:
            # 1. Send the termination signal
            os.kill(pid, signal.SIGTERM)
            
            # 2. Reconstruct a process object handle using the PID 
            # to properly 'wait' on it and clean up the zombie.
            # Note: In Python multiprocessing, we usually use the original 
            # 'p' object, but since we only have the PID, we use os.waitpid.
            
            # os.WNOHANG means "don't block the Django thread if it's not dead yet"
            time.sleep(0.1) # Give it a tiny moment to die
            os.waitpid(pid, os.WNOHANG) 

        except ProcessLookupError:
            # Process was already dead, no zombie to worry about
            pass 
        except Exception as e:
            print(f"Cleanup error: {e}")

        match type:
            case "run":
                AdbUtils.resetAndroid(device_id)

        tasks.pop(task_id, None)

        return JsonResponse({
            "status": "stopping",
            "taskId": task_id
        }, status=200)

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
    
def buildApp(deviceId, task_id):
    result = AdbUtils.installAndBuildZrtcDemo(deviceId)

    result = {
        "info": True if result else False,
        "time": time.time()
    }
    
    tasks.pop(task_id, None)
    myCache[task_id] = result


def runApp(taskId, deviceId, enableOpusPlc, enableOpusDred, timeout, startEvent, complexity=None, folderName=None):
    controller = AndroidAppController(deviceId=deviceId)
    controller.stopAll()
    try:
        controller.boolExtras["ENABLE_OPUS_PLC"] = enableOpusPlc
        controller.boolExtras["ENABLE_OPUS_DRED"] = enableOpusDred
        controller.stringExtras["OPUS_COMPLEXITY"] = complexity
        controller.startEval(startEvent)
        time.sleep(timeout)
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
                "time": time.time(),
                "audioFiles": audioFiles,
                "zrtcLog": logFiles
            }
        myCache[taskId] = result
    except Exception as e:
        print(f"[runApp] Exception: {e}")
        startEvent.set()
        controller.stopAll()
    
    tasks.pop(taskId, None)