#!/bin/bash

/usr/local/bin/file_checker.sh &
nginx -g 'daemon off;' &
exec gohttpserver -a 127.0.0.1:8080 -r /app/public
