# Packet Loss Simulator

A network condition simulator and test harness for evaluating Android voice/audio apps (ZRTC demo) under degraded network conditions (packet loss, latency, bandwidth throttling).

**Stack:** Facebook ATC (traffic shaping) · Django REST backend · Vue 3 frontend · NISQA / PLCMOS audio quality scoring

---

## Requirements

- Linux only
- Python 3.12+, Node.js 21+, ADB installed
- ATC daemon running (see [ATC setup](#1-atc-setup))
- A ZRTC demo APK — see [dangnp/android/demoapp_record_inout_audio](https://github.com/dangnguyenphuc/packet-loss-simulator)

---

## 1. ATC Setup

### 1.1 Install Python 2.7 (required by ATC daemon)

Build from source (Python 2.7 is EOL and not in package managers):

```bash
cd </your/custom/path>
wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
tar xzf Python-2.7.18.tgz
cd Python-2.7.18
./configure --prefix=/usr/local/python2.7 --enable-optimizations
make -j$(nproc)
sudo make install
```

Install pip for Python 2.7:

```bash
curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py
sudo python2.7 get-pip.py
```

### 1.2 Install ATC dependencies

```bash
cd augmented-traffic-control
pip2.7 install -r requirement.txt           # local
sudo pip2.7 install -r requirement.txt      # global (needed for atcd)
```

### 1.3 Patch Python 2 packages

**`/usr/local/lib/python2.7/site-packages/thrift/server/TNonblockingServer.py`** — fix renamed module:

```python
# Before
import queue
# After
import Queue as queue
```

**`/usr/local/lib/python2.7/site-packages/atcd/backends/linux.py`** — comment out the root QDisc deletion block (no permission and already handled):

```python
# try:
#     self.logger.info("deleting root QDisc on {0}".format(eth_name))
#     self.ipr.tc(RTM_DELQDISC, None, eth_id, 0, parent=TC_H_ROOT)
# except Exception as e:
#     ...
```

**`/usr/local/lib/python2.7/dist-packages/thrift/protocol/TProtocol.py`**, line 119 — fix string encoding:

```python
def writeString(self, str_val):
    if isinstance(str_val, bytes):
        self.writeBinary(str_val)
    else:
        self.writeBinary(str(str_val).encode('utf-8'))
```

### 1.4 Configure and start ATC

Edit the Makefile variables in `augmented-traffic-control/Makefile`:

```makefile
ATC_DEFAULT_IP   :=       # bind address (e.g. 0.0.0.0)
ATC_DEFAULT_PORT :=       # default 8080
ATC_ATCD_BINARY  :=       # path from `which atcd`
ATC_LAN_INTERFACE :=      # e.g. wlp4s0
ATC_WAN_INTERFACE :=      # e.g. eno1
```

Then run from the repo root:

```bash
make atc-reboot    # install systemd services and start ATC
make atc-stop      # stop ATC services
make atcd-log      # tail atcd.service journal
make atcui-log     # tail atcui.service journal
```

---

## 2. Auto-Test Tool

### 2.1 Configuration

| File | What to edit |
|------|-------------|
| `lossSimulator/config.env` | GitLab credentials, NDK path, JVM path, app source path, target branch |
| `Makefile` | `PYTHON3_BIN`, `PIP3_BIN`, `PROJECT_DJANGO_PORT`, `ATC_LAN_INTERFACE`, `ATC_WAN_INTERFACE` |
| `lossSimulator/utils/constants.py` | ATC gateway IP/subnet, Android package names, test timeouts |

Key constants in `constants.py`:

```python
NETWORK_ATC_GATEWAY_IP = "http://10.42.0.1:8080"  # must match ATC daemon host
PACKAGE = "com.vng.zing.vn.zrtc.demo"              # target Android package
DEFAULT_EVAL_TIMEOUT  = 30
DEFAULT_AUDIO_DURATION = 20
```

### 2.2 Single-port mode (recommended)

The Vue app is built as static files and served by Django on port 8000 — only one port needed.

```bash
make run-single    # build Vue → install deps → start Django on :8000
make stop          # stop Django
make logs          # tail django.log
```

Open `http://localhost:8000` — Django serves both the Vue SPA and all API endpoints.

**Auto-rebuild Vue on change** (while Django is already running):

```bash
# In a separate terminal
make watch-frontend
```

### 2.3 Dev mode (hot-reload)

Runs Django on `:8000` and Vite dev server on `:5173` simultaneously. Vite proxies `/api/*` to Django.

```bash
make run       # start Django + Vite dev server
make stop      # stop both
make logs      # tail both logs
make clean     # delete log files
```

Open `http://localhost:5173` for the frontend with hot-reload.

### 2.4 Manual run

```bash
# Django only
cd lossSimulator
source ../venv/bin/activate
python manage.py runserver 0.0.0.0:8000

# Frontend dev only
cd frontend/loss-simulator
npm install
npm run dev

# Build frontend once
cd frontend/loss-simulator
npm run build
```

---

## Architecture

```
Browser
  │  Single port (:8000)
  ▼
Django Backend (:8000)
  ├── main/views/
  │    ├── device_views.py  — device list, IP, info endpoints
  │    ├── task_views.py    — task run/poll/stop (queue-based)
  │    ├── file_views.py    — file delete, stats
  │    └── spa_view.py      — serves built Vue index.html
  ├── main/services/
  │    ├── task_store.py    — shared Manager().dict() for myCache & tasks
  │    └── task_runner.py   — run_app, build_app, queue worker thread
  ├── proxy/views.py        — transparent proxy to ATC API at :8080
  └── utils/
       ├── utils.py         — AdbUtils, AudioUtils, FileUtils, StatUtils, AtcClient
       ├── android.py       — AndroidAppController (uiautomator2 UI automation)
       ├── plc_mos.py       — PLCMOS quality estimation
       └── constants.py
       │
       ├── ADB → Android device (push audio, launch app, pull recordings)
       ├── ATC daemon (:8080) → kernel traffic shaping (tc/netem)
       └── NISQA/PLCMOS → MOS score from recorded audio

Vue 3 Frontend (static files at lossSimulator/static/vue/)
  └── Dev mode only: Vite dev server (:5173) with proxy → Django (:8000)
```

### Core Data Flow

1. **Test start** (`POST /api/devices/{id}/run`): placed in a `queue.Queue`, returns `202 queued` with a task ID immediately.
2. **Queue worker**: background daemon thread processes one task at a time → spawns `run_app` process → waits for start event → spawns `get_stat` process → joins both → picks next.
3. **run_app()**: pushes reference audio → starts ZRTC demo via uiautomator2 → applies ATC network shape → records output audio → runs NISQA/PLCMOS scoring → writes JSON results to `static/audio/[test_folder]/`.
4. **Task polling** (`GET /api/tasks/{id}`): frontend polls every 10 s. Status transitions: `queued → running → done/failed`. Results cached in a `Manager().dict()` and auto-expire after 71 s.
5. **Network shaping**: frontend sends ATC profile → `proxy/views.py` forwards to ATC daemon → kernel applies `tc qdisc` rules.
