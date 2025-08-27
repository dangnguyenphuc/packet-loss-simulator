#!/bin/bash
source isoEnv/bin/activate

sudo atcd --atcd-lan wlp4s0 --atcd-wan eno1 --atcd-mode unsecure --daemon

cd atcui

nohup python manage.py runserver 0.0.0.0:8080 > /dev/null 2>&1 &
