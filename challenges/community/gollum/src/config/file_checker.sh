#!/bin/bash

cd /app/public/
m=0

while :; do # give flag if my precious file is really gone 😟
    [[ -f my_precious.gif ]] && m=0 || { ((++m>=3)) && echo "$FLAG" > flag.txt; }
    sleep 1
done
