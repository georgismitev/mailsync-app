#!/usr/bin/env bash
set -e
file_exists() {
    [ -f "$1" ]
}

command_exists() {
    type "$1" &> /dev/null ;
}

VERSION=1.1.3
DISTRO=
UBUNTU=0
PYTHON=python
VERBOSE=0

# Set variables for the installation
mailsync_install_dir="/usr/local/mailsync"

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

if file_exists  "/etc/lsb-release"; then
    if cat /etc/lsb-release | grep "buntu" >> /dev/null; then
        UBUNTU=1
    fi
fi 

echo "***  Installing Mailsync $VERSION ..."

    # Install Mailsync
    if [ "$DISTRO" == "debian" ]; then
        # Skip installing python and gcc if they are already installed.
        if dpkg-query -s python-dev python-setuptools libmysqlclient-dev libpq-dev libsqlite3-0 libsqlite3-dev sqlite3 gcc >> /dev/null ; then
            echo "*** Mailsync requirements already satisfied"
        else
            echo "** Installing Mailsync dependencies"
            sudo apt-get -y install python-dev python-setuptools libmysqlclient-dev libpq-dev libsqlite3-0 libsqlite3-dev sqlite3 gcc
        fi

        if dpkg-query -W python-dev python-setuptools libmysqlclient-dev libpq-dev gcc libsqlite3-0 libsqlite3-dev sqlite3 ; then 
            echo "** Mailsync dependencies successfully installed!"
        fi
    elif [ "$DISTRO" == "rpm" ]; then
        if rpm --quiet -q gcc python-devel python-setuptools mysql-devel postgresql-devel sqlite sqlite-devel ; then
            echo "*** Mailsync requirements already satisfied"
        else 
            echo "** Installing Mailsync dependencies"
            sudo yum -t -y install gcc python-devel python-setuptools mysql-devel postgresql-devel sqlite sqlite-devel
        fi

        if rpm --quiet -q gcc python-devel python-setuptools mysql-devel postgresql-devel sqlite sqlite-devel ; then 
            echo "** Mailsync dependencies successfully installed!"
        fi
    fi
	
	sudo cp contrib/mailsync.conf /etc/mailsync.conf

	sudo cp contrib/mailsync /usr/bin/mailsync
	
	# make it executable
	sudo chmod +x /usr/bin/mailsync

    sudo $PYTHON setup.py install

	# Create a directory for the log files
	sudo mkdir -p "$mailsync_install_dir"

    # Show a message about where to go for help.
	print_instructions() {
        echo "Thank you for installing Mailsync!"
		echo "Now you can open http://127.0.0.1:4321 and enjoy Mailsync!"
	}

    # All done, let's start it 

    # If the web application is running - restart it 
    if  pgrep -x mailsync > /dev/null; then
        sudo mailsync restart
    else
        sudo mailsync start
    fi
  
    print_instructions