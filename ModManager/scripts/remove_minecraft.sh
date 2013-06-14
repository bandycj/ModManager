#!/bin/bash

MINECRAFT_ROOT="/home/minecraft"

INSTANCE_NAME=$1
if [ -z "$1" ]; then
    echo "ERROR: Must provide an instance name."
    exit 1
fi

service $INSTANCE_NAME halt

INSTANCE_ROOT="$MINECRAFT_ROOT/$INSTANCE_NAME"
if [ -d "$INSTANCE_ROOT" ] ; then
    echo "-> Removing $INSTANCE_ROOT..."
    sudo umount $INSTANCE_ROOT/ramdisk
    sudo rm -rf $INSTANCE_ROOT
else
    echo "-> $INSTANCE_ROOT not found."
fi

echo "-> Uninstalling service..."
sudo update-rc.d -f $INSTANCE_NAME remove

SERVICE_LINK="/etc/init.d/$INSTANCE_NAME"
if [ -L "$SERVICE_LINK" ] ; then
    echo "-> Removing $SERVICE_LINK..."
    sudo rm $SERVICE_LINK
else
    echo "-> $SERVICE_LINK not found."
fi

sudo sed -i "/##/d" /etc/fstab
sudo sed -i "/$INSTANCE_NAME\/ramdisk/d" /etc/fstab

echo -e "\n\n-> Cleanup complete."
