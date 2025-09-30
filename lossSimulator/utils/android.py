from .utils import AdbUtils, DateTimeUtils
from .constants import *
from django.conf import settings
import uiautomator2 as u2
import time

class AndroidAppController:
    def __init__(self, deviceId=None, packageName = APP_PACKAGE, path = ANDROID_DEMO_PATH, callMode = CALL_MODE.AUDIO, callOption = CALL_OPTION.LOOPBACK_SERVER.value):
        if deviceId:
            self.d = u2.connect(deviceId)
            self.serial = deviceId
        else:
            self.d = u2.connect()
            self.serial = self.d.serial
        
        
        self.packageName = packageName
        self.defaultPath = AdbUtils.getDownloadsPath(self.d.serial) + "/" + path
        self.timestamp = DateTimeUtils.getTimestamped()
        self.storePath = self.defaultPath + "/" + self.timestamp
        AdbUtils.removeFolder(self.defaultPath)
        AdbUtils.createTmpDir(self.storePath, self.d.serial)

        self.deviceAudioFile = self.defaultPath + "/" + AUDIO_FILE
        AdbUtils.pushFile(STATIC_FOLDER + AUDIO_FILE, self.deviceAudioFile)
        time.sleep(4)

        self.stringExtras = {
            "CALL_MODE": callMode,
            "CALL_OPTION": callOption,
            "RECORD_AUDIO_PATH": self.storePath,
            "AUDIO_FILE_PATH": self.deviceAudioFile
        }
        self.intExtras = None
        self.boolExtras = {
            "ENABLE_OPUS_PLC": False
        }
        

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

    def startEval(self, startEvent, activity=[LOGIN_ACTIVITY, MAIN_ACTIVITY]):
        self.startActivity(activity[0])
        if self.waitForActivity(activity[1]):
            startEvent.set()
