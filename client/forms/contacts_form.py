#!/usr/bin/env python
# -*- coding:utf-8 -*-

import datetime
import tkinter as tk
from tkinter import *
from tkinter import Toplevel
from tkinter import messagebox
from tkinter import simpledialog

import client.memory
import client.util.socket_listener
from client.components.contact_item import ContactItem
from client.components.vertical_scrolled_frame import VerticalScrolledFrame
from client.forms.chat_form import ChatForm
from common.message import MessageType, _deserialize_any


class ContactsForm(tk.Frame):
    """ 联系人列表 """
    bundle_process_done = False
    pack_objs = []

    def __init__(self, master=None):
        client.memory.contact_window.append(self)
        super().__init__(master)
        self.master = master
        self.master.title(client.memory.current_user['username'] + " —— 联系人列表")
        master.resizable(width=False, height=False)
        # 使窗口居中
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        self.master.geometry("%dx%d+%d+%d" % (400, 540, (width - 400) / 2, (height - 540) / 2))
        # 滚动条＋消息列表画布
        self.scroll = VerticalScrolledFrame(self)
        self.scroll.pack(side=TOP, fill=BOTH, expand=True)
        # 按钮
        self.button_frame_left = Frame(self)
        self.button_frame_left.pack(side=LEFT, fill=BOTH, expand=YES)
        self.button_frame_right = Frame(self)
        self.button_frame_right.pack(side=RIGHT, fill=BOTH, expand=YES)
        # 添加好友
        self.add_friend = Button(self.button_frame_left, text="添加好友", font=("楷体", 16), fg="black",
                                 relief=GROOVE, command=self.on_add_friend)
        self.add_friend.pack(side=TOP, expand=True, fill=BOTH)
        # 删除好友
        self.del_friend = Button(self.button_frame_right, text="删除好友", font=("楷体", 16), fg="black",
                                 relief=GROOVE, command=self.on_del_friend)
        self.del_friend.pack(side=TOP, expand=True, fill=BOTH)
        # 页面定位
        self.pack(side=TOP, fill=BOTH, expand=True)
        self.contacts = []
        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)

    def remove_socket_listener_and_close(self):
        """#关闭contacts_form"""
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        client.memory.tk_root.destroy()

    def socket_listener(self, data):
        """监听从服务端发来的反馈"""
        if data['type'] == MessageType.login_bundle:
            bundle = data['parameters']
            friends = bundle['friends']
            messages = bundle['messages']
            for friend in friends:
                self.handle_new_contact(friend)
            for item in messages:
                sent = item[1]
                message = _deserialize_any(item[0])
                client.util.socket_listener.digest_message(message, not sent)

            self.bundle_process_done = True
            self.refresh_contacts()

        if data['type'] == MessageType.incoming_friend_request:
            result = messagebox.askyesnocancel("好友请求", data['parameters']['username'] + "请求加您为好友，是否同意？(点击取消表示下次登录再询问)")
            if result is None:
                return
            self.sc.send(MessageType.resolve_friend_request, [data['parameters']['id'], result])

        if data['type'] == MessageType.contact_info:
            self.handle_new_contact(data['parameters'])
            return

        if data['type'] == MessageType.del_info:
            self.handle_del_contact(data['parameters'])
            return

        if data['type'] == MessageType.add_friend_result:
            if data['parameters'][0]:
                messagebox.showinfo('添加好友', '好友请求已发送')
            else:
                messagebox.showerror('添加好友失败', data['parameters'][1])
            return

        if data['type'] == MessageType.del_friend_result:
            if data['parameters'][0]:
                messagebox.showinfo('删除好友', '成功删除好友')
            else:
                messagebox.showerror('删除好友失败', data['parameters'][1])
            return

        if data['type'] == MessageType.friend_on_off_line:
            friend_user_id = data['parameters'][1]

            for i in range(0, len(self.contacts)):
                if self.contacts[i]['id'] == friend_user_id and self.contacts[i]['type'] == 0:
                    self.contacts[i]['online'] = data['parameters'][0]
                    break
            self.refresh_contacts()
            return

    def handle_new_contact(self, data):
        """处理新的联系人"""
        data['last_timestamp'] = 0
        data['last_message'] = '(没有消息)'
        self.contacts.insert(0, data)
        self.refresh_contacts()

    def handle_del_contact(self, data):
        """处理删除好友的操作后"""
        id = data['id']
        for conn in self.contacts:
            if conn['id'] == id:
                self.contacts.remove(conn)
        self.refresh_contacts()

    @staticmethod
    def on_frame_click(e):
        item_id = e.widget.item['id']
        if item_id in client.memory.window_instance[e.widget.item['type']]:
            client.memory.window_instance[e.widget.item['type']][item_id].master.deiconify()
            return
        form = Toplevel(client.memory.tk_root, takefocus=True)
        client.memory.window_instance[e.widget.item['type']][item_id] = ChatForm(e.widget.item, form)

    def on_add_friend(self):
        """ 添加好友 """
        result = simpledialog.askstring('+', '添加好友 - 请输入用户名')
        if not result:
            return
        self.sc.send(MessageType.add_friend, result)

    def on_del_friend(self):
        """ 删除好友 """
        result = simpledialog.askstring('-user2', '删除好友 - 请输入用户名')
        if not result:
            return
        self.sc.send(MessageType.del_friend, result)

    def refresh_contacts(self):
        """更新列表界面"""
        # self.contacts是一个列表，里面很多用户字典
        if not self.bundle_process_done:
            return

        for pack_obj in self.pack_objs:
            pack_obj.pack_forget()
            pack_obj.destroy()

        self.pack_objs = []
        self.contacts.sort(key=lambda x: -client.memory.last_message_timestamp[x['type']].get(x['id'], 0))

        for item in self.contacts:
            contact = ContactItem(self.scroll.interior, self.on_frame_click)
            contact.pack(fill=BOTH, expand=True)
            contact.item = item

            contact.bind("<Button>", self.on_frame_click)
            if item['type'] == 0:
                # 联系人
                contact.title.config(text=item['username'] + (' (在线)' if item['online'] else ' (离线)'))
                contact.title.config(fg='blue' if item['online'] else '#505050', )
                contact.friend_ip.config(text=item['ip'] + ':' + item['port'])

            self.pack_objs.append(contact)
            time_message = datetime.datetime.fromtimestamp(
                item['last_timestamp']
            ).strftime('%Y-%m-%d %H:%M:%S')

            contact.last_message_time.config(text=time_message)

            contact.last_message.config(text=client.memory.last_message[item['type']].get(item['id'], '(没有消息)'))
            contact.last_message_time.config(text=datetime.datetime.fromtimestamp(
                int(client.memory.last_message_timestamp[item['type']].get(item['id'], 0)) / 1000
            ).strftime('%Y-%m-%d %H:%M:%S'))

            unread_count = client.memory.unread_message_count[item['type']].get(item['id'], 0)
            contact.unread_message_count.pack_forget()
            if unread_count != 0:
                contact.last_message.pack_forget()
                contact.unread_message_count.pack(side=RIGHT, anchor=E, fill=None, expand=False, ipadx=4)
                contact.last_message.pack(side=LEFT, fill=X, expand=True, anchor=W)
                contact.unread_message_count.config(text=str(unread_count))
