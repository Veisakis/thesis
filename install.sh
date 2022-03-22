#!/bin/bash

apt update && apt install curl python3-pip figlet
pip3 install -r requirements

python3 src/main.py
