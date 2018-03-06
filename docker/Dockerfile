FROM python:3.6.4-alpine3.7
MAINTAINER Frank Gu <499397328@qq.com>

RUN apk add --no-cache tzdata bash

COPY requirements.txt /usr/src

# 安装influxdb工具集1.4.3版本为了进行备份
ENV INFLUXDB_VERSION 1.4.3
RUN set -ex && \
    apk add --no-cache --virtual .build-deps wget gnupg tar ca-certificates py-pip python-dev && \
    update-ca-certificates && \
    pip install -r /usr/src/requirements.txt && \
    for key in \
        05CE15085FC09D18E99EFB22684A14CF2582E0C5 ; \
    do \
        gpg --keyserver ha.pool.sks-keyservers.net --recv-keys "$key" || \
        gpg --keyserver pgp.mit.edu --recv-keys "$key" || \
        gpg --keyserver keyserver.pgp.com --recv-keys "$key" ; \
    done && \
    wget --no-verbose https://dl.influxdata.com/influxdb/releases/influxdb-${INFLUXDB_VERSION}-static_linux_amd64.tar.gz.asc && \
    wget --no-verbose https://dl.influxdata.com/influxdb/releases/influxdb-${INFLUXDB_VERSION}-static_linux_amd64.tar.gz && \
    gpg --batch --verify influxdb-${INFLUXDB_VERSION}-static_linux_amd64.tar.gz.asc influxdb-${INFLUXDB_VERSION}-static_linux_amd64.tar.gz && \
    mkdir -p /usr/src && \
    tar -C /usr/src -xzf influxdb-${INFLUXDB_VERSION}-static_linux_amd64.tar.gz && \
    rm -f /usr/src/influxdb-*/influxdb.conf && \
    chmod +x /usr/src/influxdb-*/* && \
    cp -a /usr/src/influxdb-*/* /usr/bin/ && \
    rm -rf *.tar.gz* /usr/src /root/.gnupg && \
    apk del .build-deps

COPY entrypoint.sh /

WORKDIR /usr/src

COPY main.py /usr/src

VOLUME /var/lib/influxdb

ENTRYPOINT ["/entrypoint.sh"]
CMD ["main.py"]
