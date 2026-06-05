# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Project Does

A network condition simulator and test harness for evaluating Android voice/audio apps (ZRTC demo) under degraded network conditions (packet loss, latency, bandwidth throttling). It combines:
- **Facebook ATC** for kernel-level traffic shaping
- **Django REST backend** for orchestrating Android device control via ADB
- **Vue 3 frontend** for test configuration and result visualization
- **NISQA / PLCMOS** models for audio quality scoring

## Sensitive Files — Do Not Read or Output

Never read, display, or include the contents of these files in any response:
- Any `.env`, `.env.*`, `*.env`, `config.env` files
- Any `settings.py`, `settings_local.py`, `local_settings.py` files
- Any file that may contain secrets, credentials, API keys, or tokens

If a task requires inspecting one of these files, ask the user to share only the relevant non-sensitive keys.

## Running the Project

> Linux only. Requires Python 3.12+, Node.js 21+, ADB installed, and ATC daemon running.

### Single-port mode (recommended for deployment)

The Vue app is built as static files and served directly by Django on port 8000.

```bash
# Build Vue → Django static, then start Django only
make run-single

# Stop
make stop

# Tail logs
make logs
```

Open `http://localhost:8000` — Django serves the Vue SPA and all API endpoints.

### Auto-rebuild on Vue changes (while Django runs)

```bash
# In a separate terminal — watches src/ and rebuilds on change
make watch-frontend
```

### Dev mode (Django + Vite hot-reload on separate ports)

```bash
# Start both Django (:8000) and Vite dev server (:5173)
make run

# Stop all services
make stop

# Tail logs
make logs
```

Frontend dev server: `http://localhost:5173` — Backend: `http://localhost:8000`

Vite proxies `/api/*` to Django in dev mode, so the hardcoded `:8000` address is no longer needed in the frontend code.

### Manual

```bash
# Django only
cd lossSimulator && source ../venv/bin/activate && python manage.py runserver 0.0.0.0:8000

# Frontend dev only
cd frontend/loss-simulator && npm install && npm run dev

# Build frontend once
cd frontend/loss-simulator && npm run build
```

## Configuration

| File | What to edit |
|------|-------------|
| `lossSimulator/config.env` | GitLab credentials, NDK path, JVM path, app source path, target branch |
| `Makefile` | `PYTHON3_BIN`, `PIP3_BIN`, ports (`PROJECT_DJANGO_PORT`, `PROJECT_FRONTEND_PORT`), ATC network interfaces (`ATC_LAN_INTERFACE`, `ATC_WAN_INTERFACE`) |
| `lossSimulator/utils/constants.py` | ATC gateway IP/subnet, Android package names, test timeout defaults |

Key constants in `constants.py`:
- `NETWORK_ATC_GATEWAY_IP = "http://10.42.0.1:8080"` — must match ATC daemon host
- `PACKAGE = "com.vng.zing.vn.zrtc.demo"` — target Android package
- `DEFAULT_EVAL_TIMEOUT = 30` / `DEFAULT_AUDIO_DURATION = 20` — test timing

## Architecture

```
Browser
  │ Single port (:8000)
  ▼
Django Backend (8000)
  ├── main/views/
  │    ├── device_views.py  — device list, IP, info endpoints
  │    ├── task_views.py    — task run/poll/stop (queue-based)
  │    ├── file_views.py    — file delete, stats
  │    └── spa_view.py      — serves built Vue index.html
  ├── main/services/
  │    ├── task_store.py    — shared Manager().dict() for myCache & tasks
  │    └── task_runner.py   — runApp, buildApp, queue worker thread
  ├── proxy/views.py        — transparent proxy to ATC API at :8080
  └── utils/
       ├── utils.py         — AdbUtils, AudioUtils, FileUtils, StatUtils, RequestUtils
       ├── android.py       — AndroidAppController (uiautomator2 UI automation)
       ├── plc_mos.py       — PLCMOS quality estimation
       └── constants.py
       │
       ├── ADB → Android device (push audio, launch app, pull recordings)
       ├── ATC daemon (:8080) → kernel traffic shaping (tc/netem)
       └── NISQA/PLCMOS → MOS score from recorded audio

Vue 3 Frontend (built static files at lossSimulator/static/vue/)
  └── Dev mode only: Vite dev server (:5173) with proxy → Django (:8000)
```

### Core Data Flow

1. **Test start** (`POST /api/devices/{id}/run`): Request is placed in a `queue.Queue`. Returns `202 queued` with a task ID immediately. A background worker thread processes one task at a time.
2. **Queue worker**: Takes one task at a time → spawns `runApp` process (ADB automation) → waits for startup → spawns `StatUtils.getStat` process → waits for both to finish → picks next task.
3. **runApp()**: Pushes reference audio → starts ZRTC demo via uiautomator2 → applies ATC network shape → records output audio → runs NISQA/PLCMOS scoring → writes JSON results to `static/audio/[test_folder]/`.
4. **Task polling** (`GET /api/tasks/{id}`): Frontend polls every 10 seconds. Status: `queued → running → done/failed`. Results cache in a `Manager().dict()` and auto-expire after 71 seconds.
5. **Network shaping**: Frontend sends ATC profile → `proxy/views.py` forwards to ATC API → kernel applies `tc qdisc` rules on the configured interface.

### No Automated Tests

There is no test suite. Manual testing is done through the web UI. The `utils/test.py` file exists but is minimal.

### Frontend State

Vue 3 Composition API with no Vuex/Pinia — all state is local to `src/pages/MainPage.vue`. Network profile JSON files live in `lossSimulator/static/json/` and are editable via the in-app JSON editor.

### DRED / Autorun

`atc-sim.py` runs standalone network profile sequences for DRED (audio redundancy) experiments. The Makefile `autorun` target loops through predefined network condition arrays.
