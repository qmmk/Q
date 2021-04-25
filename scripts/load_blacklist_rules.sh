#!/bin/bash

# Create chains
iptables -N ADARCH_BAN -t filter > /dev/null 2>&1
iptables -N ADARCH_EXCEPTION -t filter > /dev/null 2>&1
iptables -N ADARCH -t nat > /dev/null 2>&1

# Added as first rule: check chain ADARCH_EXCEPTION --> i.e. firstly check for particular rules (exceptions to BAN rules)
iptables -C INPUT -j ADARCH_EXCEPTION > /dev/null 2>&1
if [ $? == 1 ]; then
		iptables -I INPUT -j ADARCH_EXCEPTION
fi

# ...then go to check ADARCH_BAN chain
iptables -C INPUT -j ADARCH_BAN > /dev/null 2>&1
if [ $? == 1 ]; then
		iptables -A INPUT -j ADARCH_BAN
fi

# ...in order to not mess with existing prerouting rules, we redirect to custom chain "ADARCH"
iptables -t nat -C PREROUTING -j ADARCH > /dev/null 2>&1
if [ $? == 1 ]; then
		iptables -t nat -A PREROUTING -j ADARCH
fi

# add banning rules for blacklisted IPs
for IP in $(cat $1)
do 
	iptables -C ADARCH_BAN -s $IP -j DROP > /dev/null 2>&1

	if [ $? == 1 ]; then
		iptables -A ADARCH_BAN -s $IP -j DROP > /dev/null 2>&1
	fi
done

