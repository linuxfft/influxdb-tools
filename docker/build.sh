#!/bin/bash

set -e
BUILD_PATH=`pwd`

cp ../main.py ./

docker build -f ./Dockerfile -t gubinempower/influxdb-tools .

docker tag gubinempower/influxdb-tools gubinempower/influxdb-tools:0.0.1

docker push gubinempower/influxdb-tools

docker push gubinempower/influxdb-tools:0.0.1

exit 0