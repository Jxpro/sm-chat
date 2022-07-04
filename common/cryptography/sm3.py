import struct
from functools import reduce
from math import ceil

from common.cryptography.func import *

IV = [
    0x7380166f, 0x4914b2b9, 0x172442d7, 0xda8a0600,
    0xa96f30bc, 0x163138aa, 0xe38dee4d, 0xb0fb0e4e,
]

T_j = [
    0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519,
    0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519,
    0x79cc4519, 0x79cc4519, 0x79cc4519, 0x79cc4519, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a,
    0x7a879d8a, 0x7a879d8a, 0x7a879d8a, 0x7a879d8a
]


def _ff_j(x, y, z, j):
    ret = 0
    if 0 <= j < 16:
        ret = x ^ y ^ z
    elif 16 <= j < 64:
        ret = (x & y) | (x & z) | (y & z)
    return ret


def _gg_j(x, y, z, j):
    ret = None
    if 0 <= j < 16:
        ret = x ^ y ^ z
    elif 16 <= j < 64:
        ret = (x & y) | ((~ x) & z)
    return ret


def _p_0(x):
    return x ^ (rot_l_n(x, 9)) ^ (rot_l_n(x, 17))


def _p_1(x):
    return x ^ (rot_l_n(x, 15)) ^ (rot_l_n(x, 23))


def _cf(v_i, b_i):
    """
    压缩函数
    """
    w = [0] * 68

    # 将B(i)划分为16个字
    for i in range(16):
        w[i] = bytes_list_to_uint32(b_i[i * 4: (i + 1) * 4])

    for j in range(16, 68):
        w[j] = _p_1(w[j - 16] ^ w[j - 9] ^ (rot_l_n(w[j - 3], 15))) ^ (rot_l_n(w[j - 13], 7)) ^ w[j - 6]
    w_1 = [0] * 64
    for j in range(0, 64):
        w_1[j] = w[j] ^ w[j + 4]

    a, b, c, d, e, f, g, h = v_i

    for j in range(0, 64):
        ss_1 = rot_l_n(((rot_l_n(a, 12)) + e + (rot_l_n(T_j[j], j % 32))) & 0xffffffff, 7)
        ss_2 = ss_1 ^ (rot_l_n(a, 12))
        tt_1 = (_ff_j(a, b, c, j) + d + ss_2 + w_1[j]) & 0xffffffff
        tt_2 = (_gg_j(e, f, g, j) + h + ss_1 + w[j]) & 0xffffffff
        d = c
        c = rot_l_n(b, 9)
        b = a
        a = tt_1
        h = g
        g = rot_l_n(f, 19)
        f = e
        e = _p_0(tt_2)

    v_j = [a, b, c, d, e, f, g, h]
    return [v_j[i] ^ v_i[i] for i in range(8)]


def sm3_hash(msg):
    """
    SM3哈希算法
    """
    # 获取消息长度
    msg_len = len(msg)
    # 计算填充长度
    pad_len = 56 - (msg_len + 1) % 64
    # 填充消息
    msg += b'\x80'
    msg += b'\x00' * pad_len
    msg += struct.pack('>Q', msg_len * 8)

    # 计算分组数
    group_count = ceil((msg_len + pad_len + 9) / 64)

    # 分组处理
    B = []
    for i in range(group_count):
        B.append(msg[i * 64:(i + 1) * 64])

    # 迭代压缩
    V = IV
    for i in range(0, group_count):
        V = _cf(V, B[i])

    # 将uint32转换为字节
    V = reduce(lambda x, y: x + y, map(lambda x: uint32_to_bytes_list(x), V))
    return bytes(V)


if __name__ == '__main__':
    test_data1 = b'abc'
    test_data2 = b'abcd' * 16
    print([hex(i) for i in sm3_hash(test_data1)])
    print([hex(i) for i in sm3_hash(test_data2)])
