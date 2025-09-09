from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils, AdbUtils, AudioUtils

def index(request):

    context = {
        "name": NetworkUtils.getIpString(request),
        "files": FileUtils.listAllJsonFiles(),
        "strategies": FileUtils.listAllLossStrategyFiles()
    }
    
    return render(request, "main/index.html", context)

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