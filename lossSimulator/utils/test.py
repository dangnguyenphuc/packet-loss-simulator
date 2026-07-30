import subprocess

PACKAGE_DOMAIN = "com.vng.zing.vn"
PACKAGE = f"{PACKAGE_DOMAIN}.zrtc.demo"
APP_PACKAGE = f"{PACKAGE}.debug"
MAIN_ACTIVITY = f"{PACKAGE}.ConferenceActivity"
LOGIN_ACTIVITY = f"{PACKAGE}.LoginActivity"

def start_activity_with_extras(package_name, activity_name, device_id=None, string_extras=None, int_extras=None, bool_extras=None):
    cmd = ["adb"]
    if device_id:
        cmd += ["-s", device_id]
    cmd += ["shell", "am", "start"]

    if string_extras:
        for key, val in string_extras.items():
            cmd += ["--es", key, str(val)]

    if int_extras:
        for key, val in int_extras.items():
            cmd += ["--ei", key, str(val)]

    if bool_extras:
        for key, val in bool_extras.items():
            cmd += ["--ez", key, "true" if val else "false"]

    cmd.append(f"{package_name}/{activity_name}")
    try:
        print("dangn")
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(e)
        raise e


def get_connected_devices():
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
    device = get_connected_devices()[0]
    bool_extras = {}
    string_extras = {}

    bool_extras["ENABLE_OPUS_PLC"] = False
    string_extras["DRED_DURATION"] = 20
    string_extras["OPUS_COMPLEXITY"] = 6
    string_extras["OPUS_DEC_COMPLEXITY"] = 8
    string_extras["AUDIO_FILE_PATH"] = "/storage/emulated/0/Download/demoapp/audio.wav"

    start_activity_with_extras(APP_PACKAGE, LOGIN_ACTIVITY, device, string_extras, {}, bool_extras)