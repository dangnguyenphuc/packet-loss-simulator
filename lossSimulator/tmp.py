
TARGET_BRANCH_NAME = "dangnp/android/refactor"
NDK_PATH  = "/home/dangnp/tools/android-ndk/android-ndk-r25c/toolchains/llvm/prebuilt/linux-x86_64/bin"
APP_SRC_PATH = "example/android/ZRtcExample"

username = ""
password = ""
repoUrl = f""
token = ""

tmpDir = "zrtc"
cloneCmd = f"git clone --branch {TARGET_BRANCH_NAME} --single-branch --depth 1 {repoUrl} {tmpDir}"
buildCoreCmd = f"cd zrtc/ &&\
    sed -i '2s/.*/{NDK_PATH}' projects/nbprojects-android/common.mk &&\
    ./build/android/clean_all.sh &&\
    ./build/android/arm64_build_debug.sh"
buildDemoApp = f"cd zrtc/{APP_SRC_PATH} &&\
    echo 'org.gradle.java.home=$JVM_PATH' >> gradle.properties &&\
    ./gradlew && ./gradlew installDebug"

device = ""

installApp = f"cd zrtc/{APP_SRC_PATH}/app/build/outputs/apk/debug &&\
    adb -s {device} install app-debug.apk"

