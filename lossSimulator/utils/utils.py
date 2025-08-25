from django.http import HttpResponse, HttpRequest, JsonResponse
import ipaddress
import os
import json
from json.decoder import JSONDecodeError
import requests
from .constants import CONST
import nmap
import random
import shutil

class NetworkUtils:
    def getIp(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')

        return ip

    def checkValidIPv4(ip: str, subnet: str = CONST.NETWORK_ATC_SUBMASK_NET) -> bool:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)

    @staticmethod
    def getIpString(request: HttpRequest) -> str:
        ip = NetworkUtils.getIp(request)
        return (ip if NetworkUtils.checkValidIPv4(ip) else "Stranger")
    
    @staticmethod
    def scanNetwork(subnet=CONST.NETWORK_ATC_SUBMASK_NET):
        nm = nmap.PortScanner()
        nm.scan(hosts=subnet, arguments="-sn -n -T4 --host-timeout 1s")
        return [host for host in nm.all_hosts() if nm[host].state() == "up"]

class FileUtils:
    
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
    def saveJsonFile(data, filePath: str, folderPath: str = CONST.JSON_CONFIG_FOLDER) -> bool:
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
    
    def listFile(folderPath: str, type: str = "*") -> list[str]:
        if (type == "*"):
            return os.listdir(folderPath)

        else: return [file for file in os.listdir(folderPath) if file.endswith(type)]
    
    @staticmethod
    def copyFile(src: str, dst: str) -> bool:
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"Failed to copy {src} -> {dst}: {e}")
            return False

    @staticmethod
    def listAllJsonFiles(folderPath: str = CONST.JSON_CONFIG_FOLDER) -> list[str]:
        res = FileUtils.listFile(folderPath, type="json")
        res.sort()
        return res

    @staticmethod
    def listAllLossStrategyFiles(folderPath: str = CONST.LOSS_STRATEGIES_FOLDER) -> dict[str, int]:
        res = FileUtils.listFile(folderPath, type="json")
        return res

    @staticmethod
    def getJsonContent(filename: str, folderPath: str = CONST.JSON_CONFIG_FOLDER) -> str:
        return FileUtils.openJsonFile(os.path.join(folderPath, filename))
    
    @staticmethod
    def getAtcInfo() -> dict:
        return {
            "ip": CONST.NETWORK_ATC_GATEWAY_IP,
            "endpoint": CONST.NETWORK_ATC_ENDPOINT
        }
    
class RequestUtils:
    @staticmethod
    def atcRequest(request: HttpRequest) -> JsonResponse:

        if request.method == "GET":
            ip = request.GET.get("ip", "")
            data = []
            if ip == "":
                for ipLoop in NetworkUtils.scanNetwork():
                    tmp = {}
                    endpoint = CONST.NETWORK_ATC_GATEWAY_IP + CONST.NETWORK_ATC_ENDPOINT + ipLoop + "/"
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
                endpoint = CONST.NETWORK_ATC_GATEWAY_IP + CONST.NETWORK_ATC_ENDPOINT + ip + "/"
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

        endpoint = CONST.NETWORK_ATC_GATEWAY_IP + CONST.NETWORK_ATC_ENDPOINT + requestData['ip'] + "/"

        if request.method == 'POST':
            if 'strategy' in requestData:
                strate = requestData['strategy']
                if not strate in FileUtils.listAllLossStrategyFiles():
                    return JsonResponse(
                        {
                            "error": f"Invalid strategy '{strate}'"
                        },
                        status=400
                    )

                shapeData = FileUtils.getJsonContent(strate, CONST.LOSS_STRATEGIES_FOLDER)
                curLoss = shapeData["down"]["loss"]["percentage"]
                loss = random.randint(0,100)
                
                match strate.split(".")[0]:
                    case "fix90":
                        loss = 90
                    case "dynamic":
                        shapeData["down"]["loss"]["percentage"] = loss
                    case "increaseOnly":
                        if loss >= curLoss:
                            shapeData["down"]["loss"]["percentage"] = loss
                            FileUtils.saveJsonFile(shapeData, strate, CONST.LOSS_STRATEGIES_FOLDER)
                    case _:
                        return JsonResponse({
                            "error": f"Strategy '{strate}' is not implemented"
                        }, status=400)
                
                try:
                    response = requests.post(
                        endpoint,
                        headers={"Content-Type": "application/json"},
                        json=shapeData
                    )

                    if strate.startswith("increase"):
                        return JsonResponse(
                            {
                                "status": response.status_code,
                                "loss": loss if loss >= curLoss else curLoss
                            },
                            status=response.status_code
                        )

                    return JsonResponse(
                        {
                            "status": response.status_code,
                            "loss": loss
                        },
                        status=response.status_code
                    )
                except Exception as e:
                    return JsonResponse({"error": str(e)}, status=500)




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
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=requestData['data']
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

        elif request.method == 'DELETE':
            
            # reset increaseOnly no matter what
            FileUtils.copyFile(
                os.path.join(CONST.LOSS_STRATEGIES_FOLDER, "dynamic.json"),
                os.path.join(CONST.LOSS_STRATEGIES_FOLDER, "increaseOnly.json")
            )

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