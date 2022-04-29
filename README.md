# Bitcoin Connector 
This repository holds the code for a bitcoin connector. 
Using this reporsitory the a node in the bitcoin network can be connected to and the messages can begin to be received from the connected node and displayed in a terminal. 

This readme is divided into two sections:

1. Running the Script - This explains how to run the ```main.py``` script and what it is doing.
2. BitcoinConnector Class - An explanation of the functions in the BitcoinConnector class located in ```Lib\BitcoinConnector.py```

## Running the Script 
The main run script is located in the file ```main.py```. All the modules used in this repository are default Python packages and hence why there is no requirements.txt file in the repo. 

To run the script execute the following command below. 
```
python main.py 
```
The script instatiates an instance of the ```BitcoinConnector``` class which is located in the file ```Lib\BitcoinConnector.py```.
A node in the bitcoin network is connected to at the ip address ```1.116.110.123```.
This ip address was chosen as it was quite quick at sending messages to the host machine the script is running on from testing.

If you want to change the IP address you can by changing the variable ```ip``` in the script. You can also set it to ```None``` and the script will perform a DNS lookup to the address ```seed.bitcoin.sipa.be``` to get an IP address. 

The script will output that it has succfully connected to the given node and the handshake between the host machine and peer node has succfully taken place by printing something like the following example to the terminal below. 

```
(MyEnv) C:\Users\warre\OneDrive\Documents\College\Msc\Secure Systems\AssignmentThree>python main.py
Socket connected succfully to node 1.116.110.123 on port 8333
Initial version payload message sent at 2022-04-29 14:33:41.780054

Response from initial version message, contains version and verack
b'\xf9\xbe\xb4\xd9version\x00\x00\x00\x00\x00f\x00\x00\x00&\x95/\xde\x80\x11\x01\x00\x08\x04\x00\x00\x00\x00\x00\x003\xe9kb\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\xff\xffYd)\x18\xf7y\x08\x04\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\r\x99\x89\xbb\xb9\xcf\x9a\xda\x10/Satoshi:22.0.0/\x9c3\x0b\x00\x01'

Verack response to version sent at 2022-04-29 14:33:42.032977
```
Once the initial connection has been made the node which we have connected to will begin to send messages. 

```main.py``` will parse three kind of messages, an ```inv```, a ```tx``` and a ```block``` message. 
In the ```main.py``` you can change what messages get output to the console by changing the variables below to ```True``` or ```False```. By default they are all set to ```True``` to show all messages but it is helpful to change them if you just want to focus on an idividual message type. 

```
# displayInv   - When True will display inv messages to terminal, set False it will not 
# displayTx    - When True will display tx messages to the terminal, set False it will not 
# displayBlock - When True will display block messages to the terminal, set False it will not 
displayInv   = False
displayTx    = False
displayBlock = True
```

