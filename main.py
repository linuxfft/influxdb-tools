#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""InfluxDB backup/restore script using HTTP API and line-protocol format."""

import argparse
import subprocess
import logging
import sys
import signal
import tarfile
from typing import Optional,Any,Dict,List
from datetime import datetime
from multiprocessing import Process
import time
import os
from dateutil.tz import *

end: bool = False

t: Process = None

MIN_INTERVAL: float = 60.0

logger = logging.getLogger("influxdb-tools")
formatter = logging.Formatter('%(name)-12s %(asctime)s %(levelname)-4s %(message)s', '%a, %d %b %Y %H:%M:%S',)
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)
logger.setLevel(logging.INFO)


def compress(dir: str, ignore_suffix='gz'):
    file_name: str = "influx-backup_{0}.tar.gz".format(datetime.now(tz=tzlocal()))
    file_name = os.path.join(dir, file_name)
    with tarfile.open(file_name, mode='x:gz') as f_out:
        for dirpath, dirnames, filenames in os.walk(dir):
            fpath = dirpath.replace(dir, '')  # 这一句很重要，不replace的话，就从根目录开始复制
            fpath = fpath and fpath + os.sep or ''  # 这句话理解我也点郁闷，实现当前文件夹以及包含的所有文件的压缩
            for filename in filenames:
                if filename.find(ignore_suffix) >= 0:
                    continue
                file_path = os.path.join(dirpath, filename)
                f_out.add(file_path, arcname=filename)
                os.remove(file_path)
    print(u'压缩成功')


def dump(*args,  **kargs:Dict[str, Any]) -> None:
    """Create a backup."""
    _interval: float = float(kargs['interval'])
    while not end:
        _start = time.time()
        logger.info(u'开始备份数据库: ' + str(kargs['database']))
        cmd = "influxd backup -database {0} -host {1}:{2} -retention {3} {4}".format(kargs['database'],
                                                                                     kargs['host'], kargs['port'],
                                                                                     kargs['retention'], kargs["dir"])
        cmd_list = cmd.split(' ')
        p = subprocess.Popen(cmd, stdin=sys.stdin, stdout=sys.stdout, stderr=sys.stderr, shell=True)
        ret: int = p.wait()
        if ret == 0:
            logger.info(u'成功备份数据库: ' + str(kargs['database']))
        else:
            logger.error(u'备份数据库失败: ' + str(kargs['database']))
        compress(str(kargs['dir']))
        _diff = time.time() - _start
        _t = _interval - _diff
        if _t < MIN_INTERVAL:  # 小于0 或者 小于MIN_INTERVAL
            time.sleep(MIN_INTERVAL)  # MIN_INTERVAL to go
        else:
            time.sleep(_t)


def raise_keyboard_interrupt(signum, frame) -> None:
    global end
    end = True
    if t:
        os.kill(t.pid, signal.SIGKILL)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, raise_keyboard_interrupt)
    signal.signal(signal.SIGTERM, raise_keyboard_interrupt)

    parser = argparse.ArgumentParser(description='InfluxDB backup script')
    parser.add_argument('--host',  help='InfluxDB Host Name', default='localhost')
    parser.add_argument('--port',  help='InfluxDB Port', type=int, default=8088)
    parser.add_argument('--dir',  help='directory name for backup or restore form', default='/var/lib/influxdb/backup') # 如果不存在,influxd工具会自动生成
    parser.add_argument('--database', required=True, help='comma-separated list of database to dump/restore')
    parser.add_argument('--retention', help='retention to dump/restore', default='autogen')
    parser.add_argument('--interval', help='dump interval, unit:second', type=int, default=24 * 3600)  # 默认为one day
    args = parser.parse_args()

    t = Process(target=dump, kwargs=args.__dict__)
    t.start()

    t.join()  # 等待process停止,阻塞
    print("退出任务")
