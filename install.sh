#!/bin/bash
if [ "$(id -u)" -ne 0 ]; then
        echo 'This script must be run by root' >&2
        exit 1
fi

cp -R src/ /opt/website_monitor
cp service_file.sh /etc/init.d/website_monitor
chmod +x /etc/init.d/website_monitor
update-rc.d website_monitor defaults
service website_monitor restart
