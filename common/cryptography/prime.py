#!/usr/bin/env python
# -*- coding:utf-8 -*-

"""生成大素数

先生成随机数，然后判断是否是素数
"""

from random import randint

""" 判断是否为大素数 """
def is_prime(num, test_count):
    if num == 1:
        return False
    if test_count >= num:
        test_count = num - 1
    for x in range(test_count):
        val = randint(1, num - 1)
        if pow(val, num-1, num) != 1:
            return False
    return True

""" 生成大素数 """
def generate_big_prime(n):
    found_prime = False
    while not found_prime:
        p = randint(2**(n-1), 2**n)
        if is_prime(p, 1000):
            return p