from flask import Flask, request
import json
import requests
from time import time
import rsa
from nbc_lib import Block, Transaction
import socket

app = Flask(__name__)

# Hyperparameters
BOOTSTRAP = 1  # hyperparameter to determine the bootstrap node
N = 5  # hyperparameter / number of total nodes connected to nbc network

# Finding our local IP address by pinging the 0th node/gateway on port 80
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("192.168.0.1", 80))
my_ip = s.getsockname()[0]
my_port = 5000

# Generating RSA key pair
pubkey, privkey = rsa.newkeys(1024, poolsize=2)
# Check if there is a node running on port 5000
with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
    if ps.connect_ex((my_ip, 5000)) == 0:
        my_port = 5001

my_id = {'id': '0', 'ip': my_ip, 'port': my_port, 'e': f'{pubkey.e}', 'n': f'{pubkey.n}'}

# TODO add newcomer to nodes list as dict or not?
nodes = []
# Create genesis block and genesis transaction, only for node 0
if BOOTSTRAP:
    nodes = [my_id]
    genesis_transaction = Transaction(0, pubkey, 100 * N, None, [], None)
    genesis_block = Block(0, time(), (genesis_transaction), 0, -1)



current_node_id = 0

@app.route("/join-network", methods=['POST'])
def join_network():
    global current_node_id
    if request.method == 'POST':
        rec = json.loads(request.json)
        ip = rec['ip']
        port = rec['port']
        e = rec['e']
        n = rec['n']
        print(f'Connection from: {ip}:{port}')
        current_node_id += 1
        return json.dumps({'cni': f'{current_node_id}'})


if __name__ == '__main__':
    # Node makes join request and joins the network
    if not BOOTSTRAP:
        x = requests.post('http://192.168.0.1:5000/join-network', json=json.dumps(my_id)).json()
        my_id['id'] = x['cni']
        print(my_id['id'])
    app.run(host=my_ip, port=my_id['port'], debug=False)
