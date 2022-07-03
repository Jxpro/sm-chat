#!/usr/bin/env python
# -*- coding:utf-8 -*-

""""聊天界面及处理与聊天相关的事件"""
import datetime
import os
import time
import tkinter as tk
from tkinter import *
from tkinter import colorchooser, simpledialog, filedialog
from tkinter.scrolledtext import ScrolledText

import filetype
from PIL import ImageTk

import client.memory
from client.util import socket_listener
from client.util.socket_listener import *


class ChatForm(tk.Frame):
    """ 聊天界面 """
    font_color = "#000000"
    font_size = 16
    user_list = []
    tag_i = 0

    def __init__(self, target, master=None):
        super().__init__(master)
        self.master = master
        self.target = target
        client.util.socket_listener.add_listener(self.socket_listener)
        client.memory.unread_message_count[self.target['type']][self.target['id']] = 0
        client.memory.contact_window[0].refresh_contacts()
        master.resizable(width=False, height=False)
        # 使窗口居中
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        self.master.geometry("%dx%d+%d+%d" % (535, 500, (width - 535) / 2.5, (height - 500) / 2.5))
        self.sc = client.memory.sc
        # 私人聊天
        if self.target['type'] == 0:
            self.master.title(self.target['username'])

        self.right_frame = tk.Frame(self)

        self.right_frame.pack(side=LEFT, expand=True, fill=BOTH)
        self.input_frame = tk.Frame(self.right_frame, bg='#f5f3f2')
        self.input_textbox = ScrolledText(self.right_frame, bg='#f5f3f2', font=("楷书", 16), height=5)
        self.input_textbox.bind("<Control-Return>", self.send_message)
        self.send_btn = tk.Button(self.input_frame, text='发送消息(Ctrl+Enter)', font=("仿宋", 14, 'bold'), fg="black",
                                  bg="#f5f3f2", activebackground="#efefef", relief=GROOVE, command=self.send_message)
        self.send_btn.pack(side=RIGHT, expand=False)
        self.font_btn = tk.Button(self.input_frame, text='字体颜色', font=("仿宋", 14, 'bold'), fg="black", bg="#f5f3f2",
                                  activebackground="#efefef", relief=GROOVE, command=self.choose_color)
        self.font_btn.pack(side=LEFT, expand=False)
        self.font_btn = tk.Button(self.input_frame, text='字体大小', font=("仿宋", 14, 'bold'), fg="black", bg="#f5f3f2",
                                  activebackground="#efefef", relief=GROOVE, command=self.choose_font_size)
        self.font_btn.pack(side=LEFT, expand=False)
        self.image_btn = tk.Button(self.input_frame, text='发送图片', font=("仿宋", 14, 'bold'), fg="black", bg="#f5f3f2",
                                   activebackground="#efefef", relief=GROOVE, command=self.send_image)
        self.image_btn.pack(side=LEFT, expand=False)

        self.chat_box = ScrolledText(self.right_frame, bg='#d4dde1')
        self.input_frame.pack(side=BOTTOM, fill=X, expand=False)
        self.input_textbox.pack(side=BOTTOM, fill=X, expand=False, padx=(0, 0), pady=(0, 0))
        self.chat_box.pack(side=BOTTOM, fill=BOTH, expand=True)
        self.chat_box.bind("<Key>", lambda e: "break")
        self.chat_box.tag_config("default", lmargin1=10, lmargin2=10, rmargin=10, font=("仿宋", 15))
        self.chat_box.tag_config("me", foreground="green", spacing1='0', font=("仿宋", 15))
        self.chat_box.tag_config("them", foreground="blue", spacing1='0', font=("仿宋", 15))
        self.chat_box.tag_config("message", foreground="black", spacing1='0', font=("楷体", 15))
        self.chat_box.tag_config("system", foreground="#505050", spacing1='0', justify='center', font=("新宋体", 10))

        self.pack(expand=True, fill=BOTH)

        add_message_listener(self.target['type'], self.target['id'], self.message_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_listener_and_close)

        # 历史消息显示
        if target['id'] in client.memory.chat_history[self.target['type']]:
            for msg in client.memory.chat_history[self.target['type']][target['id']]:
                self.digest_message(msg)

            self.append_to_chat_box('- 以上是历史消息 -\n', 'system')

    def remove_listener_and_close(self):
        """将监听事件移除并关闭该窗口"""
        remove_message_listener(self.message_listener)
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()
        if self.target['id'] in client.memory.window_instance[self.target['type']]:
            del client.memory.window_instance[self.target['type']][self.target['id']]

    def message_listener(self, data):
        """定义监听事件"""
        self.digest_message(data)

    def socket_listener(self, data):
        """监听socket传来的数据"""
        init_time = int(time.time())
        dirname = "send_msg_log"
        filename = str(init_time)
        dir_flag = os.path.exists(dirname)
        if not dir_flag:
            os.mkdir(dirname)
        if data['parameters']['message']['type'] == 1:
            with open(dirname + '/' + filename, 'wb') as f:
                contents = data['parameters']['message']['data']
                f.write(contents)
                f.close()
            with open(dirname + '/' + filename, 'rb') as f:
                file_format = filetype.guess(dirname + '/' + filename)
                file_format = file_format.extension
                if file_format is None:
                    file_format = "txt"
                f.close()
            os.rename(dirname + '/' + filename, (str(dirname + '/' + filename) + '_.' + file_format))

    def digest_message(self, data):
        """处理消息并将其展示出来"""
        time = datetime.datetime.fromtimestamp(
            int(data['time']) / 1000
        ).strftime('%Y-%m-%d %H:%M:%S')
        self.append_to_chat_box(data['sender_name'] + "  " + time + '\n',
                                ('me' if client.memory.current_user['id'] == data[
                                    'sender_id'] else 'them'))
        # type 0 - 文字消息 1 - 图片消息
        if data['message']['type'] == 0:
            self.tag_i += 1
            self.chat_box.tag_config('new' + str(self.tag_i),
                                     lmargin1=16,
                                     lmargin2=16,
                                     foreground=data['message']['fontcolor'],
                                     font=(None, data['message']['fontsize']))
            self.append_to_chat_box(data['message']['data'] + '\n',
                                    'new' + str(self.tag_i))
        if data['message']['type'] == 1:
            client.memory.tk_img_ref.append(ImageTk.PhotoImage(data=data['message']['data']))
            self.chat_box.image_create(END, image=client.memory.tk_img_ref[-1], padx=16, pady=5)
            self.append_to_chat_box('\n', '')

    def append_to_chat_box(self, message, tags):
        """ 附加聊天框 """
        self.chat_box.insert(tk.END, message, [tags, 'default'])
        self.chat_box.update()
        self.chat_box.see(tk.END)

    def send_message(self, _=None):
        """ 发送消息 """
        message = self.input_textbox.get("1.0", END)
        if not message or message.replace(" ", "").replace("\r", "").replace("\n", "") == '':
            return
        self.sc.send(MessageType.send_message,
                     {'target_type': self.target['type'], 'target_id': self.target['id'],
                      'message': {
                          'type': 0,
                          'data': message.strip().strip('\n'),
                          'fontsize': self.font_size,
                          'fontcolor': self.font_color
                      }
                      })
        self.input_textbox.delete("1.0", END)
        return 'break'

    def choose_color(self):
        """ 选择字体颜色 """
        _, self.font_color = colorchooser.askcolor(initialcolor=self.font_color)
        self.apply_font_change(None)

    def choose_font_size(self):
        """ 选择字体大小 """
        result = simpledialog.askinteger("设置", "请输入字体大小", initialvalue=self.font_size)
        if result is None:
            return
        self.font_size = result
        self.apply_font_change(None)

    def apply_font_change(self, _):
        """" 更新字体 """
        try:
            self.input_textbox.tag_config('new', foreground=self.font_color, font=(None, self.font_size))
            self.input_textbox.tag_add('new', '1.0', END)
        except:
            pass

    def send_image(self):
        """" 发送图片 """
        filename = filedialog.askopenfilename(filetypes=[("Image Files",
                                                          ["*.jpg", "*.jpeg", "*.png", "*.gif", "*.JPG", "*.JPEG",
                                                           "*.PNG", "*.GIF"]),
                                                         ("All Files", ["*.*"])])
        if filename is None or filename == '':
            return
        with open(filename, "rb") as imageFile:
            f = imageFile.read()
            b = bytearray(f)
            self.sc.send(MessageType.send_message,
                         {'target_type': self.target['type'], 'target_id': self.target['id'],
                          'message': {'type': 1, 'data': b}})
