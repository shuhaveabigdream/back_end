import hashlib
from random import randint

numbers=[str(i) for i in range(0,9)]
chart=[chr(i) for i in range(97,123)]
salt_buf=numbers+chart

def create_token(tar):
    salt=''.join([salt_buf[i] for i in range(randint(5,10))])
    return hashlib.md5((tar+salt).encode()).hexdigest()

if __name__=="__main__":
    print(create_token('jack'))