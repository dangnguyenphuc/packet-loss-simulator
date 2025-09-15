from constants import *
from utils import AdbUtils
from android import AndroidAppController


if __name__ == "__main__":
    devices = AdbUtils.getConnectedDevices()
    
    if len(devices) > 0:   
        print(devices)
        controller = AndroidAppController(deviceId=devices[0])
        controller.stopAll()
        controller.sleep(2)
        try:
            controller.startEval([LOGIN_ACTIVITY, MAIN_ACTIVITY], timeout=20)
            
        except Exception as e:
            print(e)
            controller.stopApp()