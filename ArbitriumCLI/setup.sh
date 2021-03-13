#!/bin/bash


printf "
    _         _     _ _        _                   ____      _  _____ 
   / \   _ __| |__ (_) |_ _ __(_)_   _ _ __ ___   |  _ \    / \|_   _|
  / _ \ |  __|  _ \| | __|  __| | | | |  _   _ \  | |_) |  / _ \ | |  
 / ___ \| |  | |_) | | |_| |  | | |_| | | | | | | |  _ <  / ___ \| |  
/_/   \_\_|  |_.__/|_|\__|_|  |_|\__,_|_| |_| |_| |_| \_\/_/   \_\_|  

"



if [[ $(id -u) -ne 0 ]] ; then echo "Please run as root" ; exit 1 ; fi


SCRIPTPATH="$( cd "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
cd $SCRIPTPATH




if [ "$1" == "" ]
then
    echo "No Dockerfile. Usage: run main.py to handle the setup or ./setup.sh abs_path_Dockerfile"
    exit 1
fi



if ! command -v docker &> /dev/null
then
    echo "[+] Docker installation ..."
	apt-get update
	apt-get install -y apt-transport-https ca-certificates curl gnupg-agent software-properties-common
	curl -fsSL https://download.docker.com/linux/ubuntu/gpg | apt-key add -
	add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable"
	apt-get update
	apt-get install -y docker-ce docker-ce-cli containerd.io
fi



if ! docker images 2>&1 | grep arbitrium-rat
then
	echo "[+] Building docker image ..."
	docker build -f "$1" -t benchaliah/arbitrium-rat .
	echo "[!] Installation finished"
	exit
else
	echo "[!] Already installed, use main.py if you wish to customize the existing image"
	exit 1
fi
