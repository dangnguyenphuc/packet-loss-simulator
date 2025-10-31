import argparse
import json
import time
import requests
import os
import random
import subprocess

# ==== CONFIG ====
BASE_URL = "http://10.42.0.1:8080/api/v1/shape/"
DEFAULT_IP = "10.42.0.88"
PREFIX_FOLDER = "./lossSimulator/main/static/main/json/"
MAX_RETRY = 3
DEFAULT_STATE_DURATION = 5
DEFAULT_TOTAL_STATES = 100
STEP = 5
DELAY_BETWEEN_POSTS = 3
TARGET_PACKAGE = "com.vng.zing.vn.zrtc.demo.debug"

NETWORK_CONDITIONS = [
    "Edge-Lossy.json",            # 0
    "Edge-Average.json",          # 1
    "Edge-Good.json",             # 2
    "2G-DevelopingRural.json",    # 3
    "2G-DevelopingUrban.json",    # 4
    "3G-Poor.json",               # 5
    "3G-Average.json",            # 6
    "3G-Good.json",               # 7
    "4G-Poor.json",               # 8
    "4G-Average.json",            # 9
    "4G-Good.json",               #10
    "Wifi-Poor.json",             #11
    "Wifi-Average.json",          #12
    "Wifi-Good.json",             #13
    "5G-Poor.json",               #14
    "5G-Average.json",            #15
    "5G-Good.json",               #16
]


# ==== SAMPLE DATA ====
SAMPLE_DATA = {
  "down": {
    "corruption": {
      "correlation": 10,
      "percentage": 6
    },
    "delay": {
      "correlation": 10,
      "delay": "100",
      "jitter": 220
    },
    "iptables_options": [],
    "loss": {
      "correlation": 2,
      "percentage": 20
    },
    "rate": "500",
    "reorder": {
      "correlation": 10,
      "gap": 8,
      "percentage": 5
    }
  },
  "up": {
    "corruption": {
      "correlation": 0,
      "percentage": 0
    },
    "delay": {
      "correlation": 0,
      "delay": "0",
      "jitter": 0
    },
    "iptables_options": [],
    "loss": {
      "correlation": 0,
      "percentage": 0
    },
    "rate": None,
    "reorder": {
      "correlation": 0,
      "gap": 0,
      "percentage": 0
    }
  }
}


# ==== HELPERS ====

def delete_shape(endpoint):
    for attempt in range(3):
        try:
            response = requests.delete(endpoint)
            print(f"[DELETE {attempt+1}/3] Status: {response.status_code}")
            time.sleep(0.3)
        except Exception as e:
            print(f"[DELETE {attempt+1}/3] Error: {e}")


def post_shape(endpoint, data, label):
    headers = {"Content-Type": "application/json"}
    for attempt in range(MAX_RETRY):
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            print(f"[POST {attempt+1}/{MAX_RETRY}] {label} -> {response.status_code}")
            if response.status_code // 200 == 1:
                return True
        except Exception as e:
            print(f"[POST ERROR] {e}")
        time.sleep(1)
    return False


def choose_next_index(current_index):
    last_index = len(NETWORK_CONDITIONS) - 1
    rand = random.random()

    if current_index == 0:
        return current_index if rand < 0.5 else random.randint(current_index + 1, last_index)
    elif current_index == last_index:
        return current_index if rand < 0.5 else random.randint(0, current_index - 1)
    else:
        if rand < 0.2:
            return current_index
        elif rand < 0.6:
            return random.randint(current_index + 1, last_index)
        else:
            return random.randint(0, current_index - 1)


def pick_initial_index():
    candidates = [i for i, name in enumerate(NETWORK_CONDITIONS)
                  if ("3G" in name or "4G" in name or "Wifi" in name or "5G" in name)
                  and ("Average" in name or "Good" in name)]
    return random.choice(candidates) if candidates else 6


def preload_network_data():
    loaded_data = []
    for filename in NETWORK_CONDITIONS:
        path = os.path.join(PREFIX_FOLDER, filename)
        try:
            with open(path, "r") as f:
                data = json.load(f)
                loaded_data.append(data)
            print(f"[LOAD] {filename} ✅")
        except Exception as e:
            print(f"[LOAD ERROR] {filename}: {e}")
            loaded_data.append(None)
    return loaded_data


