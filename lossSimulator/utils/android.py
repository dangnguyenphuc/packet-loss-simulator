from .utils import AdbUtils, DateTimeUtils
from .constants import (
    APP_PACKAGE, ANDROID_DEMO_PATH, AUDIO_FILE, STATIC_FOLDER,
    LOGIN_ACTIVITY, MAIN_ACTIVITY, DEFAULT_TIMEOUT,
    CALL_BTN_ID, CALL_WITH_SELECTOR_ID, RECORD_CHECKBOX_ID,
    STORING_RECORD_PATH_EDIT_TEXT_ID, PLAY_AUDIO_CHECKBOX_ID,
    PLAY_AUDIO_FILE_EDIT_TEXT_ID, MAKE_AUDIO_CALL_BTN_ID,
    CALL_MODE, CALL_OPTION,
)
import uiautomator2 as u2
import time


class AndroidAppController:
    def __init__(
        self,
        device_id: str = None,
        package_name: str = APP_PACKAGE,
        path: str = ANDROID_DEMO_PATH,
        call_mode: str = CALL_MODE.AUDIO,
        call_option: int = CALL_OPTION.LOOPBACK_SERVER.value,
    ):
        self.d = u2.connect(device_id) if device_id else u2.connect()
        self.serial = device_id or self.d.serial
        self.package_name = package_name

        self.timestamp = DateTimeUtils.get_timestamped()
        default_path = AdbUtils.get_downloads_path(self.d.serial) + "/" + path
        self.default_path = default_path
        self.store_path = default_path + "/" + self.timestamp

        AdbUtils.clear_folder_except(default_path, self.d.serial, keep=AUDIO_FILE)
        AdbUtils.create_tmp_dir(self.store_path, self.d.serial)

        device_audio_file = default_path + "/" + AUDIO_FILE
        AdbUtils.push_file(STATIC_FOLDER + AUDIO_FILE, device_audio_file)
        time.sleep(4)

        self.string_extras = {
            "CALL_MODE": call_mode,
            "CALL_OPTION": call_option,
            "RECORD_AUDIO_PATH": self.store_path,
            "AUDIO_FILE_PATH": device_audio_file,
        }
        self.int_extras = None
        self.bool_extras = {"ENABLE_OPUS_PLC": False}

    def start_app(self, package_name: str = None) -> None:
        self.d.app_start(package_name or self.package_name)

    def stop_all(self) -> None:
        self.d.app_stop_all()

    def stop_app(self, package_name: str = None) -> None:
        target = package_name or self.package_name
        try:
            self.d.app_stop(target)
        except Exception:
            print(f"[AndroidAppController] Cannot stop {target}")

    def click_button(self, resource_id: str) -> None:
        self.d(resourceId=resource_id).click()

    def set_checkbox(self, resource_id: str, checked: bool = True) -> None:
        checkbox = self.d(resourceId=resource_id)
        if not checkbox.exists:
            raise ValueError(f"Checkbox not found: {resource_id}")
        if checkbox.info.get("checked", False) != checked:
            checkbox.click()

    def wait_for_activity(self, resource_id: str, timeout: int = DEFAULT_TIMEOUT) -> bool:
        self.d.wait_activity(resource_id, timeout=timeout)
        if self.d.app_current().get("activity") == resource_id:
            time.sleep(1)
            return True
        print(f"[AndroidAppController] Cannot navigate to {resource_id}")
        return False

    def sleep(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        self.d.sleep(timeout)

    def set_edit_text_value(self, resource_id: str, value) -> None:
        field = self.d(resourceId=resource_id)
        if not field.exists:
            raise ValueError(f"EditText not found: {resource_id}")
        field.clear_text()
        field.set_text(str(value))
        self.press("back")

    def select_spinner_item(self, spinner_resource_id: str, item_text: str, timeout: int = DEFAULT_TIMEOUT) -> None:
        spinner = self.d(resourceId=spinner_resource_id)
        if not spinner.exists:
            raise ValueError(f"Spinner not found: {spinner_resource_id}")
        spinner.click()
        item = self.d(text=item_text)
        if not item.wait(timeout=timeout):
            raise ValueError(f"Spinner item '{item_text}' not found")
        item.click()

    def select_folder(self, timeout: int = DEFAULT_TIMEOUT) -> None:
        confirm_btn = self.d(textMatches=(
            r"(?i)(use this folder|select|select folder|open|open folder|"
            r"choose|choose folder|ok|confirm|save here|"
            r"sử dụng thư mục này|chọn|chọn thư mục|mở|mở thư mục|đồng ý|xác nhận|lưu tại đây)"
        ))
        if confirm_btn.wait(timeout=timeout):
            confirm_btn.click()

        accept_btn = self.d(textMatches=r"(?i)(accept|allow|grant|yes|cho phép|cấp quyền|đồng ý)")
        if accept_btn.wait(timeout=timeout):
            accept_btn.click()

    def press(self, cmd: str) -> None:
        self.d.press(cmd)

    def start_activity(
        self,
        activity: str,
        string_extras: dict = None,
        int_extras: dict = None,
        bool_extras: dict = None,
    ) -> None:
        AdbUtils.start_activity_with_extras(
            self.package_name,
            activity,
            self.serial,
            string_extras or self.string_extras,
            int_extras or self.int_extras,
            bool_extras or self.bool_extras,
        )

    def start_eval(self, start_event=None, activity: list = None) -> None:
        if activity is None:
            activity = [LOGIN_ACTIVITY, MAIN_ACTIVITY]
        self.start_activity(activity[0])
        self.wait_for_activity(activity[1])
        if start_event:
            start_event.set()
