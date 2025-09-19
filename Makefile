PROJECT_DIR := /home/dangnp/workspace/tools/loss-simulator # change this

# atc var
ATC_DIR := augmented-traffic-control
ATC_UI_DIR := atcui
ATC_SCRIPT_DIR := scripts
ATC_SERVICE_DIR := services
ATC_SYSTEM_SCRIPT_DIR := /etc/atc
ATC_SYSTEM_SERVICE_DIR := /etc/systemd/system

ATC_PATH := $(PROJECT_DIR)/$(ATC_DIR)
ATC_UI_PATH := $(PROJECT_DIR)/$(ATC_DIR)/$(ATC_UI_DIR)
ATC_ENV_PATH := $(ATC_SYSTEM_SCRIPT_DIR)/atc.env
ATC_SCRIPT_PATH := $(ATC_PATH)/$(ATC_SCRIPT_DIR)
ATC_SERVICE_PATH := $(ATC_SCRIPT_PATH)/$(ATC_SERVICE_DIR)

ATC_DEFAULT_IP := 0.0.0.0
ATC_DEFAULT_PORT := 8080

ATC_LAN_INTERFACE := wlp4s0
ATC_WAN_INTERFACE := eno1

ATC_RESTART_SLEEP_TIME := 5
ATC_ATCD_BINARY := /usr/local/bin/atcd

# main project var
PYTHON3_BIN := /usr/bin/python3.12
PIP3_BIN := /usr/bin/pip3.12
PROJECT_DJANGO_PORT := 8000
PROJECT_FRONTEND_PORT := 5173

.PHONY: run stop logs clean restart atc-reboot atcd-log atcui-log

atc-reboot:
	@echo "[INFO] Writing atcd.env..."
	sudo mkdir -p $(ATC_SYSTEM_SCRIPT_DIR) 
	sudo rm -rf $(ATC_ENV_PATH)
	sudo touch $(ATC_ENV_PATH)
	echo "LAN_INTERFACE=$(ATC_LAN_INTERFACE)"        | sudo tee $(ATC_ENV_PATH) > /dev/null
	echo "WAN_INTERFACE=$(ATC_WAN_INTERFACE)"       | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "RESTART_SLEEP_TIME=$(ATC_RESTART_SLEEP_TIME)" | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "ATCD_BINARY=$(ATC_ATCD_BINARY)"           | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "ATC_PATH=$(ATC_PATH)"           | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "ATC_UI_PATH=$(ATC_UI_PATH)"           | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "DEFAULT_IP=$(ATC_DEFAULT_IP)"           | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	echo "DEFAULT_PORT=$(ATC_DEFAULT_PORT)"           | sudo tee -a $(ATC_ENV_PATH) > /dev/null
	sudo chmod 644 $(ATC_ENV_PATH)

	@echo "[INFO] Environment file written to $(ATC_ENV_PATH)"

	@echo "[INFO] Installing ATC services for auto-start on reboot..."
	sudo cp -f $(ATC_SCRIPT_PATH)/runatcd.sh $(ATC_SYSTEM_SCRIPT_DIR)
	sudo cp -f $(ATC_SCRIPT_PATH)/runatcui.sh $(ATC_SYSTEM_SCRIPT_DIR)
	sudo cp -f $(ATC_SERVICE_PATH)/atcd.service $(ATC_SYSTEM_SERVICE_DIR)
	sudo cp -f $(ATC_SERVICE_PATH)/atcui.service $(ATC_SYSTEM_SERVICE_DIR)
	sudo systemctl daemon-reload
	sudo systemctl enable atcd.service 
	sudo systemctl enable atcui.service
	sudo systemctl start atcd.service 
	sudo systemctl start atcui.service

atc-stop:
	sudo systemctl stop atcd.service 
	sudo systemctl stop atcui.service

atcd-log:
	@echo "[INFO] Showing logs for atcd.service..."
	sudo journalctl -u atcd.service -f

atcui-log:
	@echo "[INFO] Showing logs for atcui.service..."
	sudo journalctl -u atcui.service -f

run:
	@echo "[INFO] Starting project with Python=$(PYTHON3_BIN), Django port=$(PROJECT_DJANGO_PORT), Frontend port=$(PROJECT_FRONTEND_PORT)"
	PROJECT_DIR=$(PROJECT_DIR) \
	PYTHON_BIN=$(PYTHON3_BIN) \
	PIP_BIN=$(PIP3_BIN) \
	DJANGO_PORT=$(PROJECT_DJANGO_PORT) \
	FRONTEND_PORT=$(PROJECT_FRONTEND_PORT) \
	bash $(PROJECT_DIR)/run.sh

stop:
	@echo "[INFO] Stopping project on ports Django=$(PROJECT_DJANGO_PORT), Frontend=$(PROJECT_FRONTEND_PORT)"
	DJANGO_PORT=$(PROJECT_DJANGO_PORT) \
	FRONTEND_PORT=$(PROJECT_FRONTEND_PORT) \
	bash $(PROJECT_DIR)/stop.sh

logs:
	@echo "[INFO] Tailing logs..."
	@tail -f $(PROJECT_DIR)/django.log $(PROJECT_DIR)/frontend.log

clean:
	@echo "[INFO] Cleaning logs..."
	@rm -f $(PROJECT_DIR)/django.log $(PROJECT_DIR)/frontend.log

restart: stop run
