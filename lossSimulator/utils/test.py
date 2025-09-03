import uiautomator2 as u2
import subprocess
from datetime import datetime
import time
from enum import Enum

'''
adb defined intents:
CALL_MODE: str
RECORD_AUDIO_PATH: str
CALL_OPTION: str
AUDIO_FILE_PATH: str
'''

DEFAULT_TIMEOUT = 5
DEFAULT_EVAL_TIMEOUT = 30

DESKTOP_STATIC_FOLDER = "../static/"
AUDIO_FILE = "audio.wav"
ANDROID_DEMO_PATH = "demoapp"

PACKAGE = "com.vng.zing.vn.zrtc.demo"
APP_PACKAGE = f"{PACKAGE}.debug"
# Zrtc demo app activity
DEMO_ACTIVITY = f"{PACKAGE}.DemoModeActivity"
CALL_BTN_ID = f"{APP_PACKAGE}:id/button_call"

# Login activity
LOGIN_ACTIVITY = f"{PACKAGE}.LoginActivity"
# call with section
CALL_WITH_SELECTOR_ID = f"{APP_PACKAGE}:id/spinner_call_with_mode"
# record folder section
RECORD_CHECKBOX_ID = f"{APP_PACKAGE}:id/flag_record_audio"
STORING_RECORD_PATH_EDIT_TEXT_ID = f"{APP_PACKAGE}:id/storing_path_record_text"
# audio file section
PLAY_AUDIO_CHECKBOX_ID = f"{APP_PACKAGE}:id/flag_play_audio"
PLAY_AUDIO_FILE_EDIT_TEXT_ID = f"{APP_PACKAGE}:id/played_audio_file"
# buttons section
MAKE_AUDIO_CALL_BTN_ID = f"{APP_PACKAGE}:id/btn_make_audio_call"

# Main Activity
MAIN_ACTIVITY = f"{PACKAGE}.ConferenceActivity"

class CALL_OPTION(Enum):
    LOOPBACK_SERVER = 0
    SERVER = 1
    LOOPBACK_LOCAL = 2

class CALL_MODE:
    AUDIO = "audio"
    VIDEO = "video"
    GROUP = "group"

class DateTimeUtils:
    @staticmethod
    def getTimestamped():
        return datetime.now().strftime("%d-%m-%Y_%H%M%S")

class AdbUtils:
    @staticmethod
    def startActivityWithExtras(packageName, activityName, deviceId=None, stringExtras=None, intExtras=None, boolExtras=None):
        cmd = ["adb"]
        if deviceId:  # only add -s if user provided
            cmd += ["-s", deviceId]
        cmd += ["shell", "am", "start"]

        # String extras
        if stringExtras:
            for key, val in stringExtras.items():
                cmd += ["--es", key, str(val)]

        # Int extras
        if intExtras:
            for key, val in intExtras.items():
                cmd += ["--ei", key, str(val)]

        if boolExtras:
            for key, val in boolExtras.items():
                cmd += ["--ez", key, "true" if val else "false"]

        cmd.append(f"{packageName}/{activityName}")
        subprocess.run(cmd, check=True)

    @staticmethod
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
                return path
        return None
class AdbUtils:

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

    def pullFiles(src, des, deviceId=None):
        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["pull", src, des]

        try:
            subprocess.run(cmd, check=True)
        except subprocess.CalledProcessError as e:
            raise e

    @staticmethod
    def pushFile(src, dest, deviceId=None):

        cmd = ["adb"]
        if deviceId:
            cmd += ["-s", deviceId]
        cmd += ["push", src, dest]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            return True
        except subprocess.CalledProcessError as e:
            print(e.stderr)
            return False
    
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
        candidates = [
            "/storage/emulated/0/Download",
            "/sdcard/Download",
            "/mnt/sdcard/Download"
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

class AndroidAppController:
    def __init__(self, deviceId=None, packageName = APP_PACKAGE, path = ANDROID_DEMO_PATH, callMode = CALL_MODE.AUDIO, callOption = CALL_OPTION.LOOPBACK_SERVER.value):
        if deviceId:
            self.d = u2.connect(deviceId)
        else:
            self.d = u2.connect()
        
        self.serial = self.d.serial
        
        self.packageName = packageName
        self.defaultPath = AdbUtils.getDownloadsPath(self.d.serial) + "/" + path
        self.storePath = self.defaultPath + "/" + DateTimeUtils.getTimestamped()
        AdbUtils.createTmpDir(self.storePath, self.d.serial)

        self.deviceAudioFile = self.defaultPath + "/" + AUDIO_FILE
        AdbUtils.pushFile(DESKTOP_STATIC_FOLDER + AUDIO_FILE, self.deviceAudioFile)

        self.stringExtras = {
            "CALL_MODE": callMode,
            "CALL_OPTION": callOption,
            "RECORD_AUDIO_PATH": self.storePath,
            "AUDIO_FILE_PATH": self.deviceAudioFile
        }
        self.intExtras = None
        self.boolExtras = None
        

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
            self.press("back")
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

    def startActivity(self, activity, stringExtras=None, intExtras=None, boolExtras=None):
        if stringExtras or intExtras or boolExtras:
            AdbUtils.startActivityWithExtras(self.packageName, activity, self.serial, stringExtras, intExtras, boolExtras)
        else:
            AdbUtils.startActivityWithExtras(self.packageName, activity, self.serial, self.stringExtras, self.intExtras, self.boolExtras)

    def startEval(self, activity,timeout = DEFAULT_EVAL_TIMEOUT, pcAudioPath = DESKTOP_STATIC_FOLDER):
        self.startActivity(activity[0])
        if self.waitForActivity(activity[1]):
            self.sleep(timeout)
            self.press("back")
            self.press("back")

            self.stopApp()

            # pull audio files
            AdbUtils.pullFiles(self.storePath, pcAudioPath, self.serial)

if __name__ == "__main__":
    devices = AdbUtils.getConnectedDevices()
    
    if len(devices) > 0:   
        print(devices)
        controller = AndroidAppController(deviceId=devices[0])
        controller.stopAll()
        controller.sleep(2)
        try:
            # controller.startApp()
            # if controller.waitForActivity(DEMO_ACTIVITY):
            #     # Loaded demo page
            #     controller.clickButton(CALL_BTN_ID)
            #     if controller.waitForActivity(LOGIN_ACTIVITY):
            #         # Loaded login page
            #         controller.sleep(1)
            #         controller.selectSpinnerItem(CALL_WITH_SELECTOR_ID, CALL_WITH_SELECTIONS[2])
            #         controller.sleep(1)
            #         # if storing folder exist
            #         if AdbUtils.isFolderExists(controller.storePath, controller.d.serial):
            #             controller.setCheckbox(RECORD_CHECKBOX_ID, True)
            #             controller.setEditTextValue(STORING_RECORD_PATH_EDIT_TEXT_ID, controller.storePath)
            #         controller.sleep(1)
                    
            #         if AdbUtils.isFileExists(deviceAudioFile, controller.d.serial):
            #             controller.setCheckbox(PLAY_AUDIO_CHECKBOX_ID, True)
            #             controller.setEditTextValue(PLAY_AUDIO_FILE_EDIT_TEXT_ID, deviceAudioFile)
            #         controller.sleep(1)

            #         controller.clickButton(MAKE_AUDIO_CALL_BTN_ID)

            #         controller.sleep(10)
            #         controller.press("back")
            #         controller.press("back")
            
            controller.startEval([LOGIN_ACTIVITY, MAIN_ACTIVITY], timeout=5)
            
        except Exception as e:
            print(e)
            controller.stopApp()