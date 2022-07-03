#!/usr/bin/env python
# -*- coding:utf-8 -*-

import tkinter as tk
from tkinter import *
from tkinter import messagebox
from tkinter import ttk

import client.memory
import client.util.socket_listener
from common.config import get_config
from common.message import MessageType
from common.transmission.secure_channel import get_ip


class RegisterForm(tk.Frame):
    """ 注册界面 """

    def __init__(self, master=None):
        super().__init__(master)
        self.master = master
        self.sc = client.memory.sc

        self.master.title("基于国密算法的安全即时通信系统")
        master.resizable(width=False, height=False)
        # 使窗口居中
        width = self.master.winfo_screenwidth()
        height = self.master.winfo_screenheight()
        self.master.geometry("%dx%d+%d+%d" % (460, 310, (width - 460) / 2, (height - 310) / 2))
        # 画布
        self.canvas = tk.Canvas(self.master, width=460, height=310)
        # 标签 用户名、密码、确认密码、邮箱、性别、年龄
        self.user_name = tk.Label(self.master, text="用户名", font=("楷体", 16), fg="black")
        self.user_pwd = tk.Label(self.master, text="密  码", font=("楷体", 16), fg="black")
        self.confirm_pwd = tk.Label(self.master, text="确认密码", font=("楷体", 16), fg="black")
        self.user_email = tk.Label(self.master, text="邮  箱", font=("楷体", 16), fg="black")
        self.user_sex = tk.Label(self.master, text="性  别", font=("楷体", 16), fg="black")
        self.user_age = tk.Label(self.master, text="年  龄", font=("楷体", 16), fg="black")
        # 输入框
        # 用户名输入框
        self.var_user_name = tk.StringVar()
        self.entry_user_name = tk.Entry(self.master, textvariable=self.var_user_name, font=("楷体", 18), fg="black",
                                        relief=GROOVE)
        # 密码输入框
        self.var_user_pwd = tk.StringVar()
        self.entry_user_pwd = tk.Entry(self.master, textvariable=self.var_user_pwd, show='* ', font=("楷体", 18),
                                       fg="black", relief=GROOVE)
        # 确认密码输入框
        self.var_confirm_pwd = tk.StringVar()
        self.entry_confirm_pwd = tk.Entry(self.master, textvariable=self.var_confirm_pwd, show='* ', font=("楷体", 18),
                                          fg="black", relief=GROOVE)
        # 邮箱输入框
        self.var_user_email = tk.StringVar()
        self.entry_user_email = tk.Entry(self.master, textvariable=self.var_user_email, font=("Arial", 14), fg="black",
                                         relief=GROOVE)
        # 性别输入框
        self.var_user_sex = tk.StringVar()
        self.entry_user_sex = ttk.Combobox(self.master, textvariable=self.var_user_sex, font=("楷体", 18),
                                           state="readonly")
        self.entry_user_sex['values'] = ("保密", "男", "女")
        self.entry_user_sex.current(0)
        # 年龄输入框
        self.var_user_age = tk.StringVar()
        self.entry_user_age = ttk.Combobox(self.master, textvariable=self.var_user_age, font=("楷体", 18),
                                           state="readonly")
        self.entry_user_age['values'] = ("保密", 0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20,
                                         21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39, 40,
                                         41, 42, 43, 44, 45, 46, 47, 48, 49, 50, 51, 52, 53, 54, 55, 56, 57, 58, 59, 60,
                                         61, 62, 63, 64, 65, 66, 67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77, 78, 79, 80,
                                         81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99,
                                         100)
        self.entry_user_age.current(0)
        # 注册按钮
        self.register_btn = tk.Button(self.master, text='       注     册       ', font=("楷体", 18), fg="black",
                                      relief=GROOVE, width=30,
                                      command=self.do_register)
        # 位置定位
        # label位置定位
        self.canvas.grid(row=0, column=0, rowspan=18, columnspan=8, )
        self.user_name.grid(row=8, column=1, columnspan=2, sticky=E)
        self.user_pwd.grid(row=9, column=1, columnspan=2, sticky=E)
        self.confirm_pwd.grid(row=10, column=1, columnspan=2, sticky=E)
        self.user_email.grid(row=11, column=1, columnspan=2, sticky=E)
        self.user_sex.grid(row=12, column=1, columnspan=2, sticky=E)
        self.user_age.grid(row=13, column=1, columnspan=2, sticky=E)
        # 输入框位置定位
        self.entry_user_name.grid(row=8, column=3, columnspan=3, sticky=W, pady=5)
        self.entry_user_pwd.grid(row=9, column=3, columnspan=3, sticky=W, pady=5)
        self.entry_confirm_pwd.grid(row=10, column=3, columnspan=3, sticky=W, pady=5)
        self.entry_user_email.grid(row=11, column=3, columnspan=3, sticky=W, pady=5)
        self.entry_user_sex.grid(row=12, column=3, columnspan=3, sticky=W, pady=5)
        self.entry_user_age.grid(row=13, column=3, columnspan=3, sticky=W, pady=5)
        # 注册按钮位置定位
        self.register_btn.grid(row=14, column=2, columnspan=4, sticky=S + W, pady=5)

        self.sc = client.memory.sc
        client.util.socket_listener.add_listener(self.socket_listener)
        master.protocol("WM_DELETE_WINDOW", self.remove_socket_listener_and_close)

    def socket_listener(self, data):
        """ 打开事件监听 """
        if data['type'] == MessageType.username_taken:
            messagebox.showerror('Error', '用户名已被使用，请换一个')
            return

        if data['type'] == MessageType.register_successful:
            messagebox.showinfo('Congratulations', '恭喜，注册成功，您成为第' + str(data['parameters']) + '个用户')
            self.remove_socket_listener_and_close()
            return

    def remove_socket_listener_and_close(self):
        """ 关闭监听 """
        client.util.socket_listener.remove_listener(self.socket_listener)
        self.master.destroy()

    def do_register(self):
        """" 注册操作 """
        username = self.var_user_name.get()
        password = self.var_user_pwd.get()
        password_confirmation = self.var_confirm_pwd.get()
        email = self.var_user_email.get()
        sex = self.var_user_sex.get()
        age = self.var_user_age.get()

        ip = get_ip()
        config = get_config()
        port = str((config['client']['client_port']))

        if not username:
            messagebox.showerror("Error", "用户名不能为空")
            return
        if not email:
            messagebox.showerror("Error", "邮箱不能为空")
            return
        if not password:
            messagebox.showerror("Error", "密码不能为空")
            return
        if password != password_confirmation:
            messagebox.showerror("Error", "两次密码输入不一致")
            return
        if not re.match(r'^[0-9a-zA-Z_]{0,19}@[0-9a-zA-Z]{1,13}\.[comnet]{1,3}$', email):
            messagebox.showerror("Error", "邮箱格式错误")
            return
        self.sc.send(MessageType.register, [username, password, email, ip, port, sex, age])

        certname = ip + "_cert.pem"
        with open(certname, 'rb') as f:
            context = f.read()
            sp = context.split()
            f.close()
        with open(certname, 'wb') as f:
            f.write(
                (str(self.var_user_name.get()) + ' ' + str(self.var_user_email.get()) + " " + sp[2].decode()).encode())
            f.close()
