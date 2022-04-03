import json
from Crypto.Hash import SHA256
from rsa import PublicKey


class Block:
    def __init__(self, index, timestamp, transactions, nonce, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.current_hash = SHA256.new(
            bytearray(str([self.timestamp, self.transactions, self.nonce]), 'utf-8')).hexdigest()
        self.previous_hash = previous_hash

    @classmethod
    def from_json(cls, json_str):
        x = json.loads(json_str)
        return Block.from_dict(x)

    @classmethod
    def from_dict(cls, x):
        if isinstance(x['transactions'], str):
            trans = json.loads(x['transactions'])
        elif isinstance(x['transactions'], list):
            trans = x['transactions']
        return cls(x['index'], x['timestamp'], trans, x['nonce'], x['previous_hash'])

    def to_dict(self):
        # print('---------------------------')
        # print('---------------------------')
        # if isinstance(self.transactions, list):
        #     if len(self.transactions) == 0:
        #         print([])
        #     else:
        #         print(type(self.transactions), type(self.transactions[0]), len(self.transactions))
        # else:
        #     print(type(self.transactions))
        # print('---------------------------')
        # print('---------------------------')
        if isinstance(self.transactions, list):
            if self.transactions == []:
                trans = []
            elif isinstance(self.transactions[0], str):
                trans = [json.loads(item) for item in self.transactions]
            elif isinstance(self.transactions[0], Transaction):
                trans = [item.to_json() for item in self.transactions]
            elif isinstance(self.transactions[0], dict):
                trans = self.transactions
        elif isinstance(self.transactions, dict):
            trans = self.transactions
        elif isinstance(self.transactions, Transaction):
            trans = [self.transactions.to_dict()]
        return {'index': self.index,
                'timestamp': self.timestamp,
                'transactions': trans,
                'nonce': self.nonce,
                'current_hash': self.current_hash,
                'previous_hash': self.previous_hash}

    def to_json(self):
        return json.dumps(self.to_dict())


class Transaction:
    def __init__(self, sender_address, receiver_address, amount, t_inputs, t_outputs=None, signature=None):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.t_id = SHA256.new(bytearray(str([self.sender_address, self.receiver_address, self.amount]), 'utf-8')).hexdigest()
        self.t_inputs = t_inputs
        self.t_outputs = t_outputs
        self.signature = signature

    @classmethod
    def from_json(cls, json_str):
        x = json.loads(json_str)
        return Transaction.from_dict(x)

    @classmethod
    def from_dict(cls, x):
        if x['sender_address'] != 0:
            e, n = x['sender_address'].split(':')
            sender = PublicKey(int(n), int(e))
        else: sender = 0
        e2, n2 = x['receiver_address'].split(':')
        receiver = PublicKey(int(n2), int(e2))
        for out in x['transaction_outputs']:
            n, e = out['recipient'].split(':')
            out['recipient'] = PublicKey(int(n), int(e))
        if x['transaction_inputs']:
            for out in x['transaction_inputs']:
                n, e = out['recipient'].split(':')
                out['recipient'] = PublicKey(int(n), int(e))
        if x['signature']:
            x['signature'] = bytearray(x['signature'], 'ISO-8859-1')
        return cls(sender, receiver, x['amount'], x['transaction_inputs'], x['transaction_outputs'], x['signature'])

    def to_dict(self):
        out = {'sender_address': self.sender_address,
                'receiver_address': self.receiver_address,
                'amount': self.amount,
                'transaction_id': self.t_id,
                'transaction_inputs': self.t_inputs,
                'transaction_outputs': self.t_outputs,
                'signature': self.signature}
        if isinstance(out['sender_address'], PublicKey):
            out['sender_address'] = f'{self.sender_address.e}:{self.sender_address.n}'
        if isinstance(out['receiver_address'], PublicKey):
            out['receiver_address'] = f'{self.receiver_address.e}:{self.receiver_address.n}'
        for item in out['transaction_outputs']:
            if not isinstance(item['recipient'], str):
                item['recipient'] = f"{item['recipient'].e}:{item['recipient'].n}"
        if out['signature']:
            out['signature'] = out['signature'].decode('ISO-8859-1')
        if out['transaction_inputs']:
            for inp in out['transaction_inputs']:
                inp['recipient'] = f'{self.sender_address.e}:{self.sender_address.n}'
        return out

    def to_json(self):
        return json.dumps(self.to_dict())