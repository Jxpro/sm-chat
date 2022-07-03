#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""数据库操作，将用户加入到指定房间的操作"""

import server.memory
from common.message import MessageType
from server.util import add_target_type
from server.util import database


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    # 异常处理判断
    if database.in_room(user_id, parameters):
        sc.send(MessageType.general_failure, '已经在群里了')
        return
    room = database.get_room(parameters)
    if room is None:
        sc.send(MessageType.general_failure, '群不存在')
        return
    database.add_to_room(user_id, parameters)
    # contact_info操作码控制handle_contact函数，做前端添加聊天框操作
    sc.send(MessageType.contact_info, add_target_type(room, 1))
