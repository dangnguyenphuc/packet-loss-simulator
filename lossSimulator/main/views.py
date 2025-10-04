from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse, JsonResponse
from django.http import HttpResponseNotFound
from utils.utils import NetworkUtils, FileUtils, AdbUtils, AudioUtils
from utils.android import AndroidAppController
import json
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER, DEFAULT_AUDIO_DURATION, DEFAULT_AUDIO_DURATION_OFFSET
from django.conf import settings
import threading, uuid
from django.core.cache import cache
import time
from threading import Lock

runningTasks = {}
tasksLock = Lock()

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

@csrf_exempt
def runZrtcAndroidApp(request):
    with tasksLock:
        runningTasks.clear()
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
    enableOpusPlc = requestData.get("enableOpusPlc", True)
    complexity = requestData.get("complexity", 5)
    folderName = requestData.get("folderName", None)
    taskId = str(uuid.uuid4())
    startEvent = threading.Event()
    stopEvent = threading.Event()

    thread = threading.Thread(target=runApp, args=(taskId, deviceId, enableOpusPlc, timeout, startEvent, stopEvent, complexity, folderName))

    with tasksLock:
        runningTasks[taskId] = {
            "thread": thread,
            "stopEvent": stopEvent
        }

    thread.start()
    startEvent.wait()
    return JsonResponse({"status": "started", "taskId": taskId})

@csrf_exempt
def runTaskHandler(request, taskId):
    if request.method == "GET":
        return checkTask(taskId)
    elif request.method == "DELETE":
        return stopZrtcAndroidApp(taskId)
    else:
        return HttpResponseNotFound("Not found")

def checkTask(taskId):
    result = cache.get(taskId)
    if result:
        # cache.delete(taskId)
        flag = False
        for audio in result["audioFiles"]:
            try: 
                if AudioUtils.isValidAudioFile(audio):
                    print(f"{audio} is valid")
                    flag = True
                    break
                else :
                    print(f"Passed Audio {audio} with {AudioUtils.getAudioDuration(audio)}")
            except:
                print(f"Cannot open {audio}")
        
        if flag:
            result["audioFiles"] = [file.split("public")[-1] for file in result["audioFiles"]]
            return JsonResponse({"status": "done", "result": result})
    return JsonResponse({"status": "failed"}) 

@csrf_exempt
def stopZrtcAndroidApp(taskId):
    with tasksLock:
        task = runningTasks.get(taskId)
        runningTasks.clear()

    if not task:
        return JsonResponse({"error": "Task not found or already finished"}, status=404)

    # signal the thread to stop
    task["stopEvent"].set()

    return JsonResponse({"status": "stopping", "taskId": taskId})


def runApp(taskId, deviceId, enableOpusPlc, timeout, startEvent, stopEvent, complexity=None, folderName=None):
    controller = AndroidAppController(deviceId=deviceId)
    controller.stopAll()
    try:
        controller.boolExtras["ENABLE_OPUS_PLC"] = enableOpusPlc
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

@csrf_exempt
def fileHanldler(request, folderName):
    if request.method == "DELETE":
        # remove storing folder 
        FileUtils.removeStoringFolder(folderName)
        return JsonResponse({"data": "done"})
    else:
        return HttpResponseNotFound("Not found")