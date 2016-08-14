#!/bin/bash

sudo apt-get install python3-venv

if [ ! -e "config.py" ]; then
	cp config_example.py config.py
fi

if [ ! -d "venv" ]; then
	python3 -m venv venv
	. venv/bin/activate
		pip install git+https://github.com/Rapptz/discord.py.git@async
		pip install git+https://github.com/slackhq/python-slackclient.git
	deactivate
fi
