#!/bin/bash

USERNAME="minecraft"
MINECRAFT_ROOT="/home/minecraft"
RAMDISK_SIZE="256m"
CONTROL_SCRIPT="/home/minecraft/minecraft.sh"


INSTANCE_NAME=$1
if [ -z "$INSTANCE_NAME" ]; then
    echo "ERROR: Must provide an instance name."
    exit 1
fi

INSTANCE_PORT=$2
if [ -z "$INSTANCE_PORT" ] ; then
    echo "ERROR: Must specifiy port number."
    exit 1
fi


SERVER_DOWNLOAD=$3
if [ -z "$SERVER_DOWNLOAD" ] ; then
    echo "ERROR: Must provide a server jar url."
    exit 1
fi

URL_VALID=`wget --spider -S "$SERVER_DOWNLOAD" 2>&1 | grep "HTTP/" | awk '{print $2}'`
if [[ -z "$URL_VALID" || "$URL_VALID" -ne "200" ]] ; then
    echo "ERROR: URL invalid."
    exit 1
fi

INSTANCE_ROOT=$MINECRAFT_ROOT/$INSTANCE_NAME
if [ -d "$INSTANCE_ROOT" ] ; then
    echo "ERROR: Instance directory already exists."
    exit 1
elif [ -L "/etc/init.d/$INSTANCE_NAME" ] ; then
    echo "ERROR: Symbolic link in /etc/init.d already exists."
    exit 1
fi

GID=`id $USERNAME | sed 's/^.*=//;s/(.*$//' ;`

as_user() {
    if [ "$USER" == "$USERNAME" ] ; then
        bash -c "$1"
    else
        sudo su - $USERNAME -c "$1"
    fi
}

echo "-> Creating directories..."
as_user "mkdir $INSTANCE_ROOT"
as_user "mkdir $INSTANCE_ROOT/{ramdisk,rdiff,tmp}"

echo "-> Appending fstab..."
NOW=$(date +"%Y-%b-%d-%H_%M_%S")
echo -e "\n## Created $NOW\ntmpfs   $INSTANCE_ROOT/ramdisk   tmpfs   defaults,user,nosuid,size=$RAMDISK_SIZE,mode=0770,uid=$UID,gid=$GID 0   0" | sudo tee -a /etc/fstab

echo "-> Mounting ramdisk..."
sudo mount $INSTANCE_ROOT/ramdisk

echo "-> Fetching server jar..."
as_user "wget -O $INSTANCE_ROOT/ramdisk/minecraft_server.jar $SERVER_DOWNLOAD"

echo "-> Creating service symbolic links..."
as_user "ln -s $CONTROL_SCRIPT $INSTANCE_ROOT/$INSTANCE_NAME.sh"
as_user "ln -s $INSTANCE_ROOT/ramdisk/minecraft_server.jar $INSTANCE_ROOT/ramdisk/$INSTANCE_NAME.jar"
sudo ln -s $INSTANCE_ROOT/$INSTANCE_NAME.sh /etc/init.d/$INSTANCE_NAME
sudo update-rc.d $INSTANCE_NAME defaults

echo "-> Setting port..."
echo "server-port=$INSTANCE_PORT" > $INSTANCE_ROOT/ramdisk/server.properties

echo "-> Starting service..."
service $INSTANCE_NAME start

echo "-> Initial rdiff..."
as_user "rdiff-backup $INSTANCE_ROOT/ramdisk $INSTANCE_ROOT/rdiff"

