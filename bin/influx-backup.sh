#! /bin/bash

INFLUX_HOST=influxdb-01.cal.ci.spirentcom.com
BACKUP_DIR=~/tmp/dbbackup

mkdir -p $BACKUP_DIR
echo 'Backup Influx metadata'
influxd backup -host $INFLUX_HOST:8088 $BACKUP_DIR

#for db in `influx -host $INFLUX_HOST -execute "show databases" | egrep -v '(^name:|^name$|^\-|^_internal)'`
for db in `influx -host $INFLUX_HOST -format=json -execute "show databases" | jq -r '.results[].series[].values[][]' | egrep -v '(_internal)'`
do
    echo "Creating backup for $db"
    influxd backup -database $db -host $INFLUX_HOST:8088 $BACKUP_DIR
done
