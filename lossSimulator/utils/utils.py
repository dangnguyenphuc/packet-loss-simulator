from django.http import HttpResponse, HttpRequest, JsonResponse
import ipaddress
import os
import json
from json.decoder import JSONDecodeError
import requests
from .constants import *
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
import wave
from django.conf import settings 
import time

class DateTimeUtils:
    @staticmethod
    def getTimestamped():
        tz = timezone(timedelta(hours=7))
        return datetime.now(tz).strftime("%d-%m-%Y_%H%M%S")
class AudioUtils:
    def getAudioDuration(filePath: str) -> float:
        with wave.open(filePath, "rb") as wavFile:
            frames = wavFile.getnframes()
            rate = wavFile.getframerate()
            duration = frames / float(rate)
        return round(duration, 2)

    @staticmethod
    def getAudioFileWithDurations() -> list[str]:
        audioFiles = FileUtils.getAudioFiles();
        return [ f"{file}-{AudioUtils.getAudioDuration(file)}" for file in audioFiles]
class NetworkUtils:
    def getIp(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def checkValidIPv4(ip: str, subnet: str = NETWORK_ATC_SUBMASK_NET) -> bool:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)

    @staticmethod
    def getIpString(request: HttpRequest) -> str:
        ip = NetworkUtils.getIp(request)
        return (ip if NetworkUtils.checkValidIPv4(ip) else "Stranger")
    
    # @staticmethod
    # def scanNetwork(subnet=NETWORK_ATC_SUBMASK_NET):
    #     nm = nmap.PortScanner()
    #     nm.scan(hosts=subnet, arguments="-sn -n -T4 --host-timeout 1s")
    #     return [host for host in nm.all_hosts() if nm[host].state() == "up"]

class FileUtils:

    def moveFiles(src, dest):
        for filename in os.listdir(src):
            src_path = os.path.join(src, filename)
            dst_path = os.path.join(dest, filename)
            try:
                shutil.move(src_path, dst_path)
            except Exception:
                # ignore any errors (e.g. if file disappears)
                pass
    
    def openJsonFile(filePath: str) -> str:
        try:
            with open(filePath) as f:
                data = json.load(f)
                return data
        except json.JSONDecodeError as e:
            print("Invalid JSON format:", e)
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print("Unexpected error:", e)

        return ""

    @staticmethod
    def getAbsPath(filePath: str) -> str:
        return os.path.abspath(filePath)
    
    @staticmethod
    def makeDir(folderPath: str):
        return os.makedirs(folderPath, exist_ok=True)

    @staticmethod
    def saveJsonFile(data, filePath: str, folderPath: str = JSON_CONFIG_FOLDER) -> bool:
        try:
            with open(os.path.join(folderPath, filePath), "w") as f:
                json.dump(data, f, indent=4)
                return True
        except json.JSONDecodeError as e:
            print("Invalid JSON format:", e)
        except FileNotFoundError:
            print("File not found")
        except Exception as e:
            print("Unexpected error:", e)

        return False
    
    def listFile(folderPath, type="*"):
        if type == "*":
            return [os.path.abspath(os.path.join(folderPath, f)) for f in os.listdir(folderPath)]
        else:
            return [
                os.path.abspath(os.path.join(folderPath, f))
                for f in os.listdir(folderPath)
                if f.endswith(type)
            ]
    
    @staticmethod
    def copyFile(src: str, dst: str) -> bool:
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Failed to copy {src} -> {dst}: {e}")
            return False

    @staticmethod
    def listAllJsonFiles(folderPath: str = JSON_CONFIG_FOLDER) -> list[str]:
        res = FileUtils.listFile(folderPath, type="json")
        res.sort()
        return res

    @staticmethod
    def getJsonContent(filename: str, folderPath: str = JSON_CONFIG_FOLDER) -> str:
        return FileUtils.openJsonFile(os.path.join(folderPath, filename))
    
    @staticmethod
    def getAtcInfo() -> dict:
        return {
            "ip": NETWORK_ATC_GATEWAY_IP,
            "endpoint": NETWORK_ATC_ENDPOINT
        }
    
    @staticmethod
    def getAudioFiles(audioPath=STATIC_FOLDER) -> list[str]:
        paths = FileUtils.listFile(audioPath, AUDIO_TYPE)
        return [os.path.abspath(path) for path in paths]
    
    @staticmethod
    def getLogFiles(logPath=STATIC_FOLDER) -> list[str]:
        paths = FileUtils.listFile(logPath, LOG_TYPE)
        return [os.path.abspath(path) for path in paths]
        
    
