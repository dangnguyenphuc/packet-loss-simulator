import argparse
import json
import time
import requests
import sys

# ==== CONFIG ====
BASE_URL = "http://10.42.0.1:8080/api/v1/shape/"
DEFAULT_IP = "10.42.0.88"
MAX_RETRY = 3
STEP = 5
DELAY_BETWEEN_POSTS = 2  # seconds between POSTs

# ==== SAMPLE DATA ====
SAMPLE_DATA = {
    "down": {
        "rate": None,
        "loss": {"percentage": 0, "correlation": 0},
        "delay": {"delay": 0, "jitter": 0, "correlation": 0},
        "corruption": {"percentage": 0, "correlation": 0},
        "reorder": {"percentage": 0, "correlation": 0, "gap": 0},
        "iptables_options": []
    },
    "up": {
        "rate": None,
        "loss": {"percentage": 0, "correlation": 0},
        "delay": {"delay": 0, "jitter": 0, "correlation": 0},
        "corruption": {"percentage": 0, "correlation": 0},
        "reorder": {"percentage": 0, "correlation": 0, "gap": 0},
        "iptables_options": []
    }
}


def delete_shape(endpoint):
    """Try to delete the shape 3 times"""
    for attempt in range(3):
        try:
            response = requests.delete(endpoint)
            print(f"[DELETE {attempt+1}/3] Status: {response.status_code}")
            time.sleep(0.5)
        except Exception as e:
            print(f"[DELETE {attempt+1}/3] Error: {e}")


def post_shape(endpoint, data):
    """POST the shaping configuration"""
    headers = {"Content-Type": "application/json"}
    status_code = 0
    retry_time = MAX_RETRY

    while status_code // 200 != 1 and retry_time > 0:
        try:
            response = requests.post(endpoint, headers=headers, json=data)
            status_code = response.status_code
            print(f"[POST] Attempt: {MAX_RETRY - retry_time + 1}, Status: {status_code}")
            if status_code // 200 == 1:
                return True
        except Exception as e:
            print(f"[POST] Error: {e}")
        retry_time -= 1
        time.sleep(1)
    return False


def main(ip):
    endpoint = f"{BASE_URL}{ip}/"
    print(f"Target endpoint: {endpoint}")

    # Step 1: Delete current shape 3 times
    delete_shape(endpoint)

    # Step 2: Sweep loss percentage up and down
    loss_values = list(range(0, 81, STEP)) + list(range(75, -1, -STEP))
    print(f"Starting POST sequence with loss values: {loss_values}")

    try:
        for loss in loss_values:
            SAMPLE_DATA["down"]["loss"]["percentage"] = loss
            print(f"\n➡️  Setting down.loss.percentage = {loss}%")
            success = post_shape(endpoint, SAMPLE_DATA)
            if success:
                print(f"✅ Applied loss = {loss}% successfully")
            else:
                print(f"❌ Failed to apply loss = {loss}%")
            time.sleep(DELAY_BETWEEN_POSTS)

    except KeyboardInterrupt:
        print("\n⚠️  Interrupted by user (Ctrl+C). Cleaning up...")
        try:
            response = requests.delete(endpoint)
            print(f"[CLEANUP DELETE] Status: {response.status_code}")
        except Exception as e:
            print(f"[CLEANUP DELETE] Error: {e}")
        print("🛑 Exiting gracefully.")
        sys.exit(0)

    print("\n🎯 Sequence complete.")
    # Final cleanup delete (optional)
    delete_shape(endpoint)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Standalone ATC Shape tool (no Django)")
    parser.add_argument("--ip", default=DEFAULT_IP, help=f"Target device IP address (default: {DEFAULT_IP})")
    args = parser.parse_args()

    main(args.ip)

