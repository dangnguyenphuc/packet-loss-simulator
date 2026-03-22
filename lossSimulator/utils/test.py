import subprocess

PACKAGE_DOMAIN = "com.vng.zing.vn"
PACKAGE = f"{PACKAGE_DOMAIN}.zrtc.demo"
APP_PACKAGE = f"{PACKAGE}.debug"
MAIN_ACTIVITY = f"{PACKAGE}.ConferenceActivity"
LOGIN_ACTIVITY = f"{PACKAGE}.LoginActivity"

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

if __name__ == "__main__":
    device = getConnectedDevices()[0]
    boolExtras = {}
    stringExtras = {}

    boolExtras["ENABLE_OPUS_PLC"] = False
    stringExtras["DRED_DURATION"] = 20
    stringExtras["OPUS_COMPLEXITY"] = 6
    stringExtras["OPUS_DEC_COMPLEXITY"] = 8
    stringExtras["AUDIO_FILE_PATH"] = "/storage/emulated/0/Download/demoapp/audio.wav"

    startActivityWithExtras(APP_PACKAGE, LOGIN_ACTIVITY, device, stringExtras, {}, boolExtras)