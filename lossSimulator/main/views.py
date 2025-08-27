from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils, ADBUtils

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
    currentIp = NetworkUtils.getIpString(request)
    allDevices = NetworkUtils.scanNetwork()
    allDevices.remove(currentIp)
    return JsonResponse({"data": allDevices})

def getDeviceNumbers(request):
    if request.method == "GET":
        return JsonResponse({"data": ADBUtils.getConnectedDevices()})
    else:
        return HttpResponseNotFound("Not found")