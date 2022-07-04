#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    server初始化函数
    首先一运行生成自己的服务器秘钥和证书
    建立socket进入监听状态
    select.select非阻断式处理数据包接收
    while循环中会不断刷新在线信息
"""

import socket
import struct
import sys
import traceback
from pprint import pprint

import select

import common.transmission.secure_channel
import server.memory
from common.config import get_config
from common.cryptography import crypt
from common.message import MessageType
from server.event_handler import handle_event
from server.memory import *
from server.util import database


def gen_cert():
    """生成证书"""
    crypt.gen_secret("admin")
    with open("public.pem", "r") as f:
        public = f.read()
    with open("admin_cert.pem", "w") as f:
        f.write("server 1529177144@qq.com " + public)


def run():
    gen_cert()

    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind((config['server']['bind_ip'], config['server']['bind_port']))
    s.listen(1)

    print("Server listening on " + config['server']['bind_ip'] + ":" + str(config['server']['bind_port']))

    bytes_to_receive = {}
    bytes_received = {}
    data_buffer = {}

    while True:
        rlist, wlist, xlist = select.select(list(map(lambda x: x.socket, scs)) + [s], [], [])

        for i in rlist:

            if i == s:
                # 监听socket为readable，说明有新的客户要连入
                sc = common.transmission.secure_channel.accept_client_to_secure_channel(s)
                socket_to_sc[sc.socket] = sc
                scs.append(sc)
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                data_buffer[sc] = bytes()
                continue

            # 如果不是监听socket，就是旧的客户发消息过来了
            sc = socket_to_sc[i]

            if bytes_to_receive[sc] == 0 and bytes_received[sc] == 0:
                # 一次新的接收
                conn_ok = True
                first_4_bytes = ''
                try:
                    first_4_bytes = sc.socket.recv(4)
                except ConnectionError:
                    conn_ok = False

                if first_4_bytes == "" or len(first_4_bytes) < 4:
                    conn_ok = False

                if not conn_ok:
                    sc.close()

                    if sc in sc_to_user_id:
                        user_id = sc_to_user_id[sc]
                        # 通知他的好友他下线了

                        frs = database.get_friends(user_id)
                        for fr in frs:
                            if fr['id'] in user_id_to_sc:
                                user_id_to_sc[fr['id']].send(MessageType.friend_on_off_line, [False, user_id])

                    # 把他的连接信息移除
                    remove_sc_from_socket_mapping(sc)

                else:
                    data_buffer[sc] = bytes()
                    bytes_to_receive[sc] = struct.unpack('!L', first_4_bytes)[0] + 16 + 32

            buffer = sc.socket.recv(bytes_to_receive[sc] - bytes_received[sc])
            data_buffer[sc] += buffer
            bytes_received[sc] += len(buffer)

            if bytes_received[sc] == bytes_to_receive[sc] and bytes_received[sc] != 0:
                # 当一个数据包接收完毕
                bytes_to_receive[sc] = 0
                bytes_received[sc] = 0
                try:
                    data = sc.on_data(data_buffer[sc])
                    print(data['type'])
                    handle_event(sc, data['type'], data['parameters'])
                except:
                    pprint(sys.exc_info())
                    traceback.print_exc(file=sys.stdout)
                    pass
                data_buffer[sc] = bytes()
