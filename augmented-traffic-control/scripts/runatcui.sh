#!/bin/bash

deactivate > /dev/null 2>&1
source "$ATC_PATH/isoEnv/bin/activate"

python2 $ATC_UI_PATH/manage.py runserver "$DEFAULT_IP:$DEFAULT_PORT"