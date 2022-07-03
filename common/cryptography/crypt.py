#!/usr/bin/env python
# -*- coding:utf-8 -*-

import hashlib

from common.config import get_config
from common.cryptography import prime
from common.util import long_to_bytes

config = get_config()
base = config['crypto']['base']
modulus = config['crypto']['modulus']


def gen_secret(prefix=""):
    """生成公私钥并保存到文件中"""
    secret = prime.generate_big_prime(12)
    my_secret = base ** secret % modulus

    with open(prefix + "_private.pem", "wb") as f:
        f.write(str(secret).encode())
        f.close()
    with open("public.pem", "wb") as f:
        f.write(str(my_secret).encode())
        f.close()


def get_shared_secret(their_secret, prefix=""):
    """生成共享密钥"""
    f = open(prefix + "_private.pem", "rb")
    secret = int(f.read())
    f.close()
    return hashlib.sha256(long_to_bytes(int(their_secret) ** secret % modulus)).digest()


def get_pk_from_cert(cert):
    """从证书中获取公钥"""
    str = cert.split()
    return str[2]
