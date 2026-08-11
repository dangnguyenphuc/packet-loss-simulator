from django.http import HttpRequest, JsonResponse
import ipaddress
import os
import json
from json.decoder import JSONDecodeError
import requests
from .constants import (
    NETWORK_ATC_GATEWAY_IP, NETWORK_ATC_ENDPOINT, NETWORK_ATC_SUBMASK_NET,
    NETWORK_ATC_MAX_RETRY, STATIC_FOLDER, JSON_CONFIG_FOLDER,
    AUDIO_TYPE, LOG_TYPE, DEFAULT_RETRY, DEFAULT_AUDIO_DURATION,
    DEFAULT_AUDIO_DURATION_OFFSET, APP_PACKAGE, PACKAGE_DOMAIN,
    ANDROID_ARCH,
)
import shutil
import subprocess
from datetime import datetime, timezone, timedelta
import wave
from django.conf import settings
import time
from .plc_mos import PLCMOSEstimator
import soundfile as sf
import re

plcmos = PLCMOSEstimator()


class DateTimeUtils:
    @staticmethod
    def get_timestamped() -> str:
        tz = timezone(timedelta(hours=7))
        return datetime.now(tz).strftime("%d-%m-%Y_%H%M%S")


class AudioUtils:
    @staticmethod
    def is_valid_audio_file(file_path: str, timeout: float = DEFAULT_AUDIO_DURATION) -> bool:
        try:
            data, sr = sf.read(file_path)
            plcmos.run(data, sr)
            return AudioUtils.get_audio_duration(file_path) >= timeout - DEFAULT_AUDIO_DURATION_OFFSET
        except Exception:
            return False

    @staticmethod
    def get_audio_duration(file_path: str) -> float:
        with sf.SoundFile(file_path) as f:
            duration = len(f) / float(f.samplerate)
        return round(duration, 2)

    @staticmethod
    def get_audio_file_with_durations() -> list[str]:
        audio_files = FileUtils.get_audio_files()
        return [f"{file}-{AudioUtils.get_audio_duration(file)}" for file in audio_files]


class NetworkUtils:
    @staticmethod
    def get_ip(request: HttpRequest) -> str:
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            return x_forwarded_for.split(",")[0]
        return request.META.get("REMOTE_ADDR", "")

    @staticmethod
    def check_valid_ipv4(ip: str, subnet: str = NETWORK_ATC_SUBMASK_NET) -> bool:
        return ipaddress.ip_address(ip) in ipaddress.ip_network(subnet)

    @staticmethod
    def get_ip_string(request: HttpRequest) -> str:
        ip = NetworkUtils.get_ip(request)
        return ip if NetworkUtils.check_valid_ipv4(ip) else "Stranger"


