# README.md
## 1. Requirements:

- Download ZRTC Demo App at commit [dangnp/android/demoapp_record_inout_audio](https://www.youtube.com/watch?v=xvFZjo5PgG0)

- Clone whole project at [Master](https://github.com/dangnguyenphuc/packet-loss-simulator)

- Main Project requirements: Nodejs >= 21, Python >= 3.12

- Atc requirements: Python 2.7

## 2. How to run

### 2.0 Install Python

- Install pyenv:

```bash
curl -fsSL https://pyenv.run | bash 	# Linux based OS
brew install pyenv 						# MacOS
```

- Set up global install specific python version:

```bash
# Example
pyenv install 3.8.6
pyenv install 3.13
pyenv install 2.7
```

- Set global and local python version:

```bash
pyenv global 3.13 						# for all directory
pyenv local 3.8							# apply python3.8 for current folder
```
### 2.1 ATC tool:

- Change dir to augmented-traffic-control folder (project cloned at github)
		
- In Makefile, change these variables based on your needs:

```bash
PROJECT_DIR :=
ATC_DEFAULT_IP := 
ATC_DEFAULT_PORT :=
ATC_ATCD_BINARY := # (use "which atcd" to determine its path)
ATC_LAN_INTERFACE :=
ATC_WAN_INTERFACE :=
```
- Run:
```bash
make atc-reboot # to start and enable those services run on start
make atc-stop # to stop those services
make atcd-log # watch atcd.service jornal log
make atcui-log # watch atcui.service jornal log
```

### 2.2 Auto-test tool:
	
#### 2.2.1 Manual run:

+ Django:
	- Go to Project most outside folder that contains ```venv``` folder
	- Activate venv environment by:
    
    ```bash
    source venv/bin/activate
    ```
    - Go to ```lossSimulator/lossSimulator``` folder:
    ```bash
    python manage.py migrate
    python manage.py runserver 0.0.0.0:8000
    ```

+ Vue:
    - Go to Project most outside folder that contains ```frontend``` folder
    - Go to:
    ```bash
    cd frontend/loss-simulator/
    ```
    - Install packages:
    ```bash
    npm i
    ```
    - Run:
    ```bash 
    npm run dev
    ```
#### 2.2.2 Auto run:
- Note: Linux based only
- Go to Project most outside folder
- In Makefile, change these variables based on your needs:

```bash
PROJECT_DIR :=
PYTHON3_BIN := 
PIP3_BIN :=
PROJECT_DJANGO_PORT := 
PROJECT_FRONTEND_PORT :=
```
- Run:
```bash
make run   # start run back & frontend
make stop  # stop both back & frontend
make logs  # watch both back & frontend logs
make clean # clear logs
```
