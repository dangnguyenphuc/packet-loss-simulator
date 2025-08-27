import uiautomator2 as u2

APP_PACKAGE = "com.vng.zing.vn.zrtc.demo.debug"

d = u2.connect()  # connects to adb device
d.app_start(APP_PACKAGE)
d(resourceId=f"{APP_PACKAGE}:id/button_call").click()
