from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils, AdbUtils, AudioUtils
from utils.android import AndroidAppController
import json
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER
from django.conf import settings
import threading, uuid
from django.core.cache import cache

def listJsonFiles(request):
    if request.method == "GET":
        return JsonResponse({"files": FileUtils.listAllJsonFiles()})
    else:
        return HttpResponseNotFound("Not found")

def getJson(request, filename):
    if request.method == "GET":
        return JsonResponse({"data": FileUtils.getJsonContent(filename)})
    else:
        return HttpResponseNotFound("Not found")

def getAllDevices(request):
    allDevices = AdbUtils.getConnectedDevices()
    print(allDevices)
    return JsonResponse({"data": allDevices})

def getDeviceIps(request, deviceId):
    ips = AdbUtils.getDeviceIps(deviceId)
    return JsonResponse({"data": ips})

def getInfo(request):
        deviceId = request.GET.get("deviceId", None)
        appPath = AdbUtils.getAppPath()
        zrtcDemoApp = AdbUtils.getZrtcDemoApp()

        return JsonResponse(
        {
            "pc":  
            {
                "audio": AudioUtils.getAudioFileWithDurations(),
                "recordFolder": str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER
            },
            "android":
            {
                "uploadAudioFolder": appPath,
                "recordAudioFolder": appPath,
                "histogramStorePath": AdbUtils.getHistogramPath(deviceId),
                "appPackage": (zrtcDemoApp if AdbUtils.isContainZrtcDemoApp(deviceId) else ""),
                "activity": AdbUtils.getZrtcDemoAppTargetActivities(deviceId)
            }
        })

def checkTask(request, taskId):
    result = cache.get(taskId)
    if result:
        return JsonResponse({"status": "done", "result": result})
    return JsonResponse({"status": "failed"}) 

@csrf_exempt
def runZrtcAndroidApp(request):
    try :
        requestData = json.loads(request.body.decode("utf-8"))
        if ("deviceId" not in requestData or requestData["deviceId"] == ""):
            raise Exception("Missing deviceId field")
    except Exception as e:
        return JsonResponse(
            {
                "error": "Invalid JSON payload", 
                "details": str(e)
            },
            status=400
        )
    deviceId = requestData["deviceId"]
    if ("time" in requestData):
        timeout = requestData["time"]
    else:
        timeout = DEFAULT_EVAL_TIMEOUT
    taskId = str(uuid.uuid4())
    startedEvent = threading.Event()

    thread = threading.Thread(target=runApp, args=(taskId, deviceId, timeout, startedEvent))
    thread.start()
    startedEvent.wait()
    return JsonResponse({"status": "started", "taskId": taskId})

def runApp(taskId, deviceId, timeout, startedEvent):
    controller = AndroidAppController(deviceId=deviceId)
    controller.stopAll()
    controller.sleep(2)
    try:
        controller.startEval(startedEvent, timeout=timeout)
        staticFolder = str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER + controller.timestamp
        
        audioFiles = FileUtils.getAudioFiles(staticFolder)
        logFiles = FileUtils.getLogFiles(staticFolder)

        audioFiles = [file.split("public")[-1] for file in audioFiles]
        result = {
            "audioFiles": audioFiles,
            "zrtcLog": logFiles
        }
        cache.set(taskId, result, timeout=10)
    except Exception as e:
        print(e)
        startedEvent.set()
        controller.stopApp()