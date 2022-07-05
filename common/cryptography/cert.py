#!/usr/bin/env python
# -*- coding:utf-8 -*-
import base64
import os
import time

from common.config import get_config
from common.cryptography import sm2, sm3

config = get_config()
suite = sm2.SM2Suite(config['CA']['sk'], config['CA']['pk'])

cer_template = """-----BEGIN CERTIFICATE-----
{}
-----END CERTIFICATE-----"""

content_template = """版本: V1
序列号: {serial}
签名算法: sm2
哈希算法: sm3
颁发者: root
有效期: {valid_time}
使用者: {user_name}
公钥: {public}
签名: signature"""


def gen_session_key():
    return sm2.gen_key_pair()


def gen_key(prefix):
    """生成公私钥，将私钥保存到文件中，公钥返回给证书生成函数"""
    sk, pk = sm2.gen_key_pair()
    with open(prefix + "_private.pem", "w") as f:
        f.write("user: " + prefix + "\nprivate key: " + sk)
    return pk


def sign_and_verify(content, k=None, sign=None):
    # 生成指纹摘要
    fingerprint = sm3.sm3_hash(content[:content.index("签名:") - 1].encode())
    # 如果有k，则生成签名,如果有sign，则验证签名
    return suite.sign(fingerprint, k) if k else suite.verify(sign, fingerprint)


def gen_cert(user_name):
    """生成证书"""
    # 随机生成序列号
    serial = os.urandom(16).hex()
    # 获取当前格式化的时间
    valid_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()) + " 至 2030-01-01 00:00:00"
    # 生成公私钥并保存到文件中
    public = gen_key(user_name)
    content = content_template.format(serial=serial, valid_time=valid_time, user_name=user_name, public=public)
    # 签名
    content = content.replace("signature", sign_and_verify(content, k=serial))
    # 将内容进行base64编码
    content = base64.b64encode(content.encode()).decode()
    # 每隔64个字符换行
    content = "\n".join(content[i:i + 64] for i in range(0, len(content), 64))
    # 将证书内容写入文件中
    with open(user_name + "_cert.pem", "w") as f:
        f.write(cer_template.format(content))


def verify_cert(content):
    """
    验证证书
    :param content: str类型，传输过来的证书内容
    """
    # 去掉 BEGIN CERTIFICATE 和 END CERTIFICATE
    content = content[28:-26]
    content = base64.b64decode(content).decode()
    # 生成指纹
    return sign_and_verify(content, sign=content[content.index("签名:") + 4:])


def get_pk(content):
    """
    获取公钥
    :param content: str类型，证书内容
    :return: str类型，公钥
    """
    # 去掉 BEGIN CERTIFICATE 和 END CERTIFICATE
    content = content[28:-26]
    content = base64.b64decode(content).decode()
    return content.split("\n")[7].split(":")[1].strip()


def get_sk(pem_file):
    """
    获取私钥
    :param pem_file: str类型，证书文件名
    :return: str类型，私钥
    """
    with open(pem_file, "r") as f:
        return f.read().split("\n")[1].split(":")[1].strip()
