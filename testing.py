from random import Random
from flask import Flask, request
import json
import requests
from time import time_ns as time, sleep
import rsa
from nbc_lib import Block, Transaction
import socket
from threading import Timer
from Crypto.Hash import SHA256
from collections import deque
import secrets

app = Flask(__name__)

def generate_wallet():
    # poolsize is related to the # of CPU threads available
    pubkey, privkey = rsa.newkeys(1024, poolsize=2)
    return pubkey, privkey


def create_transaction(receiver_address, amount):
    pos = int(my_id['id'])
    unspent = utxo[pos]
    enough = False
    tmp = 0
    for i, un in enumerate(unspent):
        tmp += un['amount']
        if tmp >= amount:
            enough = True
            t_inputs = unspent[:i+1]
            diff = tmp - amount
            break
    if enough:
        trans = Transaction(sender_address=pubkey, receiver_address=receiver_address, amount=amount, t_inputs=t_inputs)
        t_out1 = {'id': SHA256.new(bytearray(str([time(), trans.t_id, receiver_address, amount]), 'utf-8')), 't_id': trans.t_id, 'recipient': receiver_address, 'amount': amount}
        t_out2 = {'id': SHA256.new(bytearray(str([time(), trans.t_id, pubkey, diff]), 'utf-8')), 't_id': trans.t_id, 'recipient': pubkey, 'amount': diff}
        trans.t_outputs = [t_out1, t_out2]
        del unspent[:i+1]
        unspent.append(t_out2)
        pos = find_index_by(public_key=receiver_address)
        unspent = utxo[pos]
        unspent.append(t_out1)
        trans.signature = sign_transaction(trans, privkey)
        # Send the mofo to everyone in the bitconnetwork
        broadcast_transaction(trans)
        # Add the mofo to the queue
        trans_queue.append(trans)
        if len(trans_queue) >= C:
            mine_block()
    else:
        print('Not enough money in wallet!')


def sign_transaction(trans, privkey):
    # hash and sign message in one operation
    signature = rsa.sign(str([trans.sender_address, trans.receiver_address, trans.amount]).encode("utf-8"), privkey, 'SHA-256')
    return signature


def broadcast_transaction(trans):
    for node in nodes:
        if node['id'] == my_id['id']:
            continue
        retry_attempts = 0
        while retry_attempts < 5:
            req = requests.post(f"http://{node['ip']}:{node['port']}/get-transaction", json=trans.to_json())
            if req.ok:
                break
            else:
                print('Transaction failed to be sent. Retrying...')
                sleep(2 ** retry_attempts)
                retry_attempts += 1


def verify_signature(trans, pubkey, signature):
    """
    Verifies the signature matches the transaction. 
    This is executed by the receiver.

    inputs:
    trans - signed transaction
    pubkey - public key of the sender
    signature - signature generated by sign_transaction

    outputs:
    True if valid, False if invalid
    """
    try:
        rsa.verify(str([trans.sender_address, trans.receiver_address, trans.amount]), signature, pubkey)
        return True
    except rsa.VerificationError as e:
        return False


def validate_transaction(trans, pubkey, signature):
    # If signature checks out go ahead
    if verify_signature(trans, pubkey, signature):
        # Look for the node that corresponds to the public key
        pos = find_index_by(public_key=pubkey)
        # Link the two lists
        unspent = utxo[pos]
        ok_flag = True
        tmp = []
        # List with all IDs from unspent
        unspent_ids = [item['id'] for item in unspent]
        # For every input we want to valid
        for i, inp in enumerate(trans.t_inputs):
            input_id = inp['id']
            # Check to see if it is in unspent_ids
            if input_id not in unspent_ids:
                # If even 1 is invalid then stop looping
                ok_flag = False
                break
            else:
                # If it is found then add it to a temp list
                tmp.append(unspent_ids.index(input_id))
        # If all inputs are found and everything is a-ok
        if ok_flag:
            # Loop through the temp list we made earlier with the positions of UTXOs that need to be removed
            for i in tmp:
                del unspent[i]
            # Add the output of the transaction to the spender ie the change from the removed UTXOs
            unspent.append(trans.t_outputs[1])
            # Find the receiver in nodes and
            pos = find_index_by(public_key=trans.receiver_address)
            # Add the output of the transaction to the receiver ie the money transfered
            unspent = utxo[pos]
            unspent.append(trans.t_outputs[0])


def wallet_balance(id):
    """
    Inputs: wallet id in 'idX' format or 
    """
    if isinstance(id, str):
        if 'id' in id:
            idx = find_index_by(id=id)
        else:
            idx = int(id)
    else:
        idx = id

    unspent = utxo[idx]
    return sum([item['amount'] for item in unspent])


