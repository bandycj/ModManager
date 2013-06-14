#!/bin/bash
# /etc/init.d/minecraft

### BEGIN INIT INFO
# Provides:	minecraft
# Required-Start: $local_fs $remote_fs
# Required-Stop:	$local_fs $remote_fs
# Should-Start:	$network
# Should-Stop:		$network
# Default-Start:	2 3 4 5
# Default-Stop:	0 1 6
# Short-Description:		Minecraft server
# Description:		Starts the minecraft server
### END INIT INFO

#Settings
BASEDIR=`basename $0 .sh`
SERVICE="$BASEDIR.jar"
STOP_COMMAND="stop"
USERNAME="minecraft"
MCPATH="/home/minecraft/$BASEDIR/ramdisk"
INVOCATION="java -d64 -server -Xincgc -Xmx6G -Xms2G -Xmn512M -Djava.awt.headless=true -XX:UseSSE=3 -XX:ParallelGCThreads=4 -XX:+AggressiveOpts -XX:+UseLargePages -XX:LargePageSizeInBytes=2m -jar $SERVICE nogui"
BACKUPPATH="/home/minecraft/Dropbox/minecraft"
RDIFF_DEST="/home/minecraft/${BASEDIR}/rdiff"
WWW_ROOT="/var/www/selurgniman.org/${BASEDIR}"
STANDARD_PAUSE=10


ME=`whoami`
as_user() {
	if [ "$ME" == "$USERNAME" ] ; then
		bash -c "$1"
	else
		sudo su - $USERNAME -c "$1"
	fi
}

mc_command(){
	as_user "screen -p 0 -S $SERVICE -X eval 'stuff \"$1\"\015'"
}

mc_start() {
	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "Tried to start but $SERVICE was already running!"
	else
		echo "$SERVICE was not running... starting."
		cd $MCPATH
		if [ ! -f "$MCPATH/$SERVICE" ]
		then 
			echo "Ram drive empty...	prepping."
			#as_user "cp -R $MCSTORE/* $MCPATH/"
			mc_rollback
		fi
		as_user "cd $MCPATH && screen -dmS $SERVICE $INVOCATION"
		sleep $STANDARD_PAUSE
		if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
		then
			echo "$SERVICE is now running."
		else
			echo "Could not start $SERVICE."
		fi
	fi
}

mc_saveoff() {
	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "$SERVICE is running... suspending saves"
		mc_command "save-off"
		mc_command "save-all"
		sync
		sleep $STANDARD_PAUSE
	else
		echo "$SERVICE was not running. Not suspending saves."
	fi
}

mc_saveon() {
	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "$SERVICE is running... re-enabling saves"
		mc_command "save-on"
	else
		echo "$SERVICE was not running. Not resuming saves."
	fi
}

mc_stop() {
	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "$SERVICE is running... stopping."
		mc_command "say SERVER SHUTTING DOWN IN $STANDARD_PAUSE SECONDS. Saving map..."
        mc_saveoff
		mc_command $STOP_COMMAND
        sleep $STANDARD_PAUSE
	else
		echo "$SERVICE was not running."
	fi
	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "$SERVICE could not be shut down... still running."
	else
		echo "$SERVICE is shut down."
	fi
}

mc_backup() {
  if [ -f $MCPATH/$SERVICE ]
	then
		NOW=$(date +"%Y-%b-%d-%H_%M_%S")
		ARCHIVE="$SERVICE-backup-$NOW.tar.bz2"
        echo "Cleaning up old backups"
		echo "Backing up minecraft files"
		mc_saveoff
    
		as_user "find \"$BACKUPPATH\" -name $SERVICE*.bz2 -mtime +10 -exec rm {} \;"
		as_user "tar -cvpijf $BACKUPPATH/$ARCHIVE $MCPATH"
    
        mc_saveon
		echo `date +"%b-%d-%y %H:%M"` > $WWW_ROOT/last_backup_$SERVICE.txt
	
		echo "Backup complete."
	else 
		echo "Minecraft isn't loaded to the ram-disk..."
  fi
}

mc_rdiff() {
	if [ -f $MCPATH/$SERVICE ]
	then
		echo "Peforming rdiff backup..."
		as_user "rdiff-backup --remove-older-than 720m --force $RDIFF_DEST"
		as_user "rdiff-backup --exclude-regexp '.*lo?[ck|g]$' $MCPATH $RDIFF_DEST"
		echo `date +"%b-%d-%y %H:%M"` > $WWW_ROOT/last_rdiff.txt
		echo "rdiff complete."
	else
		echo "Minecraft isn't loaded to the ram-disk..."
	fi
}

mc_rollback() {	
	mc_stop
  echo "Restoring an incremental backup..."
	if [ "$3" == "" ]; then
		as_user "rdiff-backup --force --restore-as-of now $RDIFF_DEST $MCPATH/"
	else
		as_user "rdiff-backup --force --restore-as-of $3 $RDIFF_DEST $MCPATH/"
	fi
	echo "Restore complete."
}

mc_disksaverun() {

	if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
	then
		echo "Saving ramdrive to disk."
		if [ ! -f $MCPATH/$SERVICE ]
		then
			echo "Error.. Minecraft not in ram"
		else
			mc_saveoff
			mc_rdiff
			mc_saveon
		fi
	else
		echo "Service is not running"
	fi
}

mc_disksavehalt() {
	echo "Saving ramdrive to disk."
	if [ ! -f $MCPATH/$SERVICE ]
	then 
		echo "Error.. Minecraft not in ram"
	else
		echo "Saving, screen session closed"
		mc_rdiff
		as_user "rm -rf $MCPATH/*"
	fi
}




#Start-Stop here
case "$1" in
	start)
		mc_start
		;;
	stop)
		mc_stop
		mc_disksavehalt
		;;
	restart)
		mc_stop
		mc_disksavehalt
		mc_start
		;;
	backup)
		mc_disksaverun
		mc_backup
		;;
    rdiff)
        mc_disksaverun
        mc_rdiff
        ;;
	rollback)
		mc_stop
		mc_rollback
		mc_start
		;;
	disksavehalt)
		mc_disksavehalt
		;;
	disksaverun)
		mc_disksaverun
		;;
  halt)
    mc_stop
    ;;
	command)
		COMMAND=""
		args=$@
	        for i in "$@"
        	do
		        if [[ ! $i =~ command ]] 
			then
				if [[ $COMMAND == "" ]]
				then
					COMMAND="$i"
				else
					COMMAND="$COMMAND $i"
				fi
			fi
	        done

		mc_command "$COMMAND" 
		;;
	status)
		if ps ax | grep -v grep | grep -v -i SCREEN | grep $SERVICE > /dev/null
		then
			echo "$SERVICE is running."
		else
			echo "$SERVICE is not running."
		fi
		;;

	*)
	echo "Usage: /etc/init.d/minecraft {start|stop|update|backup|status|restart|disksaverun}"
	exit 1
	;;
esac

exit 0
