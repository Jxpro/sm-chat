#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import Toplevel
from tkinter import messagebox

import client.memory
import client.util.socket_listener
from client.forms.contacts_form import ContactsForm
from client.forms.register_form import RegisterForm
from common.message import MessageType


class LoginForm(tk.Frame):
    """ 登录界面 """

    def __init__(self, master=None):
        """创建主窗口用来容纳其他组件"""
        super().__init__(master)
        self.master = master
        self.master.title("基于国密算法的安全即时通信系统")
        self.master.resizable(width=False, height=False)
        # 使窗口居中
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        self.master.geometry("%dx%d+%d+%d" % (360, 150, (width - 360) / 2, (height - 150) / 2))
        # 画布放置图片
        self.canvas = tk.Canvas(self.master, width=360, height=150)
        # 标签 用户名密码
        self.user_name = tk.Label(self.master, text='用户名', font=("楷体", 16), fg="black")
        self.user_pwd = tk.Label(self.master, text='密  码', font=("楷体", 16), fg="black")
        # 用户名输入框
        self.var_user_name = tk.StringVar()
        self.entry_user_name = tk.Entry(self.master, textvariable=self.var_user_name, font=("楷体", 18), fg="black",
                                        relief=GROOVE)
        # 密码输入框
        self.var_user_pwd = tk.StringVar()
        self.entry_user_pwd = tk.Entry(self.master, textvariable=self.var_user_pwd, show='* ', font=("楷体", 18),
                                       fg="black", relief=GROOVE)
        # 登录 注册按钮
        self.register_btn = tk.Button(self.master, text='注册', font=("楷体", 18), fg="black",
                                      relief=GROOVE, command=self.show_register)
        self.login_btn = Button(self.master, text='登录', font=("楷体", 18), fg="black",
                                relief=GROOVE, command=self.do_login)
        self.quit_btn = tk.Button(self.master, text='退出', font=("楷体", 18), fg="black",
                                  relief=GROOVE, command=self.destroy_window)
        # 位置定位
        self.canvas.grid(row=0, column=0, rowspan=7, columnspan=8, )
        self.user_name.grid(row=4, column=2, sticky=E, padx=0, pady=0, )
        self.user_pwd.grid(row=5, column=2, sticky=E + N)
        self.entry_user_name.grid(row=4, column=3, columnspan=2, sticky=W)
        self.entry_user_pwd.grid(row=5, column=3, columnspan=2, sticky=W + N)
        self.register_btn.grid(row=6, column=2, columnspan=1, sticky=E + N, pady=10)
        self.login_btn.grid(row=6, column=3, columnspan=1, sticky=E + N, pady=10)
        self.quit_btn.grid(row=6, column=4, columnspan=1, sticky=E + N, pady=10)
        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)

    def remove_socket_listener_and_close(self):
        """ 关闭端口监听 """
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    @staticmethod
    def destroy_window():
        """" 关闭窗口 """
        client.memory.tk_root.destroy()

    def socket_listener(self, data):
        """ 开启监听 """
        if data['type'] == MessageType.login_failed:
            messagebox.showerror('Error', '登入失败，请检查用户名密码')
            return

        if data['type'] == MessageType.login_successful:
            client.memory.current_user = data['parameters']
            self.remove_socket_listener_and_close()
            contacts = Toplevel(client.memory.tk_root, takefocus=True)
            ContactsForm(contacts)
            return

    def do_login(self):
        """登录操作若为空则提示用户错误"""
        username = self.var_user_name.get()
        password = self.var_user_pwd.get()
        if not username:
            messagebox.showerror("Error", "用户名不能为空", )
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        self.sc.send(MessageType.login, [username, password])

    @staticmethod
    def show_register():
        """ 转到注册界面 """
        register_form = Toplevel()
        RegisterForm(register_form)
