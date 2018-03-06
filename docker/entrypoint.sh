#!/bin/bash

set -e

: ${HOST:=${INFLUX_HOST:='localhost'}}
: ${PORT:=${INFLUX_PORT:=8088}}
: ${DATABASE:=${DB_ENV_BACKUP_DATABASE:=${BACKUP_DATABASE:='telegraf'}}}
: ${DIR:=${DB_ENV_BACKUP_DIR:=${BACKUP_DIR:='/var/lib/influxdb/backup'}}}
: ${RETENTION:=${DB_ENV_RETENTION:=${BACKUP_RETENTION:='autogen'}}}
: ${INTERVAL:=${DB_ENV_INTERVAL:=${BACKUP_INTERVAL:='86400'}}}

DB_ARGS=()
function check_config() {
    param="$1"
    value="$2"
    if ! grep -q -E "^\s*\b${param}\b\s*=" "$INFLUX_RC" ; then
        DB_ARGS+=("--${param}")
        DB_ARGS+=("${value}")
   fi;
}
check_config "host" "$HOST"
check_config "port" "$PORT"
check_config "database" "$DATABASE"
check_config "dir" "$DIR"
check_config "retention" "$RETENTION"
check_config "interval" "$INTERVAL"

case "$1" in
    -- | main.py)
        shift
        if [[ "$1" == "scaffold" ]] ; then
            exec main.py "$@"
        else
            exec main.py "$@" "${DB_ARGS[@]}"
        fi
        ;;
    -*)
        exec main.py "$@" "${DB_ARGS[@]}"
        ;;
    *)
        exec "$@"
esac

exit 1