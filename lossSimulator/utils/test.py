import uiautomator2 as u2
import subprocess
from datetime import datetime
import time

DEFAULT_TIMEOUT = 5

PACKAGE = "com.vng.zing.vn.zrtc.demo"
APP_PACKAGE = f"{PACKAGE}.debug"
# Zrtc demo app activity
DEMO_ACTIVITY = f"{PACKAGE}.DemoModeActivity"
CALL_BTN_ID = f"{APP_PACKAGE}:id/button_call"

# Login activity
LOGIN_ACTIVITY = f"{PACKAGE}.LoginActivity"
CALL_WITH_SELECTOR_ID = f"{APP_PACKAGE}:id/spinner_call_with_mode"
RECORD_CHECKBOX_ID = f"{APP_PACKAGE}:id/flag_record_audio"
STORING_RECORD_PATH_EDIT_TEXT_ID = f"{APP_PACKAGE}:id/storing_path_record_text"
MAKE_AUDIO_CALL_BTN_ID = f"{APP_PACKAGE}:id/btn_make_audio_call"

def getTimestamped():
    return datetime.now().strftime("%d-%m-%Y_%H%M%S")


def getDownloadsPath(device_id=None):
    candidates = [
        "/sdcard/Download",
        "/storage/emulated/0/Download",
        "/mnt/sdcard/Download"
    ]
    for path in candidates:
        cmd = ["adb"]
        if device_id:
            cmd += ["-s", device_id]
        cmd += ["shell", "ls", path]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if "No such file" not in result.stdout and "not found" not in result.stdout:
            return path + "/demo"
    return None

def createTmpDir(path, device_serial=None):
    cmd = ["adb"]
    if device_serial:
        cmd += ["-s", device_serial]
    cmd += ["shell", "mkdir", "-p", path]

    subprocess.run(cmd, check=True)
    print(f"Created dir: {path} on device {device_serial or ''}")


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


import uiautomator2 as u2

class AndroidAppController:
    def __init__(self, deviceId=None, packageName = APP_PACKAGE):
        if deviceId:
            self.d = u2.connect(deviceId)
        else:
            self.d = u2.connect()
        
        self.packageName = packageName
        self.storePath = getDownloadsPath(self.d.serial) + "/" + getTimestamped()
        createTmpDir(self.storePath, self.d.serial)
        

    def startApp(self, packageName = None):
        if packageName:
            self.d.app_start(packageName)
        else:
            self.d.app_start(self.packageName)

    def stopAll(self):
        self.d.app_stop_all()

    def stopApp(self, packageName = None):
        try:
            if packageName:
                self.d.app_stop(packageName)
            else:
                self.d.app_stop(self.packageName)

        except:
            print(f"Cannot stop {packageName if packageName else self.packageName}")

    def clickButton(self, resourceId):
        self.d(resourceId=resourceId).click()

    def setCheckbox(self, resourceId, checked=True):
        checkbox = self.d(resourceId=resourceId)
        if not checkbox.exists:
            raise Exception(f"Checkbox with resourceId {resourceId} not found")

        currentState = checkbox.info.get("checked", False)
        if currentState != checked:
            checkbox.click()

    def waitForActivity(self, resourceId, timeout = DEFAULT_TIMEOUT):
        self.d.wait_activity(resourceId, timeout=timeout)
        if self.d.app_current().get('activity') == resourceId: 
            return True
        else:
            print(f"Cannot get into {resourceId} template!!")
            return False
    
    def sleep(self, timeout = DEFAULT_TIMEOUT):
        self.d.sleep(timeout)

    def setEditTextValue(self, resourceId, value):
        try:
            field = self.d(resourceId=resourceId)
            if not field.exists:
                raise Exception(f"[ERROR] EditText {resourceId} not found")
            field.clear_text()
            field.set_text(str(value))
        except Exception as e:
            raise e
    
    def selectSpinnerItem(self, spinnerResourceId, itemText, timeout = DEFAULT_TIMEOUT):
        try:
            spinner = self.d(resourceId=spinnerResourceId)
            if not spinner.exists:
                raise Exception(f"[ERROR] Spinner {spinnerResourceId} not found")

            spinner.click()
            
            item = self.d(text=itemText)
            if not item.wait(timeout=timeout):
                raise Exception(f"[ERROR] Spinner item '{itemText}' not found")

            item.click()
        except Exception as e:
            raise e
        
    def selectFolder(self, timeout = DEFAULT_TIMEOUT):
            confirmBtn = self.d(textMatches="(?i)(use this folder|select|select folder|open|open folder|choose|choose folder|ok|confirm|save here|sử dụng thư mục này|chọn|chọn thư mục|mở|mở thư mục|đồng ý|xác nhận|lưu tại đây)")
            if confirmBtn.wait(timeout=timeout):
                confirmBtn.click()

            acceptBtn = self.d(textMatches="(?i)(accept|allow|grant|yes|cho phép|cấp quyền|đồng ý)")
            if acceptBtn.wait(timeout=timeout):
                acceptBtn.click()

    def press(self, cmd):
        self.d.press(cmd)

if __name__ == "__main__":
    devices = getConnectedDevices()
    if len(devices) > 0:   
        print(devices)
        controller = AndroidAppController(deviceId=devices[0])
        controller.stopAll()
        controller.sleep(2)
        controller.startApp()
        try:
            if controller.waitForActivity(DEMO_ACTIVITY):
                # Loaded demo page
                controller.clickButton(CALL_BTN_ID)
                if controller.waitForActivity(LOGIN_ACTIVITY):
                    # Loaded login page
                    controller.sleep(1)
                    controller.setCheckbox(RECORD_CHECKBOX_ID, True)
                    controller.selectSpinnerItem(CALL_WITH_SELECTOR_ID, "Server")
                    controller.sleep(1)
                    controller.setEditTextValue(STORING_RECORD_PATH_EDIT_TEXT_ID, controller.storePath)
                    # controller.selectFolder()
                    controller.sleep(1)
                    controller.clickButton(MAKE_AUDIO_CALL_BTN_ID)

                    controller.sleep(10)
                    controller.press("back")
                    controller.press("back")
        except Exception as e:
            print(e)
            controller.stopApp()