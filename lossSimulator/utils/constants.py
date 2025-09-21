from enum import Enum
from django.conf import settings

NETWORK_ATC_SUBMASK_NET = "10.42.0.0/24"
NETWORK_ATC_GATEWAY_IP = "http://10.42.0.1:8080"
NETWORK_ATC_ENDPOINT = "/api/v1/shape/"
NETWORK_ATC_MAX_RETRY = 5

STATIC_FOLDER = f"{str(settings.BASE_DIR)}/static/"
JSON_CONFIG_FOLDER = f"{str(settings.BASE_DIR)}/main/static/main/json"
AUDIO_TYPE = ".wav"
LOG_TYPE = ".log"

# =====================================================================
# ========================== ANDROID Constants ========================
# =====================================================================
DEFAULT_TIMEOUT = 5
DEFAULT_EVAL_TIMEOUT = 30

class CALL_OPTION(Enum):
    LOOPBACK_SERVER = 0
    SERVER = 1
    LOOPBACK_LOCAL = 2

class CALL_MODE:
    AUDIO = "audio"
    VIDEO = "video"
    GROUP = "group"


DESKTOP_STATIC_FOLDER = "../frontend/loss-simulator/public/audio/"
AUDIO_FILE = "audio.wav"
ANDROID_DEMO_PATH = "demoapp"
ANDROID_DOWNLOAD_PATH = "Download"
ANDROID_DOCUMENTS_PATH = "Documents"

ANDROID_HISTOGRAM_PATH = "ZrtcDemoLog/stats_call.log"

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

# =====================================================================
# ========================== ANDROID Constants ========================
# =====================================================================
