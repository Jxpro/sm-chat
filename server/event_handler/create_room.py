#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""操作数据库创建房间，新增数据"""

import server.memory
from common.message import MessageType
from server.util import add_target_type
from server.util import database


def run(sc, parameters):
    user_id = server.memory.sc_to_user_id[sc]
    c = database.get_cursor()
    c.execute("insert into rooms (room_name) values (?)", [parameters])
    sc.send(MessageType.contact_info, add_target_type(database.get_room(c.lastrowid), 1))
    database.add_to_room(user_id, c.lastrowid)
    sc.send(MessageType.general_msg, '创建成功，群号为：' + str(c.lastrowid))
