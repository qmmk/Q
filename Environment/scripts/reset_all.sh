#!/bin/bash

sudo iptables -F
sudo iptables -F -t nat
sudo iptables -X
sudo iptables -X -t nat
sudo rm ./persistent/blacklist.txt
sudo rm ./persistent/log.txt
sudo rm ./persistent/endlessh.db