class AtcClient:
    """Thin HTTP client for the ATC daemon API."""

    @staticmethod
    def _build_endpoint(ip: str) -> str:
        return f"{NETWORK_ATC_GATEWAY_IP}{NETWORK_ATC_ENDPOINT}{ip}/"

    @staticmethod
    def get_shape(ip: str) -> JsonResponse:
        endpoint = AtcClient._build_endpoint(ip)
        try:
            response = requests.get(endpoint)
            data = [{"ip": ip, "active": response.status_code // 200 == 1}]
        except Exception:
            data = [{"ip": ip, "active": False}]
        return JsonResponse({"data": data})

    @staticmethod
    def post_shape(ip: str, shape_data: dict) -> JsonResponse:
        endpoint = AtcClient._build_endpoint(ip)
        status_code = 0
        retries_left = NETWORK_ATC_MAX_RETRY
        try:
            while status_code // 200 != 1 and retries_left > 0:
                response = requests.post(
                    endpoint,
                    headers={"Content-Type": "application/json"},
                    json=shape_data,
                )
                status_code = response.status_code
                retries_left -= 1
            return JsonResponse({"status": status_code, "data": ""}, status=status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @staticmethod
    def delete_shape(ip: str) -> JsonResponse:
        endpoint = AtcClient._build_endpoint(ip)
        try:
            response = requests.delete(endpoint)
            return JsonResponse({"status": response.status_code, "data": ""}, status=response.status_code)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

    @staticmethod
    def handle_request(request: HttpRequest) -> JsonResponse:
        """Route an incoming HTTP request to the appropriate ATC API call."""
        if request.method == "GET":
            ip = request.GET.get("ip", "")
            if not ip:
                return JsonResponse({"error": "Missing 'ip' query parameter"}, status=400)
            return AtcClient.get_shape(ip)

        try:
            body = json.loads(request.body.decode("utf-8"))
        except (UnicodeDecodeError, JSONDecodeError) as e:
            return JsonResponse({"error": "Invalid JSON payload", "details": str(e)}, status=400)

        ip = body.get("ip")
        if not ip:
            return JsonResponse({"error": "Missing 'ip' field"}, status=400)

        if request.method == "POST":
            shape_data = body.get("data")
            if shape_data is None:
                return JsonResponse({"error": "Missing 'data' field"}, status=400)
            return AtcClient.post_shape(ip, shape_data)

        if request.method == "DELETE":
            return AtcClient.delete_shape(ip)

        return JsonResponse({"error": "Method not allowed"}, status=405)


# Keep backward-compatible alias
class RequestUtils:
    @staticmethod
    def atcRequest(request: HttpRequest) -> JsonResponse:  # noqa: N802 (legacy name)
        return AtcClient.handle_request(request)


class FileUtils:
    @staticmethod
    def get_username() -> str:
        return os.getlogin()

    @staticmethod
    def write_stat(path: str, stat_type: str, num: float) -> None:
        path = path.rstrip("/")
        with open(f"{path}/{stat_type}.txt", "a") as f:
            f.write(f"{num}\n")

    @staticmethod
    def remove_folder(folder: str) -> None:
        shutil.rmtree(folder, ignore_errors=True)

    @staticmethod
    def remove_storing_folder(folder: str) -> None:
        from utils.constants import DESKTOP_STATIC_FOLDER
        base = FileUtils.get_abs_path(str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER)
        shutil.rmtree(os.path.join(base, folder), ignore_errors=True)

    @staticmethod
    def remove_stat_file(stat_type: str, path: str) -> None:
        file_path = os.path.join(path, f"{stat_type}.txt")
        if os.path.isfile(file_path):
            os.remove(file_path)

    @staticmethod
    def move_files(src: str, dest: str) -> None:
        for filename in os.listdir(src):
            try:
                shutil.move(os.path.join(src, filename), os.path.join(dest, filename))
            except Exception:
                pass

    @staticmethod
    def open_json_file(file_path: str):
        try:
            with open(file_path) as f:
                return json.load(f)
        except (json.JSONDecodeError, FileNotFoundError, Exception) as e:
            print(f"[FileUtils.open_json_file] {e}")
            return ""

    @staticmethod
    def get_abs_path(file_path: str) -> str:
        return os.path.abspath(file_path)

    @staticmethod
    def make_dir(folder_path: str) -> None:
        os.makedirs(folder_path, exist_ok=True)

    @staticmethod
    def save_json_file(data, file_path: str, folder_path: str = JSON_CONFIG_FOLDER) -> bool:
        try:
            with open(os.path.join(folder_path, file_path), "w") as f:
                json.dump(data, f, indent=4)
            return True
        except Exception as e:
            print(f"[FileUtils.save_json_file] {e}")
            return False

    @staticmethod
    def list_file(folder_path: str, file_type: str = "*") -> list[str]:
        if file_type == "*":
            return [os.path.abspath(os.path.join(folder_path, f)) for f in os.listdir(folder_path)]
        return [
            os.path.abspath(os.path.join(folder_path, f))
            for f in os.listdir(folder_path)
            if f.endswith(file_type)
        ]

    @staticmethod
    def copy_file(src: str, dst: str) -> bool:
        try:
            shutil.copy2(src, dst)
            return True
        except Exception as e:
            print(f"[FileUtils.copy_file] Failed to copy {src} -> {dst}: {e}")
            return False

    @staticmethod
    def list_all_json_files(folder_path: str = JSON_CONFIG_FOLDER) -> list[str]:
        res = FileUtils.list_file(folder_path, file_type="json")
        res.sort()
        return res

    @staticmethod
    def get_json_content(filename: str, folder_path: str = JSON_CONFIG_FOLDER):
        return FileUtils.open_json_file(os.path.join(folder_path, filename))

    @staticmethod
    def get_audio_files(audio_path: str = STATIC_FOLDER) -> list[str]:
        return [os.path.abspath(p) for p in FileUtils.list_file(audio_path, AUDIO_TYPE)]

    @staticmethod
    def get_log_files(log_path: str = STATIC_FOLDER) -> list[str]:
        return [os.path.abspath(p) for p in FileUtils.list_file(log_path, LOG_TYPE)]


class AdbUtils:
    @staticmethod
    def is_device_exists(device_id: str = "") -> bool:
        result = subprocess.run(["adb", "devices"], capture_output=True, text=True)
        devices = [
            line.split()[0]
            for line in result.stdout.strip().splitlines()[1:]
            if line.strip()
        ]
        return device_id in devices if device_id else len(devices) > 0

    @staticmethod
    def get_device_ips(device_id: str = None) -> list[dict]:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
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
            if line[0].isdigit() and ":" in line:
                parts = line.split(":")
                if len(parts) >= 2:
                    current_iface = parts[1].strip().split()[0]
            elif line.startswith("inet ") and current_iface:
                ip = line.split()[1].split("/")[0]
                interfaces.append({"interface": current_iface, "ip": ip})
        return interfaces

    @staticmethod
    def start_activity_with_extras(
        package_name: str,
        activity_name: str,
        device_id: str = None,
        string_extras: dict = None,
        int_extras: dict = None,
        bool_extras: dict = None,
    ) -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "am", "start"]

        for key, val in (string_extras or {}).items():
            cmd += ["--es", key, str(val)]
        for key, val in (int_extras or {}).items():
            cmd += ["--ei", key, str(val)]
        for key, val in (bool_extras or {}).items():
            cmd += ["--ez", key, "true" if val else "false"]

        cmd.append(f"{package_name}/{activity_name}")
        subprocess.run(cmd, check=True)

    @staticmethod
    def pull_files(src: str, dest: str, device_id: str = None, retries: int = DEFAULT_RETRY) -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["pull", src, dest]

        for attempt in range(1, retries + 1):
            try:
                subprocess.run(cmd, check=True, capture_output=True, text=True)
                return
            except subprocess.CalledProcessError:
                if attempt >= retries:
                    raise
                time.sleep(1)

    @staticmethod
    def list_device_files(path: str, device_id: str = None, pattern: str = "*") -> list[str]:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "find", path, "-maxdepth", "1", "-type", "f", "-name", pattern]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return [line.strip() for line in result.stdout.splitlines() if line.strip()]

    @staticmethod
    def push_file(src: str, dest: str, device_id: str = None, retries: int = DEFAULT_RETRY) -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["push", src, dest]

        for attempt in range(1, retries + 1):
            try:
                subprocess.run(cmd, capture_output=True, text=True, check=True)
                return
            except subprocess.CalledProcessError:
                if attempt >= retries:
                    raise
                time.sleep(1)

    @staticmethod
    def is_file_exists(path: str, device_id: str = None) -> bool:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", f"test -f {path} && echo 1 || echo 0"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == "1"

    @staticmethod
    def is_folder_exists(path: str, device_id: str = None) -> bool:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", f"test -d {path} && echo 1 || echo 0"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        return result.stdout.strip() == "1"

    @staticmethod
    def remove_folder(path: str, device_id: str = None) -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", f"rm -rf {path}"]
        subprocess.run(cmd, capture_output=True, text=True)

    @staticmethod
    def clear_folder_except(path: str, device_id: str = None, keep: str = "") -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        find_expr = f"find {path} -mindepth 1 -maxdepth 1"
        if keep:
            find_expr += f" ! -name '{keep}'"
        find_expr += " -exec rm -rf {} +"
        cmd += ["shell", find_expr]
        subprocess.run(cmd, capture_output=True, text=True)

    @staticmethod
    def get_downloads_path(device_id: str = None) -> str:
        from utils.constants import ANDROID_DOWNLOAD_PATH
        return AdbUtils.get_default_path(device_id) + "/" + ANDROID_DOWNLOAD_PATH

    @staticmethod
    def get_document_path(device_id: str = None) -> str:
        from utils.constants import ANDROID_DOCUMENTS_PATH
        return AdbUtils.get_default_path(device_id) + "/" + ANDROID_DOCUMENTS_PATH

    @staticmethod
    def get_app_path(device_id: str = None) -> str:
        from utils.constants import ANDROID_DEMO_PATH
        return AdbUtils.get_downloads_path(device_id) + "/" + ANDROID_DEMO_PATH

    @staticmethod
    def get_histogram_path(device_id: str = None) -> str:
        from utils.constants import ANDROID_HISTOGRAM_PATH
        return AdbUtils.get_document_path(device_id) + "/" + ANDROID_HISTOGRAM_PATH

    @staticmethod
    def get_default_path(device_id: str = None) -> str:
        candidates = ["/storage/emulated/0", "/sdcard", "/mnt/sdcard"]
        for path in candidates:
            cmd = ["adb"]
            if device_id:
                cmd += ["-s", device_id]
            cmd += ["shell", "ls", path]
            result = subprocess.run(cmd, capture_output=True, text=True)
            if "No such file" not in result.stdout and "not found" not in result.stdout:
                return path
        return None

    @staticmethod
    def create_tmp_dir(path: str, device_id: str = None) -> None:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "mkdir", "-p", path]
        subprocess.run(cmd, check=True)

    @staticmethod
    def get_connected_devices() -> list[str]:
        try:
            result = subprocess.run(["adb", "devices"], capture_output=True, text=True, check=True)
            lines = result.stdout.strip().split("\n")[1:]
            return [line.split()[0] for line in lines if line.strip() and "device" in line]
        except subprocess.CalledProcessError as e:
            print(f"[AdbUtils.get_connected_devices] {e}")
            return []

    @staticmethod
    def is_contain_package(package_name: str, device_id: str = None) -> bool:
        try:
            cmd = ["adb"]
            if device_id:
                cmd += ["-s", device_id]
            cmd += ["shell", "pm", "list", "packages", "|", "grep", package_name]
            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
            return package_name in result.stdout
        except Exception:
            return False

    @staticmethod
    def is_contain_zrtc_demo_app(device_id: str = None) -> bool:
        return AdbUtils.is_contain_package(APP_PACKAGE)

    @staticmethod
    def get_zrtc_demo_app() -> str:
        return APP_PACKAGE

    @staticmethod
    def install_and_build_zrtc_demo(device_id: str) -> bool:
        try:
            android_arch = AdbUtils.get_android_arch(device_id)
            if not android_arch:
                return False

            apk_path = (
                f"{settings.GIT_CLONE_FOLDER}/{settings.APP_SRC_PATH}"
                "/app/build/outputs/apk/debug/app-debug.apk"
            )
            if os.path.isfile(apk_path):
                if AdbUtils.install_app(apk_path, device_id):
                    return False
                FileUtils.remove_folder(settings.GIT_CLONE_FOLDER)
                return True

            FileUtils.remove_folder(settings.GIT_CLONE_FOLDER)
            clone_cmd = (
                f"git clone --branch {settings.TARGET_BRANCH_NAME} "
                f"--single-branch --depth 1 "
                f"{settings.ZRTC_CORE_URL} {settings.GIT_CLONE_FOLDER}"
            )
            if subprocess.run(clone_cmd, shell=True, preexec_fn=os.setsid).returncode != 0:
                return False

            build_core_cmd = (
                f"pwd && rm -rf .git && "
                f"sed -i '2s|.*|compilerPath={settings.NDK_PATH}|' "
                f"projects/nbprojects-android/common.mk && "
                f"./build/android/clean_all.sh && "
                f"./build/android/{android_arch}_build_debug.sh $(nproc)"
            )
            if subprocess.run(
                build_core_cmd, cwd=settings.GIT_CLONE_FOLDER, shell=True, preexec_fn=os.setsid
            ).returncode != 0:
                return False

            demo_path = os.path.join(settings.GIT_CLONE_FOLDER, settings.APP_SRC_PATH)
            gradle_file = os.path.join(demo_path, "gradle.properties")
            with open(gradle_file, "a") as f:
                f.write(f"\norg.gradle.java.home={settings.JVM_17_PATH}\n")

            if subprocess.run(
                "./gradlew installDebug", cwd=demo_path, shell=True, preexec_fn=os.setsid
            ).returncode != 0:
                return False

            FileUtils.remove_folder(settings.GIT_CLONE_FOLDER)
            return True

        except Exception as e:
            print(f"[AdbUtils.install_and_build_zrtc_demo] {e}")
            return False

    @staticmethod
    def install_app(app_path: str, device_id: str = None) -> bool:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["install", app_path]
        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
        return result.returncode == 0 and "Success" in result.stdout

    @staticmethod
    def has_activity(package_name: str, activity_name: str, device_id: str = None) -> bool:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", f"dumpsys package {package_name} | grep {activity_name}"]
        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
        return result.returncode == 0 and activity_name in result.stdout

    @staticmethod
    def get_android_arch(device_id: str = None) -> str:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "getprop ro.product.cpu.abi"]
        result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True)
        abi = result.stdout.strip()
        if result.returncode != 0 or abi not in ANDROID_ARCH:
            return ""
        return ANDROID_ARCH[abi]

    @staticmethod
    def get_zrtc_demo_app_target_activities(device_id: str = None) -> list[str]:
        from utils.constants import LOGIN_ACTIVITY, MAIN_ACTIVITY
        zrtc_demo_app = AdbUtils.get_zrtc_demo_app()
        return [
            act for act in [LOGIN_ACTIVITY, MAIN_ACTIVITY]
            if AdbUtils.has_activity(zrtc_demo_app, act, device_id)
        ]

    @staticmethod
    def get_cpu_usage(device_id: str = None, package_name: str = PACKAGE_DOMAIN) -> float:
        try:
            cmd = ["adb"]
            if device_id:
                cmd += ["-s", device_id]
            cmd += ["shell", "top", "-n", "1", "|", "grep", package_name, "|", "awk", "'{print $9}'"]
            result = subprocess.run(" ".join(cmd), shell=True, capture_output=True, text=True, timeout=5)
            if result.returncode != 0 or not result.stdout.strip():
                return -1
            for token in result.stdout.strip().replace("%", "").splitlines():
                try:
                    return float(token)
                except ValueError:
                    continue
            return -1
        except (subprocess.TimeoutExpired, Exception):
            return -1

    @staticmethod
    def get_mem_usage(device_id: str = None, package_name: str = APP_PACKAGE) -> float:
        try:
            cmd = ["adb"]
            if device_id:
                cmd += ["-s", device_id]
            cmd += ["shell", "dumpsys", "meminfo", package_name, "||", "grep", "Total"]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=5)
            if result.returncode != 0 or not result.stdout.strip():
                return -1
            match = re.search(r"TOTAL\s+PSS:\s+([\d,]+)", result.stdout)
            if match:
                return int(match.group(1).replace(",", ""))
            return -1
        except (subprocess.TimeoutExpired, Exception):
            return -1

    @staticmethod
    def reset_android(device_id: str = None, package_name: str = APP_PACKAGE) -> None:
        def _run(*extra):
            cmd = ["adb"]
            if device_id:
                cmd += ["-s", device_id]
            cmd += list(extra)
            try:
                subprocess.run(cmd, timeout=5)
            except Exception:
                pass

        _run("shell", "am", "force-stop", package_name)
        _run("shell", "am", "kill-all")
        _run("shell", "pm", "trim-caches", "999999999999")


class StatUtils:
    @staticmethod
    def get_stat(device_id: str, path: str, timeout: int) -> None:
        os.makedirs(path, exist_ok=True)
        FileUtils.remove_stat_file("cpu", path)
        FileUtils.remove_stat_file("mem", path)

        for _ in range(timeout):
            FileUtils.write_stat(path, "cpu", AdbUtils.get_cpu_usage(device_id))
            FileUtils.write_stat(path, "mem", AdbUtils.get_mem_usage(device_id) / 1000.0)
            time.sleep(1)
