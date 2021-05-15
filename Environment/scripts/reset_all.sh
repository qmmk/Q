#!/bin/bash

sudo iptables -F
sudo iptables -F -t nat
sudo iptables -X
sudo iptables -X -t nat
sudo rm ./Environment/persistent/blacklist.txt
sudo rm ./Environment/persistent/log.txt
sudo rm ./Environment/persistent/endlessh.db


