# README.md
## 1. Requirements:

- Download ZRTC Demo App at commit [dangnp/android/demoapp_record_inout_audio](http://zalogit2.zing.vn/voip_platform/core/zrtc_core/-/tree/def02a24ada4c8d123233d5be18815441658a62c)

- Clone whole project at [Master](https://github.com/dangnguyenphuc/packet-loss-simulator)

- Nodejs >= 21, python >= 3.12

## 2. How to run
	
### 2.1 ATC tool:
	
- Change dir to augmented-traffic-control folder (project cloned at github)
		
- Run file: runatc.sh (Optional: Change __LAN_INTERFACE__ and __WAN_INTERFACE__ inside this file)
	
- Check if run successfully: ```<IP>:8080```
		

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
- Go to Project most outside folder folder and run:
    ```bash
    ./run.sh # to run
    ./stop.sh # to stop
    ```
- Infomation:
    ```bash
    # ATC tool run on <IP>:8080
    # Django backend run on "localhost:8000"
    # Vue frontend run on "localhost:5173"
    ```