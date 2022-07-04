#!/usr/bin/env python
# -*- coding:utf-8 -*-

from common.config import get_config
from common.cryptography import sm2, sm3

config = get_config()
suite = sm2.SM2Suite(0, 0)


def gen_secret(prefix=""):
    """生成公私钥并保存到文件中"""
    sk, pk = sm2.gen_key_pair()

    with open(prefix + "_private.pem", "w") as f:
        f.write(sk)
    with open("public.pem", "w") as f:
        f.write(pk)


def get_shared_secret(pk, prefix=""):
    """生成共享密钥"""
    with open(prefix + "_private.pem", "r") as f:
        sk = f.read()
    return sm3.sm3_hash(suite.kg(int(sk, 16), pk.decode()).encode())[:16]


def get_pk_from_cert(cert):
    """从证书中获取公钥"""
    str = cert.split()
    return str[2]
