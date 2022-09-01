from base64 import b64decode
from base64 import b64encode
from Crypto.Cipher import AES # pip install pycrypto==2.6.1
import time


class ECBCipher(object):
    '''
    定义一个基于AES的ECB模式的加解密类
    '''
    def __init__(self, key):
        '''
        定义构造方法，初始化key和加解密对象
        :params key:长度必须为16位
        '''
        if len(key) % 16 != 0:
            raise ValueError('key的长度必须为16的倍数。')
        self.key = key
        self.__cipher = AES.new(self.key.encode(),  AES.MODE_ECB)
    
    def __pad(self, s): # 私有方法
        '''
        定义PKCS7填充的私有方法，用于对目标进行补位填充
        '''
        return s + (AES.block_size - len(s) % AES.block_size) * chr(AES.block_size - len(s) % AES.block_size)
    
    def __unpad(self, s):
        '''
        定义去除填充的私有方法，用于对目标进行解码得到原始值
        '''
        return s[:-ord(s[-1:])]

    def encrypted(self, msg):
        '''
        定义加密方法，对目标进行加密，并返回一个byte类型的字符串
        :params msg:需要加密的明文
        '''
        try:
            return b64encode(self.__cipher.encrypt(self.__pad(msg).encode())).decode()
        except:
            return None

    def decrypted(self, encode_str):
        '''
        定义解密方法，对目标进行解密，并返回一个解密得到的字符串
        :params encode_str:需要解密的密文
        '''
        try:
            decode_str = self.__unpad(self.__cipher.decrypt(b64decode(encode_str))).decode()
            return decode_str if decode_str else None
        except:
            return None


if __name__ == '__main__':
    ecb_obj =  ECBCipher('16ed9ecc7d9011eab9c63c6aa7c68b67')
    encode_text = ecb_obj.encrypted('e2d8fae47d4c11ea942cc8d9d2066a43+%s' % str(int(time.time())))
    decode_text = ecb_obj.decrypted(encode_text)
    print('加密:', encode_text)
    print('解密:', decode_text)