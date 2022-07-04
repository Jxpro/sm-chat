#!/usr/bin/env python
# -*- coding:utf-8 -*-

""" 服务器使用数据库验证客户端数据登录 """
from common.cryptography import sm3
from common.message import MessageType
from server.memory import *
from server.util import add_target_type
from server.util import database


def run(sc, parameters):
    parameters[0] = parameters[0].strip().lower()
    c = database.get_cursor()
    r = c.execute('SELECT id,username from users where username=? and password=?',
                  (parameters[0], sm3.sm3_hash(parameters[1].encode())))
    rows = r.fetchall()

    if len(rows) == 0:
        sc.send(MessageType.login_failed)
        return

    user_id = rows[0][0]

    # 已经登入，踢下线
    if user_id in user_id_to_sc:
        sc_old = user_id_to_sc[user_id]
        sc_old.send(MessageType.server_kick)
        sc_old.close()
        remove_sc_from_socket_mapping(sc_old)

    sc_to_user_id[sc] = user_id
    user_id_to_sc[user_id] = sc
    user = database.get_user(user_id)
    sc.send(MessageType.login_successful, user)

    login_bundle = {}

    # 发送好友请求
    frs = database.get_pending_friend_request(user_id)

    for fr in frs:
        sc.send(MessageType.incoming_friend_request, fr)

    # 发送好友列表
    frs = database.get_friends(user_id)
    login_bundle['friends'] = list(map(lambda x: add_target_type(x, 0), frs))

    for fr in frs:
        # 通知他的好友他上线了
        if fr['id'] in user_id_to_sc:
            user_id_to_sc[fr['id']].send(MessageType.friend_on_off_line, [True, user_id])

    login_bundle['messages'] = database.get_chat_history(user_id)
    sc.send(MessageType.login_bundle, login_bundle)
