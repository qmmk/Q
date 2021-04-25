#!/bin/bash
iptables -C ADARCH_BAN -s $1 -j DROP > /dev/null 2>&1
if [ $? == 1 ]; then
	iptables -A ADARCH_BAN -s $1 -j DROP > /dev/null 2>&1
fi

