#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    服务器控制数据库注册，删除了空白字符并将英文字符小写。
    并在本地将之前的用户证书更新，写入用户username和邮箱
"""
import os

from common.cryptography import sm3
from common.message import MessageType
from server.util import database


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = database.get_cursor()
    r = c.execute('SELECT * from users where username=?', [parameters[0]])
    rows = r.fetchall()
    if len(rows) > 0:
        sc.send(MessageType.username_taken)
        return

    # 用户ip获取，命名证书，获取信息更新证书，服务端证书也会用自己的个人信息更新
    ip = str(parameters[3])
    certname = ip + "_cert.pem"
    with open(certname, 'r') as f:
        context = f.read()
        sp = context.split()
    with open(certname, 'w') as f:
        f.write("%s\n%s\n%s" % (parameters[0], parameters[2], sp[2]))

    c = database.get_cursor()
    salt = os.urandom(16)
    c.execute('INSERT into users (username,password,email,sex,age,salt) values (?,?,?,?,?,?)',
              [parameters[0],
               sm3.sm3_hash(parameters[1].encode() + salt),
               parameters[2],
               parameters[4],
               parameters[5],
               salt])
    sc.send(MessageType.register_successful, c.lastrowid)
