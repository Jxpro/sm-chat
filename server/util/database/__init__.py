#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""
    定义实现数据库操作的各种函数
"""

import sqlite3

from server.memory import *

conn = sqlite3.connect('server/database.db', isolation_level=None)


def get_cursor():
    return conn.cursor()


def commit():
    return conn.commit()


def get_user(user_id):
    c = get_cursor()
    fields = ['id', 'username', 'ip', 'port']
    row = c.execute('SELECT ' + ','.join(fields) + ' FROM users WHERE id=?', [user_id]).fetchall()
    if len(row) == 0:
        return None
    else:
        user = dict(zip(fields, row[0]))
        user['online'] = user_id in user_id_to_sc
        return user


def get_pending_friend_request(user_id):
    """获取user_id是被加方的所有行"""
    c = get_cursor()
    users = []
    rows = c.execute('SELECT from_user_id FROM friends WHERE to_user_id=? AND NOT accepted', [user_id]).fetchall()
    for row in rows:
        uid = row[0]
        users.append(get_user(uid))
    return users


def get_friends(user_id):
    """获取user_id是申请方的所有行"""
    c = get_cursor()
    users = []
    rows = c.execute('SELECT to_user_id FROM friends WHERE from_user_id=? AND accepted', [user_id]).fetchall()
    for row in rows:
        uid = row[0]
        users.append(get_user(uid))
    return users


def is_friend_with(from_user_id, to_user_id):
    c = get_cursor()
    r = c.execute('SELECT 1 FROM friends WHERE from_user_id=? AND to_user_id=? AND accepted=1',
                  [from_user_id, to_user_id]).fetchall()
    return len(r) > 0


def add_to_chat_history(user_id, target_id, target_type, data, sent):
    """将发送方向接收方发送的信息存入数据库,用于历史消息重发"""
    c = get_cursor()
    c.execute('INSERT INTO chat_history (user_id,target_id,target_type,data,sent) VALUES (?,?,?,?,?)',
              [user_id, target_id, target_type, data, sent])
    return c.lastrowid


def get_chat_history(user_id):
    """获取某用户的历史消息"""
    c = get_cursor()
    ret = list(map(lambda x: [bytearray(x[0]), x[1]],
                   c.execute('SELECT data,sent FROM chat_history WHERE user_id=?',
                             [user_id]).fetchall()))
    c = get_cursor()
    c.execute('UPDATE chat_history SET sent=1 WHERE user_id=?', [user_id])
    return ret
