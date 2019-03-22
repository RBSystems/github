#! /bin/sh

echo -e "\033[30;32m"

echo ""

echo "********** Welcome ***********"

echo "Running initialization.sh for system status"

echo p>

echo "Hostname:"

hostname

echop>

echo "Username:"

whoami

echop>

echo "System time:"

date

echop>

echo "System running time and load:"

uptime

echop>

echo "Disk usage:"

df -H

echop>

echo "Memeory usage:"

free -g

echop>

echo "Recent 10 login:"

last -10

echo p>

echo "All logged in users:"

w

echop>

echo ""

echo -e "\033[0m"