A [inv](https://en.bitcoin.it/wiki/Protocol_documentation#inv) message will advertise the knowledge of one or more events and contains inventory vectors on events. These inventory vectors will contain the hashes relating to given events see full details [here](https://en.bitcoin.it/wiki/Protocol_documentation#Inventory_Vectors). These hashes can be used as the payload for a [getdata](https://en.bitcoin.it/wiki/Protocol_documentation#getdata) message to get more information on a given event. The script using the functions in the ```BitcoinConnector``` class only extracts ```MSG_TX``` and ```MSG_BLOCK``` type events. 

Example output from the script of a ```inv``` message being parsed below.  

```
*******************INV MESSAGE*******************
Length of payload = 613 Bytes
Inv Count = 17
Length of inventory vectors = 612 Bytes

Summary Inventory Vectors Received
        Number of MSG_TX vectors = 17
        Number of MSG_BLOCK vectors = 0
****************END OF INV MESSAGE***************
```

A [tx](https://en.bitcoin.it/wiki/Protocol_documentation#tx) message is in response from a [getdata](https://en.bitcoin.it/wiki/Protocol_documentation#tx) message sent with a payload containing one or more ```MSG_TX``` objects. It contains information on a single transaction which is either processed or being processed (depends upon lock_time). 

Example output from the script of a ```tx``` message being parsed below.

```
*******************TX MESSAGE*******************
Length of payload  = 258 Bytes
version (4 Bytes)  = 1 or b'\x01\x00\x00\x00'
tx_in count (1 Byte)  = 1 or b'\x01'
        Transaction input 0
                previous_output (36 Bytes) = b"\x10\x1f\xb5\xa8\xfa\xd3K\x95'\x01\x0b\x1c\x95q\xb1\xa2\xc27t\xf4\xdd\x18\r\xc5\xa5\\\xf0/\x19\xca\xc05\x02\x00\x00\x00"
                script length (1 Bytes) = 107 or b'k'
                script signature (107 Bytes) = b'H0E\x02!\x00\xd8\x9aso*\xd0\xe4\xae\xa3$\xdee\xe3\xc3"\xa4O\xa0\xca\x19\x97q{V\xe7@W\xda\xc9e\x86\xf4\x02 \x0c\x8b\x17\xfcg\x83!dw\x9fa\x02\x8e\xff\x03\x07(XQ\xcc\xcd\x17q\xee\xa0\x1b\xc3\x19\xe1\x0eqN\x81!\x02H\x8d\xa0\x10\xd9\xd6\xb71\xce\x0c(nU]s\'~\xe7\xa2\xa8n\xcb\xc4\xc7\xb4"O\x81\xf3\xb6\xd8,'
                sequence (4 Bytes) = b'\xff\xff\xff\xff'
tx_out count (1 Bytes) = 3 or b'\x03'
        Transaction Output 0
                value (8 Bytes) = 19592 Satoshis (0.00019592 BTC)
                pk_script length (1 Bytes) = 25 or b'\x19'
                pk_script (25 Bytes) = b'v\xa9\x14~\x02\xb7\x86\xf1v\xf2\x93\xf5\x9c\xf5^1\xf9\xb3`S\xb8\x84\x95\x88\xac'
        Transaction Output 1
                value (8 Bytes) = 255200 Satoshis (0.002552 BTC)
                pk_script length (1 Bytes) = 23 or b'\x17'
                pk_script (23 Bytes) = b'\xa9\x14^P.\x8b{\xd1\xf6\xcc\xb0\x86aH9\xad\xf8\x97\xce\x1f\xa2(\x87'
        Transaction Output 2
                value (8 Bytes) = 9510772 Satoshis (0.09510772 BTC)
                pk_script length (1 Bytes) = 25 or b'\x19'
                pk_script (25 Bytes) = b'v\xa9\x14\xc3\xba\xedK\x98\xcba\xcc\n\x11h\xce\x99Q_\xb9\xd7\xff\x87\xfd\x88\xac'
lock_time (4 Bytes) = b'\x00\x00\x00\x00' transaction not locked
******************* END OF TX MESSAGE *******************
```


A [block](https://en.bitcoin.it/wiki/Protocol_documentation#block) message is in response from a [getdata](https://en.bitcoin.it/wiki/Protocol_documentation#tx) message sent with a payload containing one or more ```MSG_BLOCK``` objects. It gives details on a new block mined which contains a number of successfully verified transactions. 

Example output from the script of a ```block``` message being parsed below. The individual transactions in a block where not parsed as it is the same information as looking at a single transaction, getting an overview of the block itself was more interesting. 

```
*******************BLOCK MESSAGE*******************
Length of payload  = 4260 Bytes
version (4 Bytes)  = b'\x00\x00\x00 '
prev_block hash (32 Bytes) = b'\xbb\xd8\xe8;\xb9\r\x90\xdch\xaa\xad\xc4\xa0g\xb1\xb0\xd7Lu\xd0Yt\x05\x00\x00\x00\x00\x00\x00\x00\x00\x00'
merkleRoot (32 Bytes) = b"\x88\xea\xa08ge\x85'N\x96dh\x1cF\x93r\xd0b\x03\xc4\x8c\xbdA/\xf0\x9e\x82\xd4\xb5\xd0\r4"
timestamp (4 Bytes) = 2022-04-29 13:44:09
difficulty target (4 Bytes) = 386495093 or b'ur\t\x17'
nonce (4 Bytes) = 2289053436 or b'\xfc.p\x88'
txn count (2 Bytes) = 2613 or b'5\n'
****************END OF BLOCK MESSAGE***************
```

## BitcoinConnector 
This class is located in the file ```Lib\BitcoinConnector.py``` and performs the operations of connecting to the bitcoin network and parsing the messages. 

The functions in the class are listed below. 

### __init__
```
Description:
        initiliaser method for the class 
Inputs:
        protocolVersion - The version of bitcoin the node you are connecting to is using see https://developer.bitcoin.org/reference/p2p_networking.html#protocol-versions
        magic           - The magic value for given network, default to mainent 
        lookUpDomain    - This is where to get the actual IP address of the node to connect to, need to obtain an IP address from active node 
        port            - Port for the connecting peer node 
        ip              - Can set this if you want to use a specific IP instead of performing a lookup, was added because IP address you got at seed.bitcoin.sipa.be was sometimes slow to send updates, if got a good one wanted to keep the IP 
```
### getSocket
```
Description:
        Gets a socket object which can be used to open a connection to a bitcon node
Returns:
        s - An instance of the class socket https://docs.python.org/3/library/socket.html
```
### getIPAddress
```
Description:
        Performs a lookup to get a Bitcoin nodes IP address using the lookUpDomain instance variable and socket class. This is by default set to seed.bitcoin.sipa.be.
Returns:
        ip - The ip address of the given bitcoin node 
```
### connectSocket
```
Description:
        Connects the socket class instance stored in self.socket to a given IP address at the location
        stored in the variable self.peerIP and at the port stored in the variable self.peerPort
```
### createMessage
```
Description:
        This function will create a message in the format specified for the bitcoin protocol. 
        A message contains 5 components 
                1. magic    - Magic value for given bitcoin network
                2. command  - The command name 
                3. length   - The lenght of the payload
                4. checksum - first 4 bytes of the hash of the hash of the payload
                5. payload  - The actual data to be sent 
Inputs:
        commandName (string)  - The name of the command, for example "version".
        payload (byte string) - The payload in bytes to send.   
Returns
        message (byte string) - The messsage data in a byte string 
```
### sendMessage
```
Description:
        Sends a message to the connected peer at self.peerIP using the socket established.
Inputs:
        message - A message which has been created with the function createMessage
        msgName - Optional string which will be used in a console log to print name of message. Useful for keeping track of message flows.
```
### connectToPeer
```
Description:
        This function performs the connection to the given node to start receiving messages. 
        To establish a connection there are three steps:
                1. Send version message - The machine wishing to connect sends a version message to the node to connect to. 
                2. Receieve resposne - The response will be a version message and a ver ack message acknowlwdging the initial version message.
                3. Send verack - A version acknowledgment is then sent to the node to acknowledge the version message received.
```
### createVerackCommand
```
Description:
            Creates a verack payload command which is used to acknowledge the version command sent from the node. 
            A verack command is just a message with an empty payload. This function really just creates an empty 8 
            byte payload. 
Returns
        verackCMD - Empty 4 byte payload 
```
### createVersionCommand
```
Description:
            Creates the version message for the bitcoin transaction.
            The version message is sent initially to the node which is being connected to.  
            The verion message contains 9 components:
                1. version      - The bitcoin protocol version 4 bytes
                2. services     - Capabailities to be enabled on a node 8 bytes 
                3. timestamp    - A UNIX timestamp in seconds 8 bytes 
                4. addr_recv    - Network address of recieving node 26 bytes 
                5. addr_from    - Network address of the sending node 26 bytes
                6. nonce        - Random nonce generated for every message 8 bytes
                7. user_agent   - The user agent used, variable string length
                8. start_height - The last block recieved by the sending node 4 bytes
                9. relay        - Boolean for the remote peer to announce every transaction or not  
Returns:
        versionCMD (Byte String) - The version command which can be sent as a payload for a message 
```
### parseInvMsg
```
Description:
        This function parses the inv messages which a node will send with updates. 
        The updates vary and depend upon the type of inventory vector sent. 
        There can be up to 50,000 inevnetory vectors sent in a given inv message. 
        See https://en.bitcoin.it/wiki/Protocol_documentation#inv for detail on inv messages.
        The inv message consists of 2 main components 
            count     - This is the count of the number of inventory vectors in this message https://en.bitcoin.it/wiki/Protocol_documentation#Variable_length_integer
            inventory - These are the inventory vectors which contain a code (4 bytes) on the type of event and then a hash (32 bytes) which can be used to request data on this event. 
        The type of inventory events this function parses is specifically MSG_TX and MSG_BLOCK events.
Inputs:
    msg - This is a inv message recieved to be parsed 
    display - Boolean, if set true will print out summary on the inventory message parsed
Returns:
    finalVecs = Byte string which contains the MSG_TX and MSG_BLOCK type inventory vectors which can be used in a getdata message to get information on new transactions and blocks
```
### getInventoryVectors
```
Description:
        This function returns a list with each element being an inventory vectory.
Inputs:
        inventory - Byte string of inventory vectors, must be a multiple of 36 as there is 36 bytes in an individual inventory vector
Returns:
        inventoryVecs - A list where each element is a 36 byte sting reppresenting an inventory vector
```
### createGetDataCMD
```
Description:
        Creates the getdata payload for the getdata message https://en.bitcoin.it/wiki/Protocol_documentation#getdata
        This payload is sent in response to a inv message to obtain more information on a given event identified by its 
        hash in the inventory vec associated with this event. 
        The getdata payload has two components:
            count     - The number of inventory vecs in the payload 
            inventory - These are inventory vectors obtained from an inv message and contain the hashes of the events we want more information on. 
Inputs:    
        inventoryVecs - Byte string containg the inventory vectors. These are returned from the function parseInvMsg.
Returns:
        payload - The payload for the getdata message.
```
### parseTXMsg
```
Description:
    This function parses a message of the type tx see https://en.bitcoin.it/wiki/Protocol_documentation#tx
    The payload of the message will vary in length however the main components are:
        version      - Transaction data format version
        flag         - Indicates presence of witness data (not parsed in this function)
        tx_in count  - The number of transaction inputs
        tx_in        - The transaction inputs
        tx_out count - The number of transaction outputs
        tx_out       - The transaction outputs 
        tx_witness   - List of witness (not parsed in this function)
        lock_time    - The block number or time at which the block is unlocked 
Inputs:
    msg     - Byte string including the message header and payload
    display - Boolean, set true if you want parsed message displayed to output 
Returns:
    payload         - Byte string, entire payload of message 
    version         - Byte string, version of payload 
    txInCount       - Byte string, number of input transactions
    transactionsIn  - List, each element in the list is a dictionary realting to a tx_in data type in Bitcoin docs
    txOutCount      - Byte string, number of output transactions 
    transactionsOut - List, each element in the list is a dictionary realting to a tx_out data type in bitcoin docs 
    lockTime        - Byte string, relating to the lock time 
```
### displayTransaction
```
Description:
    Displays the deatails of a tx message. 
    It is called from the parseTXMsg message when the display input is set to true. 
Inputs:
    payload         - Byte string, entire payload of message 
    version         - Byte string, version of payload 
    txInCount       - Byte string, number of input transactions
    transactionsIn  - List, each element in the list is a dictionary realting to a tx_in data type in Bitcoin docs
    txOutCount      - Byte string, number of output transactions 
    transactionsOut - List, each element in the list is a dictionary realting to a tx_out data type in bitcoin docs 
    lockTime        - Byte string, relating to the lock time 
```
### parseBlockMsg
```
Description:
    This function parses a block message received after a getdata message. 
    The message contains information on a new block mined 
    The payload of the message contains 8 components:
        1. version     - The block version information 
        2. prev_block  - The hash value of the previous block 
        3. merkle_root - The reference to a Merkle tree collection which is a hash of all transactions related to this block.
        4. timestamp   - The timestamp for when this block was created 
        5. bits        - The calculated difficulity of the block.
        6. nonce       - The nonce used to generate this block 
        7. txn_count   - The number of transactions in this block. 
        8. txns        - The transactions in the format of tx message payloads 
Inputs:
    msg     - Byte string of the msg of type block        
    display - Boolean, set true if want block information printed
Returns:
    payload     - Byte string of the entire payload 
    version     - Byte string relating to the version 
    prevBlock   - Byte string of the previous blocks hash 
    merkle_root - Byte string of the merkle tree collection 
    timestamp   - Byte string of the timestamp of when the block was created
    bits        - Byte string of the difficulity target for the block
    nonce       - Byte string of the nonce to generate this block 
    txn_count   - Byte string of the transaction count
```
### displayBlock
```
Description:
    Used to print out the information related to a block message.
    It is called from the function parseBlockMsg wen display is set true. 
Inputs:
    payload     - Byte string of the entire block message payload
    version     - Byte string relating to the version 
    prevBlock   - Byte string of the previous blocks hash 
    merkle_root - Byte string of the merkle tree collection 
    timestamp   - Byte string of the timestamp of when the block was created
    bits        - Byte string of the difficulity target for the block
    nonce       - Byte string of the nonce to generate this block 
    txn_count   - Byte string of the transaction count
```
