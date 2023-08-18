from cryptography.fernet import Fernet # symmetric encryption

# info 암호화 하라고하면.... 하자

class SimpleEnDecrypt:
    def __init__(self, key=None):
        if key is None: # 키가 없다면
            key = Fernet.generate_key() # 키를 생성한다
        self.key = key
        self.f   = Fernet(self.key)
    
    def encrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.encrypt(data) # 바이트형태이면 바로 암호화
        else:
            ou = self.f.encrypt(data.encode('utf-8')) # 인코딩 후 암호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
    def decrypt(self, data, is_out_string=True):
        if isinstance(data, bytes):
            ou = self.f.decrypt(data) # 바이트형태이면 바로 복호화
        else:
            ou = self.f.decrypt(data.encode('utf-8')) # 인코딩 후 복호화
        if is_out_string is True:
            return ou.decode('utf-8') # 출력이 문자열이면 디코딩 후 반환
        else:
            return ou
        
if __name__ == "__main__":    
    k = b'WpUoE8m10EAHX93N9pz_Z_yoyY68Uo6TBFFTMxiOzS0='


    simpleEnDecrypt = SimpleEnDecrypt(key=k)
    # encrypt_text  = simpleEnDecrypt.encrypt("Kyobovbs11!")
    # print(f"encrypt_text : {encrypt_text}")

    decrypt_text = "gAAAAABk3spVWd4fThd88YjbgvWJfsZ8T-hVxrgQJrFTisX73Yo4rj58SrVl0-Gd5Saoh0lj_3FsVlrAXrwZjfbkU3LtyZ3leA=="
    decrypt_text  = simpleEnDecrypt.decrypt(decrypt_text)
    print(f"decrypt_text : {decrypt_text}")


