#!/usr/bin/env bash

file_exists() {
	[ -f "$1" ]
}

command_exists() {
    type "$1" &> /dev/null ;
}

set +e # Don"t exit the script if some command fails
DISTRO=

# Debian based distros - Tested and supported on : Debian, Ubuntu
if file_exists /etc/debian_version ; then
    DISTRO="debian"
# RPM based distros - Tested and supported on : Fedora, CentOS, Amazon Linux AMI
elif file_exists /etc/redhat-release ; then
    DISTRO="rpm"
elif file_exists /etc/system-release ; then
    DISTRO="rpm"
else 
    echo "Your operating system is not supported at the moment"
    exit
fi

site_packages=`python -c "from distutils.sysconfig import get_python_lib; print get_python_lib()"`
mailsync_dir="/usr/local/mailsync"

sudo rm -rf "$site_packages/mailsync*"
sudo rm -rf "$site_packages/tornado*"
sudo rm -rf "$site_packages/jinja2*"
sudo rm -rf "$site_packages/formencode*"
sudo rm -rf "$site_packages/createsend*"
sudo rm -rf "$site_packages/mailsnake*"
sudo rm -rf "$site_packages/SQLAlchemy*"
sudo rm -rf "$site_packages/pip"
sudo rm -rf "$site_packages/pytz"

echo "** Dependencies succesfully removed."

# Delete the binary
if [ -e /usr/bin/mailsync ]; then
	sudo mailsync stop
	sudo rm /usr/bin/mailsync
	echo "** Mailsync succesfully removed."
fi

# Delete the config file
sudo rm /etc/mailsync.conf
echo "** Config file succesfully removed."

# Remove the directory
if [ -d "$mailsync_dir" ]; then
	sudo rm -rf "$mailsync_dir"
	echo "** Directory succesfully removed."
fi

# Remove Mailsync from the startup list
if [ "$DISTRO" == "debian" ]; then
    sudo update-rc.d -f mailsync remove
elif [ "$DISTRO" == "rpm" ]; then
    chkconfig --del mailsync
fi