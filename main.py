### House Keeping ###
# Name           - Warren Kavanagh 
# Description    - Main script which connects to another node in the bitcoin network and then listens out for inv, tx and block messages 

## Imports ##
# BitcoinConnector - Class developed for this project which provides funtionality for conntecting to bitcoin network and parsing messages 
from Lib.BitcoinConnector import BitcoinConnector

if __name__ == '__main__':
    # ip - this is the ip address of the node which is to be connected to, it is set here as I found this IP to be quite quick at sending messages
    #      The value of ip can be changed to None if you want to script to perform a DNS lookup for seed.bitcoin.sipa.be to get a bitcoin node IP if this ip is offline 
    ip = '1.116.110.123'
    # connector - This is an instance of the BitcoinConnector class developed for this project, see the file Lib/BitcoinConnector.py for more information on this
    connector = BitcoinConnector(ip=ip)
    # Call the connectToPeer function, this performs the sending of the initial version message, recieveing the version and verack response and then sending a verack response 
    connector.connectToPeer()

    # displayInv   - When True will display inv messages to terminal, set False it will not 
    # displayTx    - When True will display tx messages to the terminal, set False it will not 
    # displayBlock - When True will display block messages to the terminal, set False it will not 
    displayInv   = True
    displayTx    = True
    displayBlock = True

    # This will enter a loop forever which can only be escaped when ctrl+c is entered on the keyboard
    # the exception will be caught and will print "program exited" to the terminal 
    try:
        # Loop forever 
        while True:
            # Recover the message from the node, msg will be a byte string containing a bitcoin message 
            # The node will be sending messages as the connection has already been established using the connectToPeer function called earlier
            msg = connector.socket.recv(2048)
            # Inv message type - These message will include updates on the network including tx and block hashes which can be used to get tx and block messages. See https://en.bitcoin.it/wiki/Protocol_documentation#inv
            if msg[0:7] == b'\xf9\xbe\xb4\xd9inv':
                # Parse the inv messages and extract out the inventory vectors of type MSG_TX and MSG_BLOCK
                inventoryVecs = connector.parseInvMsg(msg,display=displayInv)
                # Now create a getdata message using the inventory vectors for transactions and blocks to gather more information on them 
                # The payload for getdata message is built using the function createGetDataCMD
                # The message is built using the function createMessage, this adds the headers
                getDataMSG = connector.createMessage('getdata',connector.createGetDataCMD(inventoryVecs))
                # Now send the getdata message, the optional second input is a string which will print "getdata message sent <time>" to console when its sent
                connector.sendMessage(getDataMSG,'getdata message')
            # transaction message type - This type of message contains information on transactions. See https://en.bitcoin.it/wiki/Protocol_documentation#tx
            elif msg[0:6] == b'\xf9\xbe\xb4\xd9tx':
                # Parse the transaction message, set the display True or False to display the parsed message  
                connector.parseTXMsg(msg,display=displayTx)
            # block message type - This type of message is related to a new block being mined and contains information on it. See https://en.bitcoin.it/wiki/Protocol_documentation#block 
            elif msg[0:9] == b'\xf9\xbe\xb4\xd9block':
                # Parse the block message, set the display True or False to display the parsed message  
                connector.parseBlockMsg(msg,display=displayBlock)
    # This exception is just here so that a stack trace is not printed when you press ctrl+c to stop loop 
    except KeyboardInterrupt:
        print("Program exited")
