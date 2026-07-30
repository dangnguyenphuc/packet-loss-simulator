import json
import uuid
import time
import signal
import os

from django.http import JsonResponse
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

from utils.utils import AdbUtils, AudioUtils, FileUtils
from utils.constants import DEFAULT_EVAL_TIMEOUT, DESKTOP_STATIC_FOLDER

from main.services.task_store import myCache, tasks
from main.services.task_runner import task_queue, build_app

from multiprocessing import Process, Event


@method_decorator(csrf_exempt, name="dispatch")
class TaskRunView(View):

    def _missing_device_response(self):
        return JsonResponse(
            {"error": "Invalid device id", "details": "device id is empty"},
            status=400,
        )

    def _invalid_type_response(self):
        return JsonResponse(
            {"error": "Invalid task type", "details": "Type: run | install"},
            status=400,
        )

    def _invalid_json_response(self, exc: Exception):
        return JsonResponse(
            {"error": "Invalid JSON payload", "details": str(exc)},
            status=400,
        )

    def _validate_device(self, device_id: str) -> bool:
        return bool(device_id) and AdbUtils.is_device_exists(device_id)

    def post(self, request, device_id, type):
        if not self._validate_device(device_id):
            return self._missing_device_response()

        match type:
            case "install":
                return self._install(device_id)
            case "run":
                return self._run(request, device_id)
            case "move":
                return self._move()
            case _:
                return self._invalid_type_response()

    def _move(self):
        from django.conf import settings
        static_folder = FileUtils.get_abs_path(str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER)
        FileUtils.move_files(static_folder, "/home/dangnp/workspace/tmp/audio")
        return JsonResponse({}, status=200)

    def _install(self, device_id: str):
        task_id = str(uuid.uuid4())
        p = Process(target=build_app, args=(device_id, task_id))
        p.start()
        tasks[task_id] = {
            "thread": [p.pid],
            "type": "install",
            "id": device_id,
            "status": "running",
        }
        return JsonResponse({"status": "started", "taskId": task_id}, status=202)

    def _run(self, request, device_id: str):
        try:
            data = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return self._invalid_json_response(e)

        task_id = str(uuid.uuid4())
        start_event = Event()
        tasks[task_id] = {
            "thread": [],
            "type": "run",
            "id": device_id,
            "targetFolder": "",
            "status": "queued",
        }
        task_queue.put({
            "task_id": task_id,
            "device_id": device_id,
            "enable_opus_plc": data.get("enableOpusPlc", False),
            "dred_duration": data.get("dredDuration", 0),
            "dec_complexity": data.get("decComplexity", 6),
            "timeout": data.get("time", DEFAULT_EVAL_TIMEOUT),
            "complexity": data.get("complexity", 5),
            "folder_name": data.get("folderName"),
            "pull_audio": data.get("pullAudio", False),
            "start_event": start_event,
        })

        # Block the response until the queued app process has actually started
        # (or failed to), so the frontend's countdown stays in sync with the
        # backend's eval timeout instead of starting the moment it's queued.
        start_event.wait()
        return JsonResponse({"status": "started", "taskId": task_id}, status=202)


@method_decorator(csrf_exempt, name="dispatch")
class TaskDetailView(View):

    def get(self, request, task_id):
        return self._check_task(task_id)

    def delete(self, request, task_id):
        return self._stop_task(task_id)

    def _check_task(self, task_id: str):
        task = tasks.get(task_id)
        if task and task.get("status") == "queued":
            return JsonResponse({"status": "queued"}, status=202)

        # Expire stale cache entries
        now = time.time()
        for key in list(myCache.keys()):
            if now - myCache[key]["time"] >= 71:
                myCache.pop(key, None)

        result = myCache.get(task_id)
        if not result:
            return JsonResponse({"status": "failed"}, status=404)

        if result.get("skipped"):
            return JsonResponse({"status": "done", "result": result}, status=200)

        valid_audio = any(
            AudioUtils.is_valid_audio_file(audio, result["duration"])
            for audio in result["audioFiles"]
        )
        if valid_audio:
            result["audioFiles"] = [f.split("public")[-1] for f in result["audioFiles"]]
            return JsonResponse({"status": "done", "result": result}, status=200)

        return JsonResponse({"status": "processing"}, status=202)

    def _stop_task(self, task_id: str):
        task = tasks.get(task_id)
        if not task:
            return JsonResponse({"error": "Task not found or already finished"}, status=404)

        pids = task["thread"]
        task_type = task["type"]
        device_id = task["id"]

        for pid in pids:
            try:
                os.kill(pid, signal.SIGTERM)
                time.sleep(0.1)
                os.waitpid(pid, os.WNOHANG)
            except ProcessLookupError:
                pass
            except Exception as e:
                print(f"[TaskDetailView._stop_task] pid={pid}: {e}")

        if task_type == "run":
            AdbUtils.reset_android(device_id)

        tasks.pop(task_id, None)
        return JsonResponse({"status": "stopping", "taskId": task_id}, status=200)
