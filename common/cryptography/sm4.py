# -*-coding:utf-8-*-
import os
from functools import reduce

from common.cryptography.func import *

# 加密模式
SM4_ECB_MODE = "_ecb_mode"
SM4_CBC_MODE = "_cbc_mode"
SM4_CFB_MODE = "_cfb_mode"
SM4_OFB_MODE = "_ofb_mode"
SM4_CTR_MODE = "_ctr_mode"

# 需要iv的加密模式
_need_iv_list = [SM4_CBC_MODE, SM4_CFB_MODE, SM4_OFB_MODE]
# 需要nonce的加密模式
_need_nonce_list = [SM4_CTR_MODE]
# 加密解密时，轮密钥顺序需要转置的模式
_need_reverse_list = [SM4_ECB_MODE, SM4_CBC_MODE]

# S盒
_SM4_BOXES_TABLE = [
    0xd6, 0x90, 0xe9, 0xfe, 0xcc, 0xe1, 0x3d, 0xb7, 0x16, 0xb6, 0x14, 0xc2, 0x28, 0xfb, 0x2c,
    0x05, 0x2b, 0x67, 0x9a, 0x76, 0x2a, 0xbe, 0x04, 0xc3, 0xaa, 0x44, 0x13, 0x26, 0x49, 0x86,
    0x06, 0x99, 0x9c, 0x42, 0x50, 0xf4, 0x91, 0xef, 0x98, 0x7a, 0x33, 0x54, 0x0b, 0x43, 0xed,
    0xcf, 0xac, 0x62, 0xe4, 0xb3, 0x1c, 0xa9, 0xc9, 0x08, 0xe8, 0x95, 0x80, 0xdf, 0x94, 0xfa,
    0x75, 0x8f, 0x3f, 0xa6, 0x47, 0x07, 0xa7, 0xfc, 0xf3, 0x73, 0x17, 0xba, 0x83, 0x59, 0x3c,
    0x19, 0xe6, 0x85, 0x4f, 0xa8, 0x68, 0x6b, 0x81, 0xb2, 0x71, 0x64, 0xda, 0x8b, 0xf8, 0xeb,
    0x0f, 0x4b, 0x70, 0x56, 0x9d, 0x35, 0x1e, 0x24, 0x0e, 0x5e, 0x63, 0x58, 0xd1, 0xa2, 0x25,
    0x22, 0x7c, 0x3b, 0x01, 0x21, 0x78, 0x87, 0xd4, 0x00, 0x46, 0x57, 0x9f, 0xd3, 0x27, 0x52,
    0x4c, 0x36, 0x02, 0xe7, 0xa0, 0xc4, 0xc8, 0x9e, 0xea, 0xbf, 0x8a, 0xd2, 0x40, 0xc7, 0x38,
    0xb5, 0xa3, 0xf7, 0xf2, 0xce, 0xf9, 0x61, 0x15, 0xa1, 0xe0, 0xae, 0x5d, 0xa4, 0x9b, 0x34,
    0x1a, 0x55, 0xad, 0x93, 0x32, 0x30, 0xf5, 0x8c, 0xb1, 0xe3, 0x1d, 0xf6, 0xe2, 0x2e, 0x82,
    0x66, 0xca, 0x60, 0xc0, 0x29, 0x23, 0xab, 0x0d, 0x53, 0x4e, 0x6f, 0xd5, 0xdb, 0x37, 0x45,
    0xde, 0xfd, 0x8e, 0x2f, 0x03, 0xff, 0x6a, 0x72, 0x6d, 0x6c, 0x5b, 0x51, 0x8d, 0x1b, 0xaf,
    0x92, 0xbb, 0xdd, 0xbc, 0x7f, 0x11, 0xd9, 0x5c, 0x41, 0x1f, 0x10, 0x5a, 0xd8, 0x0a, 0xc1,
    0x31, 0x88, 0xa5, 0xcd, 0x7b, 0xbd, 0x2d, 0x74, 0xd0, 0x12, 0xb8, 0xe5, 0xb4, 0xb0, 0x89,
    0x69, 0x97, 0x4a, 0x0c, 0x96, 0x77, 0x7e, 0x65, 0xb9, 0xf1, 0x09, 0xc5, 0x6e, 0xc6, 0x84,
    0x18, 0xf0, 0x7d, 0xec, 0x3a, 0xdc, 0x4d, 0x20, 0x79, 0xee, 0x5f, 0x3e, 0xd7, 0xcb, 0x39,
    0x48,
]

# 系统参数
_SM4_FK = [0xa3b1bac6, 0x56aa3350, 0x677d9197, 0xb27022dc]

# 固定参数
_SM4_CK = [
    0x00070e15, 0x1c232a31, 0x383f464d, 0x545b6269,
    0x70777e85, 0x8c939aa1, 0xa8afb6bd, 0xc4cbd2d9,
    0xe0e7eef5, 0xfc030a11, 0x181f262d, 0x343b4249,
    0x50575e65, 0x6c737a81, 0x888f969d, 0xa4abb2b9,
    0xc0c7ced5, 0xdce3eaf1, 0xf8ff060d, 0x141b2229,
    0x30373e45, 0x4c535a61, 0x686f767d, 0x848b9299,
    0xa0a7aeb5, 0xbcc3cad1, 0xd8dfe6ed, 0xf4fb0209,
    0x10171e25, 0x2c333a41, 0x484f565d, 0x646b7279
]


