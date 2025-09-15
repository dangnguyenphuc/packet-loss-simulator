from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils, AdbUtils, AudioUtils
from utils.android import AndroidAppController
import json
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER

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
                "recordFolder": FileUtils.getStaticFolder()
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
    controller = AndroidAppController(deviceId=deviceId)
    controller.stopAll()
    controller.sleep(2)
    try:
        controller.startEval(timeout=timeout)

        staticFolder = DESKTOP_STATIC_FOLDER + controller.timestamp

        return JsonResponse({
            "audioFiles": FileUtils.getAudioFiles(staticFolder),
            "zrtcLog": FileUtils.getLogFiles(staticFolder)
        })
        
    except Exception as e:
        print(e)
        controller.stopApp()
        return JsonResponse({
            "error": e
        }, status=500)

    