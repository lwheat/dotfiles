#! /bin/bash

INFLUX_HOST=influxdb-01.cal.ci.spirentcom.com
BACKUP_DIR=~/tmp/dbbackup
LOCAL_INFLUX_DIR=/usr/local/var/influxdb

if [ ! -d $BACKUP_DIR ]; then
    echo "no backup directory"
    exit 1
fi

echo 'Restore Influx metadata'
influxd restore -metadir ${LOCAL_INFLUX_DIR}/meta $BACKUP_DIR


#for db in `influx -host $INFLUX_HOST -execute "show databases" | egrep -v '(^name:|^name$|^\-|^_internal)'`
for db in `influx -host $INFLUX_HOST -format=json -execute "show databases" | jq -r '.results[].series[].values[][]' | egrep -v '(_internal)'`
do
  echo "Restoring backup for $db"
  influxd restore  -database $db -datadir ${LOCAL_INFLUX_DIR}/data $BACKUP_DIR
done