class SM4Suite(object):

    def __init__(self, key, mode, **kwargs):
        """
        :param key: 16字节bytes类型的密钥
        :param iv: 16字节bytes类型的初始化向量
        :param nonce: 16字节bytes类型的计数器种子
        """
        self.key = key
        self.mode = mode
        self.iv = kwargs.get('iv', None)
        self.nonce = kwargs.get('nonce', None)

        if self.mode in _need_iv_list:
            assert self.iv, "IV is not initialized"
        if self.mode in _need_nonce_list:
            assert self.nonce, "nonce is not initialized"

        self.is_encrypt = True
        self.is_encrypt_cfb = True
        self.rk = [0] * 32
        self._key_expand()

    def encrypt(self, data):
        """加密模式"""
        # 如果之前的模式不是加密模式，需要改变加解密状态
        if not self.is_encrypt:
            # 设置标识
            self.is_encrypt = True
            # 重新生成轮密钥
            self._key_expand()

        # 由于CFB加密模式的特殊性，轮密钥不需要重新生成，但是需要有加解密状态的表示
        if self.mode == SM4_CFB_MODE:
            self.is_encrypt_cfb = True

        # 将字节类型转换为列表
        data = list(data)
        # 将数据进行填充
        data = padding(data)
        # 加密
        data = self.__getattribute__(self.mode)(data, 0, len(data))
        # 将数据转化成字节流返回
        return bytes(data)

    def decrypt(self, data):
        """解密模式"""
        # 判断加密模式，需要改变时改变加解密状态
        need_to_be_decrypt = self.mode in _need_reverse_list
        if need_to_be_decrypt == self.is_encrypt:
            self.is_encrypt = False
            self._key_expand()

        # 由于CFB加密模式的特殊性，轮密钥不需要重新生成，但是需要有加解密模式的表示
        if self.mode == SM4_CFB_MODE:
            self.is_encrypt_cfb = False

        # 将字节类型转换为列表
        data = list(data)
        # 解密
        data = self.__getattribute__(self.mode)(data, 0, len(data))
        # 将数据去填充
        data = unpadding(data)
        # 将数据转化成字节流返回
        return bytes(data)

    @staticmethod
    def _T(data, is_key_generate=False):
        """
        公共的T函数运算.
        :param data: uint32类型，初始数据.
        :param is_key_generate: bool类型，用于判断是否是密钥生成过程中的迭代运算.
        :return: uint32类型，运算产生的新数据.
        """
        data = uint32_to_bytes_list(data)
        # 将数据分四组，每组1个字节
        data[0] = _SM4_BOXES_TABLE[data[0]]
        data[1] = _SM4_BOXES_TABLE[data[1]]
        data[2] = _SM4_BOXES_TABLE[data[2]]
        data[3] = _SM4_BOXES_TABLE[data[3]]
        b = bytes_list_to_uint32(data)
        # 根据情况进行不同的移位异或运算
        data = b ^ (rot_l_n(b, 13)) ^ (rot_l_n(b, 23)) if is_key_generate else \
            b ^ (rot_l_n(b, 2)) ^ (rot_l_n(b, 10)) ^ (rot_l_n(b, 18)) ^ (rot_l_n(b, 24))
        return data

    def _iterate(self, data, is_key_generate=False):
        """
        公共的迭代运算.
        :param data: uint128类型，初始数据.
        :param is_key_generate: bool类型，用于判断是否是密钥生成过程中的迭代运算.
        :return: list类型，列表每一项代表一个uint32，迭代结果列表.
        """
        res = [0] * 36
        # 将数据分四组，每组4个字节
        res[0] = bytes_list_to_uint32(data[0:4])
        res[1] = bytes_list_to_uint32(data[4:8])
        res[2] = bytes_list_to_uint32(data[8:12])
        res[3] = bytes_list_to_uint32(data[12:16])
        # 如果是密钥扩展，需要和FK进行异或
        if is_key_generate:
            res[0:4] = xor_list(res[0:4], _SM4_FK)
        # 迭代运算32次
        for i in range(32):
            # 公共部分
            T_input = res[i + 1] ^ res[i + 2] ^ res[i + 3]
            # 根据情况选择异或CK还是rk
            T_input ^= _SM4_CK[i] if is_key_generate else self.rk[i]
            # 进行T函数运算
            res[i + 4] = res[i] ^ (self._T(T_input, is_key_generate))
        return res

    def _key_expand(self):
        """
        密钥扩展运算.
        :return: list类型，列表每一项代表一个uint32，轮密钥列表.
        """
        # 迭代产生rk
        K = self._iterate(self.key, True)
        # 将列表K中第五个之后的所以数据赋值给rk
        self.rk = K[4:]
        # 如果是解密，需要将rk中的数据进行反序
        if not self.is_encrypt:
            for idx in range(16):
                t = self.rk[idx]
                self.rk[idx] = self.rk[31 - idx]
                self.rk[31 - idx] = t

    def _crypto(self, text):
        """
        加解密计算.
        :param text: list类型，列表每一项代表一个Byte，待加解密的16字节数据.
        :return: list类型，列表每一项代表一个Byte，返回加解密后的16字节数据.
        """
        # 进行加解密运算前必须先进行密钥扩展
        assert self.rk != [0] * 32, "Round key is not generated"
        # 进行加解密运算
        x = self._iterate(text)
        # 最后的结果经过反序变换进行拼接
        return reduce(lambda a, b: a + uint32_to_bytes_list(b), x[35:31:-1], [])

    def _ecb_mode(self, input_data, index, length):
        """
        ECB模式加解密.
        :param input_data: list类型，待加解密的数据.
        :param index: int类型，待加解密数据的起始位置.
        :param length: int类型，待加解密数据的长度.
        :return: list类型，返回加解密后的数据.
        """
        # 输出结果
        output_data = []

        # 当数据剩余长度大于16时，继续进行分组加密
        while length > 0:
            output_data += self._crypto(input_data[index:index + 16])
            index += 16
            length -= 16

        #  返回加解密后的字节类型数据
        return output_data

    def _cbc_mode(self, input_data, index, length):
        """
        CBC模式加解密.
        :param input_data: list类型，待加解密的数据.
        :param index: int类型，待加解密数据的起始位置.
        :param length: int类型，待加解密数据的长度.
        :return: list类型，返回加解密后的数据.
        """
        # 将iv附加到输出结果前面，方便计算
        iv = list(self.iv)
        output_data = iv
        input_data = iv + input_data

        # 当数据剩余长度大于16时，继续进行分组加密
        if self.is_encrypt:
            while length > 0:
                output_data += self._crypto(xor_list(input_data[index + 16:index + 32], output_data[index:index + 16]))
                index += 16
                length -= 16
        else:
            while length > 0:
                output_data += xor_list(self._crypto(input_data[index + 16:index + 32]), input_data[index:index + 16])
                index += 16
                length -= 16

        #  返回加解密后的字节类型数据
        return output_data[16:]

    def _cfb_mode(self, input_data, index, length):
        """
        CFB模式加解密.
        :param input_data: list类型，待加解密的数据.
        :param index: int类型，待加解密数据的起始位置.
        :param length: int类型，待加解密数据的长度.
        :return: list类型，返回加解密后的数据.
        """
        # 将iv附加到输出结果前面，方便计算
        iv = list(self.iv)
        output_data = iv
        input_data = iv + input_data

        # 当数据剩余长度大于16时，继续进行分组加密
        if self.is_encrypt_cfb:
            while length > 0:
                output_data += xor_list(self._crypto(output_data[index:index + 16]), input_data[index + 16:index + 32])
                index += 16
                length -= 16
        else:
            while length > 0:
                output_data += xor_list(self._crypto(input_data[index:index + 16]), input_data[index + 16:index + 32])
                index += 16
                length -= 16

        #  返回加解密后的字节类型数据
        return output_data[16:]

    def _ofb_mode(self, input_data, index, length):
        """
        OFB模式加解密.
        :param input_data: list类型，待加解密的数据.
        :param index: int类型，待加解密数据的起始位置.
        :param length: int类型，待加解密数据的长度.
        :return: list类型，返回加解密后的数据.
        """
        # 将iv附加到输出结果前面，方便计算
        output_data = list(self.iv)

        # 当数据剩余长度大于16时，继续进行分组加密
        while length > 0:
            output_data += self._crypto(output_data[index:index + 16])
            index += 16
            length -= 16

        return xor_list(output_data[16:], input_data)

    def _ctr_mode(self, input_data, index, length):
        """
        CTR模式加解密.
        :param input_data: list类型，待加解密的数据.
        :param index: int类型，待加解密数据的起始位置.
        :param length: int类型，待加解密数据的长度.
        :return: list类型，返回加解密后的数据.
        """
        # 初始化计数器和掩码
        counter = 0
        mask = 0xffffffffffffffffffffffffffffffff

        # 输出结果
        output_data = []

        # 当数据剩余长度大于16时，继续进行分组加密
        while length > 0:
            output_data += self._crypto(((int(self.nonce, 16) + counter) & mask).to_bytes(16, 'big'))
            index += 16
            length -= 16

        return xor_list(output_data, input_data)


if __name__ == '__main__':
    test_key = os.urandom(16)
    test_nonce = os.urandom(16)
    test_data = b'1234567890abcdef_padding\x00\x01\x00'

    suite = SM4Suite(test_key, SM4_CBC_MODE, iv=test_key, nonce=test_nonce)
    cipher = suite.encrypt(test_data)
    plain = suite.decrypt(cipher)
    print([hex(i) for i in cipher])
    print(plain)
