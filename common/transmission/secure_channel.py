#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
通过安全信道传输的消息格式
|--Length of Message Body(4Bytes)--|-- IV (16Bytes)--|--MAC (32Bytes)--|--Encrypted Message Body (CSON)--|
"""

import os
import socket
import struct
from pprint import pprint

from common.config import get_config
from common.cryptography import crypt, sm3
from common.cryptography.sm4 import SM4Suite, SM4_CBC_MODE
from common.message import serialize_message, deserialize_message, ByteArrayReader


class SecureChannel:
    """建立安全信道"""

    def __init__(self, socket, shared_secret):
        socket.setblocking(0)
        self.socket = socket
        self.shared_secret = shared_secret
        return

    def send(self, message_type, parameters=None):
        iv = os.urandom(16)

        data_to_encrypt = serialize_message(message_type, parameters)
        encrypted_message = SM4Suite(self.shared_secret, SM4_CBC_MODE, iv=iv).encrypt(data_to_encrypt)

        mac = sm3.sm3_hash(encrypted_message)
        length_of_encrypted_message = len(encrypted_message)
        self.socket.send(struct.pack('!L', length_of_encrypted_message) + iv + mac + encrypted_message)
        return

    def on_data(self, data_array):
        """
        用select循环socket.recv，当收到一个完整的数据块后（收到后length_of_encrypted_message+16+32个字节后），
        把 iv + +mac + encrypted_message 传给本函数
        """
        br = ByteArrayReader(data_array)
        iv = br.read(16)

        recv_mac = br.read(32)
        data = br.read_to_end()
        mac = sm3.sm3_hash(data)
        if mac != recv_mac:
            pprint('Message Authentication Error')
            exit(-1)

        return deserialize_message(SM4Suite(self.shared_secret, SM4_CBC_MODE, iv=iv).decrypt(data))

    def close(self):
        self.socket.close()


def establish_secure_channel_to_server():
    config = get_config()
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    s.connect((config['client']['server_ip'], int(config['client']['server_port'])))

    # 获取本机IP
    ip = get_ip()
    s.send(ip.encode())

    # 接收服务器证书
    server_cert = s.recv(1024)

    certname = ip + "_cert.pem"
    if not os.path.exists(certname):
        # 生成私钥公钥和证书
        crypt.gen_secret("client")
        f = open('public.pem', 'r')
        public = f.read()
        with open(certname, 'w') as f:
            f.write("client\n1529177144@qq.com\n" + public)

    # 首次连接，给服务器发送证书
    with open(certname, 'rb') as f:
        s.send(f.read())

    pk = crypt.get_pk_from_cert(server_cert)
    # 计算出共同密钥
    shared_secret = crypt.get_shared_secret(pk, "client")

    sc = SecureChannel(s, shared_secret)

    return sc


def accept_client_to_secure_channel(socket):
    conn, addr = socket.accept()

    # 首次连接，客户端会发送diffle hellman密钥
    ip = conn.recv(1024)
    certname = ip.decode() + "_cert.pem"

    # 把服务器的证书发送给客户端
    with open("admin_cert.pem", 'rb') as f:
        conn.send(f.read())

    client_cert = conn.recv(1024)
    with open(certname, 'wb') as f:
        f.write(client_cert)

    # 计算出共享密钥
    pk = crypt.get_pk_from_cert(client_cert)
    shared_secert = crypt.get_shared_secret(pk, "admin")
    sc = SecureChannel(conn, shared_secert)

    return sc


def get_ip():
    """获取本机IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip
