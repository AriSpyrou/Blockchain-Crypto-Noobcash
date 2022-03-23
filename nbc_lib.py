import json
from Crypto.Hash import SHA256


class Block:
    def __init__(self, index, timestamp, transactions, nonce, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.transactions = transactions
        self.nonce = nonce
        self.current_hash = SHA256.new(
            bytearray(str([self.timestamp, self.transactions, self.nonce]), 'utf-8'))
        self.previous_hash = previous_hash

    @classmethod
    def from_json(cls, json_str):
        x = json.loads(json_str)
        return cls(x.index, x.timestamp, x.transactions, x.nonce, x.previous_hash)

    @classmethod
    def from_dict(cls, x):
        return cls(x['index'], x['timestamp'], x['transactions'], x['nonce'], x['previous_hash'])

    def __hash__(self):
        return SHA256.new(bytearray(str([self.timestamp, self.transactions, self.nonce]), 'utf-8'))

    def to_dict(self):
        return {'index': self.index,
                'timestamp': self.timestamp,
                'transactions': self.transactions,
                'nonce': self.nonce,
                'current_hast': self.current_hash,
                'previous_hast': self.previous_hash}

    def to_json(self):
        return json.dumps(self.to_dict())


class Transaction:
    def __init__(self, sender_address, receiver_address, amount, t_inputs, t_outputs, signature):
        self.sender_address = sender_address
        self.receiver_address = receiver_address
        self.amount = amount
        self.t_id = SHA256.new(bytearray(
            str([self.sender_address, self.receiver_address, self.amount]), 'utf-8'))
        self.t_inputs = t_inputs
        self.t_outputs = t_outputs
        self.signature = signature

    @classmethod
    def from_json(cls, json_str):
        x = json.loads(json_str)
        return cls(x.sender_address, x.receiver_address, x.amount, x.t_inputs, x.t_outputs, x.signature)

    @classmethod
    def from_dict(cls, x):
        return cls(x['sender_address'], x['receiver_address'], x['amount'], x['t_inputs'], x['t_outputs'], x['signature'])

    def __hash__(self):
        return SHA256.new(bytearray(str([self.sender_address, self.receiver_address, self.amount]), 'utf-8'))

    def to_dict(self):
        return {'sender_address': self.sender_address,
                'receiver_address': self.receiver_address,
                'amount': self.amount,
                'transaction_id': self.t_id,
                'transaction_inputs': self.t_inputs,
                'transaction_outputs': self.t_outputs,
                'signature': self.signature}

    def to_json(self):
        return json.dumps(self.to_dict())