class RequestUtils:
    @staticmethod
    def atcRequest(request: HttpRequest) -> JsonResponse:

        if request.method == "GET":
            ip = request.GET.get("ip", "")
            data = []
            if ip == "":
                for ipLoop in NetworkUtils.scanNetwork():
                    tmp = {}
                    endpoint = NETWORK_ATC_GATEWAY_IP + NETWORK_ATC_ENDPOINT + ipLoop + "/"
                    try:
                        response = requests.get(endpoint)
                        tmp = {
                            "ip": ipLoop, 
                            "active": (response.status_code//200 == 1)
                        }
                    except:
                        tmp = {
                            "ip": ipLoop, 
                            "active": False
                        }
                    data.append(tmp)
            else:
                endpoint = NETWORK_ATC_GATEWAY_IP + NETWORK_ATC_ENDPOINT + ip + "/"
                try:
                    response = requests.get(endpoint)
                    if response.status_code//200 == 1:
                        data.append(ipLoop)
                except:
                    pass
            return JsonResponse({"data": data})        

        try :
            requestData = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as e:
            return JsonResponse(
                {
                    "error": "Invalid JSON payload", 
                    "details": str(e)
                },
                status=400
            )

        if 'ip' not in requestData:
            return JsonResponse(
                {
                    "error": "Invalid request format. Missing 'ip' field"
                },
                status=400
            )

        endpoint = NETWORK_ATC_GATEWAY_IP + NETWORK_ATC_ENDPOINT + requestData['ip'] + "/"

        if request.method == 'POST':
            if 'data' not in requestData:
                return JsonResponse(
                    {
                        "error": "Invalid request format. Missing 'data' field"
                    },
                    status=400
                )
            
            headers = {
                "Content-Type": "application/json"
            }

            try:
                statusCode = 1
                retryTime = NETWORK_ATC_MAX_RETRY
                while statusCode//200 != 1 and retryTime > 0:
                    response = requests.post(
                        endpoint,
                        headers=headers,
                        json=requestData['data']
                    ) 
                    statusCode = response.status_code
                    retryTime -= 1 
                return JsonResponse(
                    {
                        "status": response.status_code,
                        "data": ""
                    },
                    status=response.status_code
                )
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)

        elif request.method == 'DELETE':
            try:
                response = requests.delete(
                    endpoint
                )    
                return JsonResponse(
                    {
                        "status": response.status_code,
                        "data": ""
                    },
                    status=response.status_code
                )
            except Exception as e:
                return JsonResponse({"error": str(e)}, status=500)
        else:
            return JsonResponse(
                {"error": "You do not have permission to access this resource."},
                status=403
            ) 
        
