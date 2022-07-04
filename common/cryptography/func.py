# -*-coding:utf-8-*-

def xor_list(a, b):
    return [a[i] ^ b[i] for i in range(min(len(a), len(b)))]


def rot_l_n(x, n):
    return ((x << n) & 0xffffffff) | ((x >> (32 - n)) & 0xffffffff)


def bytes_list_to_uint32(key_data):
    return (key_data[0] << 24) | (key_data[1] << 16) | (key_data[2] << 8) | (key_data[3])


def uint32_to_bytes_list(n):
    return [((n >> 24) & 0xff), ((n >> 16) & 0xff), ((n >> 8) & 0xff), (n & 0xff)]


def padding(data, block=16):
    return data + [(16 - len(data) % block) for _ in range(16 - len(data) % block)]


def unpadding(data):
    return data[:-data[-1]]
