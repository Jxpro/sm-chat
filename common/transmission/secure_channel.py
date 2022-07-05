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
from common.cryptography import cert, sm3, sm2
from common.cryptography.sm4 import SM4Suite, SM4_CBC_MODE
from common.message import serialize_message, deserialize_message, ByteArrayReader


class SecureChannel:
    """建立安全信道"""

    def __init__(self, sc_socket, shared_secret):
        sc_socket.setblocking(0)
        self.socket = sc_socket
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

    # 如果客户端的证书不存在，则创建一个新的证书
    cert_name = ip + "_cert.pem"
    if not os.path.exists(cert_name):
        cert.gen_cert(ip)

    # 首次连接，给服务器发送证书
    with open(cert_name, 'rb') as f:
        s.send(f.read())

    # 接收服务器证书
    server_cert = s.recv(1024).decode()
    # 验证服务器证书
    if not cert.verify_cert(server_cert):
        raise Exception("Server's cert is invalid")

    # 获取服务器公钥
    server_pk = cert.get_pk(server_cert)
    # 获取客户端密钥
    client_sk = cert.get_sk(ip + "_private.pem")
    # 密钥协商
    share_secret = key_agreement(s, server_pk, client_sk)

    sc = SecureChannel(s, bytes.fromhex(share_secret[:32]))

    return sc


def accept_client_to_secure_channel(sc_socket):
    conn, address = sc_socket.accept()

    # 接收客户端证书
    client_cert = conn.recv(1024)

    # 验证客户端证书
    if not cert.verify_cert(client_cert):
        raise Exception("Client's cert is invalid")

    # 把服务器的证书发送给客户端
    with open("admin_cert.pem", 'rb') as f:
        conn.send(f.read())

    # 获取客户端公钥
    client_pk = cert.get_pk(client_cert)
    # 获取客户端密钥
    server_sk = cert.get_sk("admin_private.pem")
    # 密钥协商
    share_secret = key_agreement(conn, client_pk, server_sk)

    sc = SecureChannel(conn, bytes.fromhex(share_secret[:32]))
    return sc


def key_agreement(s, pk, sk):
    """
    密钥协商
    :param s: socket连接
    :param pk: 公钥
    :param sk: 私钥
    :return: session_key
    """
    # 会话加密套件
    session_suite = sm2.SM2Suite(sk, pk)

    # 生成会话密钥对
    session_sk, session_pk = cert.gen_session_key()

    # 发送会话密钥
    s.send((session_pk + session_suite.sign(session_pk.encode(), os.urandom(16).hex())).encode())

    # 接受会话密钥
    recv_data = s.recv(1024).decode()
    recv_session_pk = recv_data[:128]
    recv_sign = recv_data[128:]

    # 验证会话密钥
    if not session_suite.verify(recv_sign, recv_session_pk.encode()):
        raise Exception("Session key is invalid")

    # 计算会话密钥
    return session_suite.kg(int(session_sk, 16), recv_session_pk)


def get_ip():
    """获取本机IP"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    ip = s.getsockname()[0]
    return ip