class AdbUtils:

    @staticmethod
    def getDeviceIps(deviceId=None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["shell", "ip -f inet addr show"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise Exception(f"adb error: {result.stderr}")

        interfaces = []
        current_iface = None
        for line in result.stdout.splitlines():
            line = line.strip()
            if not line:
                continue
            # Detect new interface
            if line[0].isdigit() and ":" in line:
                # Example: "3: wlan0: <BROADCAST,MULTICAST,UP,LOWER_UP> mtu 1500 ..."
                parts = line.split(":")
                if len(parts) >= 2:
                    current_iface = parts[1].strip().split()[0]
            elif line.startswith("inet ") and current_iface:
                # Example: "inet 192.168.1.42/24 brd 192.168.1.255 scope global wlan0"
                ip = line.split()[1].split("/")[0]
                interfaces.append({"interface": current_iface, "ip": ip})

        return interfaces

    @staticmethod
    def startActivityWithExtras(packageName, activityName, deviceId=None, stringExtras=None, intExtras=None, boolExtras=None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["shell", "am", "start"]

        if stringExtras:
            for key, val in stringExtras.items():
                cmd += ["--es", key, str(val)]

        if intExtras:
            for key, val in intExtras.items():
                cmd += ["--ei", key, str(val)]

        if boolExtras:
            for key, val in boolExtras.items():
                cmd += ["--ez", key, "true" if val else "false"]

        cmd.append(f"{packageName}/{activityName}")
        try:
            subprocess.run(cmd, check=True)
        except Exception as e:
            raise e

    def pullFiles(src, des, deviceId=None, retries=DEFAULT_RETRY):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["pull", src, des]

        attempt = 0
        while attempt < retries:
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                return
            except subprocess.CalledProcessError as e:
                attempt += 1
                if attempt > retries:
                    raise
                time.sleep(1)

    @staticmethod
    def pushFile(src, dest, deviceId=None, retries=DEFAULT_RETRY):

        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["push", src, dest]

        attempt = 0
        while attempt < retries:
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                return
            except subprocess.CalledProcessError as e:
                attempt += 1
                if attempt > retries:
                    raise
                time.sleep(1)
    
    @staticmethod
    def isFileExists(path, deviceId = None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["shell", f"test -f {path} && echo 1 || echo 0"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == "1"

    @staticmethod
    def isFolderExists(path, deviceId = None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["shell", f"test -d {path} && echo 1 || echo 0"]

        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == "1"

    @staticmethod
    def getDownloadsPath(deviceId = None):
        return AdbUtils.getDefaultPath(deviceId) + "/" + ANDROID_DOWNLOAD_PATH
    
    @staticmethod
    def getDocumentPath(deviceId = None):
        return AdbUtils.getDefaultPath(deviceId) + "/" + ANDROID_DOCUMENTS_PATH

    @staticmethod
    def getAppPath(deviceId = None):
        return AdbUtils.getDownloadsPath(deviceId) + "/" + ANDROID_DEMO_PATH

    @staticmethod
    def getHistogramPath(deviceId = None):
        return AdbUtils.getDocumentPath(deviceId) + "/" + ANDROID_HISTOGRAM_PATH


    @staticmethod
    def getDefaultPath(deviceId = None):
        candidates = [
            "/storage/emulated/0",
            "/sdcard",
            "/mnt/sdcard"
        ]
        for path in candidates:
            cmd = ["adb"]
            if deviceId:
                cmd += ["-s", deviceId]
            cmd += ["shell", "ls", path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "No such file" not in result.stdout and "not found" not in result.stdout:
                return path
        return None

    @staticmethod
    def createTmpDir(path, deviceId = None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["shell", "mkdir", "-p", path]

        subprocess.run(cmd, check=True)
        print(f"Created dir: {path} on device {deviceId or ''}")

    @staticmethod
    def getConnectedDevices():
        try:
            cmd = subprocess.run(
                ["adb", "devices"],
                capture_output=True,
                text=True,
                check=True
            )
            lines = cmd.stdout.strip().split("\n")[1:]  # skip "List of devices attached"
            return [line.split()[0] for line in lines if line.strip() and "device" in line]
        except subprocess.CalledProcessError as e:
            print("Error running adb:", e)
            return []

    @staticmethod
    def isContainPackage(packageName: str , deviceId: str=None) -> bool:
        try:
            cmd = ["adb"]
            if deviceId:
                cmd += ["-s", deviceId]
            cmd += ["shell", "pm", "list", "packages", "|", "grep", packageName]

            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
            return packageName in result.stdout
        except Exception as e:
            return False
        
    @staticmethod
    def isContainZrtcDemoApp(deviceId: str = None) -> bool:
        return AdbUtils.isContainPackage(APP_PACKAGE)
    
    @staticmethod
    def getZrtcDemoApp() -> str:
        return APP_PACKAGE
    
    @staticmethod
    def hasActivity(packageName, activityName, deviceId=None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += [
            "shell",
            f"dumpsys package {packageName} | grep {activityName}"
        ]

        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
        return result.returncode == 0 and activityName in result.stdout

    @staticmethod
    def getZrtcDemoAppTargetActivities(deviceId=None) -> list[str]:
        targetActivities = [LOGIN_ACTIVITY, MAIN_ACTIVITY]
        zrtcDemoApp = AdbUtils.getZrtcDemoApp()
        
        return [act for act in targetActivities if AdbUtils.hasActivity(zrtcDemoApp, act, deviceId)]