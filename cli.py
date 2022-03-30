import os 
import re

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

    pattern = re.compile("t\sid(\d)\s(\d+)")
    match = pattern.match(cmd)

    if match:
        recipient = match.group(1)
        amount = match.group(2)
        # create_transaction(recipient, amount)

    if cmd == "view":
        pass
        # view_transactions()

    if cmd == "balance":
        pass
        # wallet_balance()

    if cmd == "help":
        print(help)

if __name__ == "__main__":
    main()