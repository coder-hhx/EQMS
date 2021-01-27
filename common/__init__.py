import hashlib
import base64
import os

BASE_URL = 'http://127.0.0.1:8000/'

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def make_pwd(txt):
    md5_ = hashlib.md5(txt.encode('utf-8'))
    md5_.update('&$@839#*+'.encode('utf-8'))

    return base64.b32encode(md5_.hexdigest().encode('utf-8')).decode('utf-8')
