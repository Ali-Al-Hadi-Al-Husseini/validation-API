from hashlib import sha256
from random import randrange

characters = """zxcvbnmasdfghjklqwertyuiop1234567890QWERTYUIOP|ASDFGHJKL:?><MNBVCXZ!@#$%^&*"""

def generate_key():
    key = []
    for _ in range(32):
        ran = randrange(0,len(characters))
        key.append(characters[ran])

    return "".join(key)
    
def hashText(text):
    return sha256(text.encode()).hexdigest()
    

