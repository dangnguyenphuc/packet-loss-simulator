# README.md
## 1. Requirements:

- Download your own ZRTC version. For example my app at commit [dangnp/android/demoapp_record_inout_audio](https://www.youtube.com/watch?v=xvFZjo5PgG0)

- Clone whole project at [Master](https://github.com/dangnguyenphuc/packet-loss-simulator)

- Main Project requirements: Nodejs >= 21, Python >= 3.12

- Atc requirements: Python 2.7

## 2. How to run

### 2.0 Prerequisites

#### 2.0.1 Install python2:
- Install and build from source because it already deprecated

    ```
    cd </your/custom/path>
    wget https://www.python.org/ftp/python/2.7.18/Python-2.7.18.tgz
    tar xzf Python-2.7.18.tgz
    cd Python-2.7.18
    ```

- Go to ```Lib/test/regrtest.py``` file and search for "Run tests sequentially"
    - Should be return a line inside an ```else``` block, disable/remove that blockl

- Configure and build:

    ```
    ./configure --prefix=/usr/local/python2.7 --enable-optimizations
    make -j6 # build with 6 cores
    ```

- Export to use globally:

    ```
    sudo make install
    ```

- Install pip for python2:

    ```
    curl -O https://bootstrap.pypa.io/pip/2.7/get-pip.py
    sudo python2.7 get-pip.py
    ```
#### 2.0.2 Install atcd dependencies:
- Change to directory ```augmented-traffic-control```
- Run:
```
pip2.7 install -r requirement.txt           # just install locally
sudo pip2.7 install -r requirement.txt      # install globally to use atcd
```

#### 2.0.3 Change some python2 packages source code (superuser privilege):
- In your ```/usr/local/lib/python2.7/site-packages/thrift/server/TNonblockingServer.py```, might be there're some outdated libraries, or they just been renamed:
```python
import queue # error

# change to
import Queue as queue
```

- In your ```/usr/local/lib/python2.7/site-packages/atcd/backends/linux.py```, don't need to remove root QDisc anymore because it simply doesn't have any permission to do that and we already covered that case. Just need to comment these lines:

```python
    try:
        self.logger.info("deleting root QDisc on {0}".format(eth_name))
        self.ipr.tc(RTM_DELQDISC, None, eth_id, 0, parent=TC_H_ROOT)
    except Exception as e:
        # a (2, 'No such file or directory') can be thrown if there is
        # nothing to delete. Ignore such error, return the error otherwise
        if isinstance(e, NetlinkError) and e.code == 2:
            self.logger.warning(
                "could not delete root QDisc. There might "
                "have been nothing to delete")
        else:
            self.logger.exception(
                'Initializing root Qdisc for {0}'.format(eth_name)
            )
            raise
```

- ```/usr/local/lib/python2.7/dist-packages/thrift/protocol/TProtocol.py```, line 119. Just simply change to:

```python
def writeString(self, str_val):
    if isinstance(str_val, bytes):
        self.writeBinary(str_val)
    else:
        self.writeBinary(str(str_val).encode('utf-8'))
```
### 2.1 ATC tool:



- Change dir to augmented-traffic-control folder (project cloned at github)
		
- In Makefile, change these variables based on your needs:

    ```bash
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
- Read zalo docs utility for newcommers to get the real [config.env](lossSimulator/config.env) file
- Go to Project most outside folder
- In Makefile, change these variables based on your needs:

    ```bash
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
