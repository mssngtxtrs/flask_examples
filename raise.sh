#!/bin/sh

sudo systemctl start postgresql.service
sudo flask run -h 192.168.1.65 -p 80 --debug
