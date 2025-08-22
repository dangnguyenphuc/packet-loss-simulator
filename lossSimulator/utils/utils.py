from django.http import HttpResponse, HttpRequest, JsonResponse
import ipaddress
import os
import json
from json.decoder import JSONDecodeError
import requests
from .constants import CONST
import nmap

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

    def listFile(folderPath: str, type: str = "*") -> list[str]:
        if (type == "*"):
            return os.listdir(folderPath)

        else: return [file for file in os.listdir(folderPath) if file.endswith(type)]
    
    @staticmethod
    def listAllJsonFiles(folderPath: str = CONST.JSON_CONFIG_FOLDER) -> list[str]:
        res = FileUtils.listFile(folderPath, type="json")
        res.sort()
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

        endpoint = CONST.NETWORK_ATC_GATEWAY_IP + CONST.NETWORK_ATC_ENDPOINT + NetworkUtils.getIpString(request) + "/"
        
        if request.method == 'POST':
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
            headers = {
                "Content-Type": "application/json"
            }
            
            try:
                response = requests.post(
                    endpoint,
                    headers=headers,
                    json=requestData
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