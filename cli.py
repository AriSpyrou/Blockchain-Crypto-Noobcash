import re
import requests

help = '''
************************************* HELP PAGE *************************************
Commands:
> t (recepient_id) (amount) |  Perform a transaction for "amount" to "recipient_id"
> view                      |  Display last transactions
> balance                   |  Display the balance of each wallet on the network
> help                      |  Display the help page
> exit                      |  Exit the CLI
*************************************************************************************
'''

while True:
    cmd = input("Noobcash client > ")

    pattern = re.compile("t\s(id\d)\s(\d+)")
    match = pattern.match(cmd)

    if match:
        recipient = match.group(1)
        amount = match.group(2)
        print(recipient, amount)
        r = requests.post(url = "http://192.168.0.1:5000/new-transaction", json =  {"receiver_address": recipient, "amount": amount})
        print(r.status_code)

    if cmd == "view":
        pass
        # view_transactions()

    if cmd == "balance":
        pass
        # wallet_balance()

    if cmd == "help":
        print(help)

    if cmd == "poutses":
        r = requests.get(url = "http://192.168.0.1:5000/get-chain")
        print(r.json())


if __name__ == "__main__":
    main()