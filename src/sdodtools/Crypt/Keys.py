import subprocess
import hashlib
import random

# openssl enc -aes-256-cbc -pbkdf2 -iter 20000 -in hello -out hello.enc -k meow
# openssl enc -d -aes-256-cbc -pbkdf2 -iter 20000 -in hello.enc -out hello.out

# KEY=$( echo -n "0123456789ABC" | md5sum -b | sed 's/ .*//')
# IV=$( echo -n "CBA12345" | md5sum -b | sed 's/ .*//')

# openssl enc -a -aes-256-cbc -in cleartext -out cleartext.enc -K "$K" -iv "$IV"
# openssl enc -d -a -aes-256-cbc -in cleartext.enc -K "$K" -iv "$IV"

##############################################################################
##############################################################################
### Classes
##############################################################################
##############################################################################

##############################################################################
##############################################################################

class KeyIV:

    ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ+*#'-_.:,;!$%&/()=?"

    @classmethod
    def generate(cls, *args, salt=None, key_length=64, iv_length=32, count=200000, **kwargs):

        password = ''.join(random.choice(cls.ALPHABET) for i in range(64))
        password = str.encode(password)

        return cls.from_password(password=password, salt=salt, key_length=key_length, iv_length=iv_length, count=count, **kwargs)

    @classmethod
    def from_password(cls, password, *args, salt=None, key_length=64, iv_length=32, count=200000, **kwargs):
  
        if salt is None:

            salt = ''.join(random.choice(cls.ALPHABET) for i in range(16))
            salt = str.encode(salt)

        d = b''
        d_i = b''

        while len(d) < key_length + iv_length:
            
            h = d_i + password + salt
            i = count

            while i > 0:

                h = hashlib.md5(h).hexdigest()
                h = str.encode(h)
                i -= 1

            d_i = h
            d += d_i

        return cls(*args, key=d[:key_length], iv=d[key_length:key_length+iv_length], **kwargs)

    @classmethod
    def from_bytes(cls, b, *args, **kwargs):

        if not b.startswith(b'['):

            idx_start = b.find(b'[')
            b = b[idx_start + 1:]

        idx_stop = b.find(b']') 
        key, iv = b[:idx_stop].split(b"|")

        return cls(key=key, iv=iv), b[idx_stop + 1:]

    def __init__(self, key, iv) -> None:

        self.key = key
        self.iv = iv
        self.signature = "<" +  ".".join([type(self).__module__, type(self).__qualname__]) + ">"

    def __bytes__(self) -> bytes:

        return '{sig}[{key}|{iv}]'.format(sig=self.signature, key=self.key.decode(), iv=self.iv.decode()).encode()
    
    def __str__(self) -> str:

        return '{sig}[{key}|{iv}]'.format(sig=self.signature, key=self.key.decode(), iv=self.iv.decode())
    
    def __repr__(self) -> str:  

        return f"{self.signature}[{self.key.decode()}|{self.iv.decode()}]"
    
    def encrypt(self, data):

        cmd = subprocess.Popen(args=['openssl', 'enc', '-a', '-aes-256-cbc', '-K', self.key.decode(), '-iv', self.iv.decode()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)
        (stdout, stderr) = cmd.communicate(input=data)

        return cmd.returncode, stdout, stderr

    def decrypt(self, data):

        data += b'\n'
        cmd = subprocess.Popen(args=['openssl', 'enc', '-d', '-a', '-aes-256-cbc', '-K', self.key.decode(), '-iv', self.iv.decode()], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=False)
        (stdout, stderr) = cmd.communicate(input=data)

        return cmd.returncode, stdout, stderr