def force_stop_package(package_name):
    try:
        print(f"🛑 Forcing stop for package: {package_name}")
        result = subprocess.run(
            ["adb", "shell", "am", "force-stop", package_name],
            capture_output=True,
            text=True,
        )
        if result.returncode == 0:
            print(f"✅ Successfully stopped package: {package_name}")
        else:
            print(f"❌ Failed to stop package: {package_name}\n{result.stderr}")
    except Exception as e:
        print(f"⚠️  Error while trying to stop package: {e}")


# ==== MODE: SINGLE ====
def run_single_mode(endpoint):
    delete_shape(endpoint)
    loss_values = list(range(5, 91, STEP)) + list(range(85, 4, -STEP))
    print(f"Starting SINGLE mode sweep: {loss_values}")

    try:
        # for loss in loss_values:
        #     SAMPLE_DATA["down"]["loss"]["percentage"] = loss
        #     print(f"\n➡️  Setting down.loss.percentage = {loss}%")
        #     success = post_shape(endpoint, SAMPLE_DATA, f"loss={loss}")
        #     if success:
        #         print(f"✅ Applied loss = {loss}% successfully")
        #     else:
        #         print(f"❌ Failed to apply loss = {loss}%")
        #     time.sleep(DELAY_BETWEEN_POSTS)

        # for loss in loss_values:
        #     SAMPLE_DATA["down"]["loss"]["percentage"] = loss
        #     print(f"\n➡️  Setting down.loss.percentage = {loss}%")


        success = post_shape(endpoint, SAMPLE_DATA, "SAMPLE_DATA")
        if success:
            print(f"✅ Applied SAMPLE_DATA successfully")
        else:
            print(f"❌ Failed to apply SAMPLE_DATA")
        time.sleep(30)

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user.")
    finally:
        print("🧹 Cleaning up (SINGLE mode)...")
        delete_shape(endpoint)
        # force_stop_package(TARGET_PACKAGE)
        print("🏁 Done.")


# ==== MODE: MULTIPLE ====
def run_multiple_mode(endpoint, state_duration, total_states):
    delete_shape(endpoint)

    print("\n📂 Preloading all network condition JSON files...")
    NETWORK_DATA = preload_network_data()
    print("✅ All JSONs loaded.\n")

    current_index = pick_initial_index()
    print(f"🚀 Starting simulation from: {NETWORK_CONDITIONS[current_index]} (index {current_index})")

    try:
        for step in range(1, total_states + 1):
            label = NETWORK_CONDITIONS[current_index]
            data = NETWORK_DATA[current_index]

            if data is None:
                print(f"⚠️ Skipping {label} (unloaded or invalid)")
                current_index = choose_next_index(current_index)
                continue

            print(f"\n[STATE {step}/{total_states}] Applying: {label}")
            success = post_shape(endpoint, data, label)
            if success:
                print(f"✅ Applied {label} successfully.")
            else:
                print(f"❌ Failed to apply {label}.")

            time.sleep(state_duration)

            next_index = choose_next_index(current_index)
            print(f"🔁 Transition: {label} -> {NETWORK_CONDITIONS[next_index]} (index {next_index})")
            current_index = next_index

    except KeyboardInterrupt:
        print("\n⚠️ Interrupted by user.")
    finally:
        print("\n🧹 Cleaning up (MULTIPLE mode)...")
        delete_shape(endpoint)
        force_stop_package(TARGET_PACKAGE)
        print("🏁 Simulation complete.")


# ==== ENTRYPOINT ====
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Automatic Network Condition Simulator")
    parser.add_argument("--ip", default=DEFAULT_IP, help=f"Target device IP address (default: {DEFAULT_IP})")
    parser.add_argument("--mode", choices=["single", "multiple"], default="single",
                        help="Choose simulation mode: 'single' for sample data, 'multiple' for 100-step random simulation")
    parser.add_argument("--state_duration", type=int, default=DEFAULT_STATE_DURATION,
                        help=f"Duration (seconds) per state (default: {DEFAULT_STATE_DURATION})")
    parser.add_argument("--total_states", type=int, default=DEFAULT_TOTAL_STATES,
                        help=f"Total number of states to simulate (default: {DEFAULT_TOTAL_STATES})")

    args = parser.parse_args()
    endpoint = f"{BASE_URL}{args.ip}/"

    if args.mode == "multiple":
        run_multiple_mode(endpoint, args.state_duration, args.total_states)
    else:
        run_single_mode(endpoint)