def mine_block():
    transactions = trans_queue[C:]
    previous_block = blockchain[-1]

    new_idx = previous_block.index + 1
    # Possibly add PID and/or random sleep
    timestamp = time()
    previous_hash = previous_block.current_hash
    while True:
        nonce = secrets.randbits(128)
        temp = Block(new_idx, timestamp, transactions, nonce, previous_hash)
        if temp.current_hash.hexdigest()[:D] == D*'0':
            print(temp.current_hash.hexdigest())
            print('Suitable hash found!')
            return temp


def send_nodes_to_all(nodes):
    while True:
        if len(nodes) == N:
            for node in nodes[1:]:
                print(f"Sent node list to {node['id']}")
                requests.post(f"http://{node['ip']}:{node['port']}/get-nodes", json=json.dumps(nodes))
            break
        else:
            sleep(5)


def find_index_by(id=None, public_key=None):
    """
    Finds a node in nodelist 

    Input: id in 'idX' format or public key

    Returns: an index in nodelist
    """
    if id and 'id' in id:
        num = id[2:]
        for i, node in enumerate(nodes):
            if node['id'] == num:
                return i
    elif public_key:
        for node in nodes:
            if str(public_key.e) == node['e'] and str(public_key.n) == node['n']:
                return int(node['id'])


@app.route("/join-network", methods=['POST'])
def join_network():
    if request.method == 'POST':
        rec = json.loads(request.json)
        ip = rec['ip']
        port = rec['port']
        e = rec['e']
        n = rec['n']
        print(f'Connection from: {ip}:{port}')
        c_id = len(nodes)
        nodes.append({'id': c_id, 'ip': ip, 'port': port, 'e': e, 'n': n})
        print(f'Added node: {c_id}: {ip}:{port} to network')

        return json.dumps({'cni': f'{c_id}'})


@app.route("/get-nodes", methods=['POST'])
def get_nodes():
    if request.method == 'POST':
        nodes = json.loads(request.json)
        return 'OK'


@app.route("/get-transaction", methods=['POST'])
def get_transaction():
    if request.method == 'POST':
        trans = Transaction.from_json(json.loads(request.json))
        if validate_transaction(trans):
            print("Valid transaction received")
            trans_queue.appendleft(trans)
            if len(trans_queue) >= C:
                mine_block()
        else:
            print("Invalid transaction")
    return 'OK'


# Finding our local IP address by pinging the 0th node/gateway on port 80
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("192.168.0.1", 80))
my_ip = s.getsockname()[0]
my_port = 5000

# Hyperparameters
if my_ip == "192.168.0.1":  
    BOOTSTRAP = 1  # hyperparameter to determine the bootstrap node
else:
    BOOTSTRAP = 0
N = 2  # hyperparameter / number of total nodes connected to nbc network
C = 1 # hyperparameter / capacity
D = 4 # hyperparameter / difficulty

# Generating RSA key pair
pubkey, privkey = generate_wallet()
# Check if there is a node running on port 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if s.connect_ex((my_ip, 5000)) == 0:
        my_port = 5001

my_id = {'id': '0', 'ip': my_ip, 'port': my_port, 'e': f'{pubkey.e}', 'n': f'{pubkey.n}'}

utxo = [[] for _ in range(N)]
nodes = []
trans_queue = []
blockchain = []

# Create genesis block and genesis transaction, only for node 0
if BOOTSTRAP:
    # Add bootstrap's id to nodes
    nodes = [my_id]
    # Create the genesis transaction
    # (class) Transaction(sender_address, receiver_address, amount, t_inputs=None, t_outputs=None, signature=None)
    genesis_transaction = Transaction(0, pubkey, 100 * N, None, [], None)
    # This is for code compatibility and so that the next line isn't super long
    trans = genesis_transaction
    # Add the single output of the genesis transaction to it
    genesis_transaction.t_outputs = [{'id': SHA256.new(bytearray(str([time(), trans.t_id, pubkey, 100 * N]), 'utf-8')), 't_id': trans.t_id, 'recipient': pubkey, 'amount': 100 * N}, {}]
    utxo[0].append(genesis_transaction.t_outputs[0])
    # Create the genesis block
    # (class) Block(index, timestamp, transactions, nonce, previous_hash)
    genesis_block = Block(0, time(), (genesis_transaction), 0, -1)
    blockchain.append(genesis_block)

if __name__ == '__main__':
    create_transaction(pubkey, 50)
