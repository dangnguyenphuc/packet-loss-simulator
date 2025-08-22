from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils

def index(request):

    context = {
        "name": NetworkUtils.getIpString(request),
        "files": FileUtils.listAllJsonFiles(),
    }
    
    return render(request, "main/index.html", context)

def listJsonFiles(request):
    return JsonResponse({"files": FileUtils.listAllJsonFiles()})

def getJson(request, filename):
    return JsonResponse({"data": FileUtils.getJsonContent(filename)})

def getAllDevices(request):
    currentIp = NetworkUtils.getIpString(request)
    allDevices = NetworkUtils.scanNetwork()
    allDevices.remove(currentIp)
    return JsonResponse({"data": allDevices})