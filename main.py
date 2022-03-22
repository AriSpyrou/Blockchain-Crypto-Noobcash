import rsa
from Crypto.Hash import SHA256
from nbc_lib import Block, Transaction
from time import time


NODE_ID = 0
N = 5
TODO = None
pubkey, privkey = rsa.newkeys(1024, poolsize=2)
genesis_transaction = Transaction(0, pubkey, 100*N, None, None, None)
genesis_block = Block(0, time(), (genesis_transaction), 0, -1)