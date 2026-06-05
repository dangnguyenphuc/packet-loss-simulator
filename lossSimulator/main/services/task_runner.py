import queue
import threading
import time
import os

from multiprocessing import Process, Event
from django.conf import settings

from utils.utils import FileUtils, AdbUtils, StatUtils
from utils.android import AndroidAppController
from utils.constants import DESKTOP_STATIC_FOLDER

from main.services.task_store import myCache, tasks

task_queue = queue.Queue()


def build_app(device_id: str, task_id: str) -> None:
    result = AdbUtils.install_and_build_zrtc_demo(device_id)
    myCache[task_id] = {
        "info": bool(result),
        "time": time.time(),
    }


def run_app(
    task_id: str,
    device_id: str,
    enable_opus_plc: bool,
    dred_duration: int,
    dec_complexity: int,
    timeout: int,
    start_event,
    complexity: int = None,
    folder_name: str = None,
) -> None:
    controller = AndroidAppController(device_id=device_id)
    static_folder = FileUtils.get_abs_path(str(settings.BASE_DIR) + "/" + DESKTOP_STATIC_FOLDER)
    specific_folder = (
        static_folder + "/" +
        f"en-{complexity}_dec-{dec_complexity}_"
        f"{'plc_' if enable_opus_plc else 'normal_'}"
        f"dred-{dred_duration}_"
        f"{folder_name + '_' if folder_name else ''}"
        f"{controller.timestamp}"
    )

    tmp = tasks.get(task_id, {})
    tmp["targetFolder"] = specific_folder
    tasks[task_id] = tmp

    controller.stop_all()
    try:
        controller.bool_extras["ENABLE_OPUS_PLC"] = enable_opus_plc
        controller.string_extras["DRED_DURATION"] = dred_duration
        controller.string_extras["OPUS_DEC_COMPLEXITY"] = dec_complexity
        controller.string_extras["OPUS_COMPLEXITY"] = complexity
        controller.start_eval(start_event)
        time.sleep(timeout)
        controller.press("back")
        controller.press("back")
        controller.stop_app()

        FileUtils.make_dir(specific_folder)
        AdbUtils.pull_files(controller.store_path, specific_folder, device_id)
        AdbUtils.pull_files(AdbUtils.get_histogram_path(), specific_folder, device_id)

        try:
            FileUtils.move_files(
                specific_folder + "/" + "_".join(specific_folder.split("_")[-2:]),
                specific_folder,
            )
            FileUtils.remove_folder(specific_folder + "/" + controller.store_path.split("/")[-1])
        finally:
            myCache[task_id] = {
                "time": time.time(),
                "duration": timeout,
                "audioFiles": FileUtils.get_audio_files(specific_folder),
                "zrtcLog": FileUtils.get_log_files(specific_folder),
            }
    except Exception as e:
        print(f"[run_app] Exception: {e}")
        start_event.set()
        controller.stop_all()


def _worker() -> None:
    while True:
        item = task_queue.get()
        if item is None:
            break

        task_id = item["task_id"]

        tmp = tasks.get(task_id, {})
        tmp["status"] = "running"
        tasks[task_id] = tmp

        start_event = Event()
        run = Process(
            target=run_app,
            args=(
                task_id,
                item["device_id"],
                item["enable_opus_plc"],
                item["dred_duration"],
                item["dec_complexity"],
                item["timeout"],
                start_event,
                item["complexity"],
                item["folder_name"],
            ),
        )
        run.start()
        start_event.wait()

        stat_monitor = Process(
            target=StatUtils.get_stat,
            args=(item["device_id"], tasks[task_id]["targetFolder"], item["timeout"]),
        )
        stat_monitor.start()

        tmp = tasks.get(task_id, {})
        tmp["thread"] = [stat_monitor.pid, run.pid]
        tasks[task_id] = tmp

        run.join()
        stat_monitor.join()

        task_queue.task_done()


def start_worker() -> None:
    t = threading.Thread(target=_worker, daemon=True)
    t.start()
