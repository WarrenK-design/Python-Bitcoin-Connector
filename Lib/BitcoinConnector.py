### House Keeping ###
# Name           - Warren Kavanagh 
# Email          - C16463344@MYTuDublin.ie
# Student Number - C16463344 

## Description ##
#   This file holds the class BitcoinConnector
#   The class provides the functionality to connect to a bitcoin node either at a specified IP address or using the lookup domain seed.bitcoin.sipa.be
#   It performs the handshake with the node to initiate the connection of sending the version meessage, recieving the version and verack, then sending the verack back.
#   It also provides functionality for parsing messages for displaying information on inv, transaction and block meesages.


## Imports ##
# time    - https://docs.python.org/3/library/time.html
# socket  - https://docs.python.org/3/library/socket.html
# struct  - https://docs.python.org/3/library/struct.html
# os      - https://docs.python.org/3/library/os.html
# hashlib - https://docs.python.org/3/library/hashlib.html
# datetime - https://docs.python.org/3/library/datetime.html
import time
import socket
import struct
import os
import hashlib
from datetime import datetime

class BitcoinConnector:
    def __init__(self,protocolVersion=70015,magic=b'\xf9\xbe\xb4\xd9',lookUpDomain='seed.bitcoin.sipa.be',peerPort=8333,ip=None):
        '''
        Description:
            initiliaser method for the class 
        Inputs:
            protocolVersion - The version of bitcoin the node you are connecting to is using see https://developer.bitcoin.org/reference/p2p_networking.html#protocol-versions
            magic           - The magic value for given network, default to mainent 
            lookUpDomain    - This is where to get the actual IP address of the node to connect to, need to obtain an IP address from active node 
            port            - Port for the connecting peer node 
            ip              - Can set this if you want to use a specific IP instead of performing a lookup, was added because IP address you got at seed.bitcoin.sipa.be was sometimes slow to send updates, if got a good one wanted to keep the IP 
        '''
        # Set the class variables 
        self.protocolVersion = protocolVersion
        self.magic           = magic
        self.lookUpDomain    = lookUpDomain
        self.peerPort        = peerPort
        # Create a socket instance, will allow us to send messages to the node and recieve messages through a socket 
        self.socket= self.getSocket()
        # Set the IP address of the peer node we are going to connect to from the lookUpDomain 
        # If ip is passed use the ip passed 
        if ip:
            self.peerIP = ip
        else:
            # If a specific ip is not passed then do a DNS lookup
            self.peerIP = self.getIPAddress()
        # Connect the socket to the peer node 
        self.connectSocket()

    def getSocket(self):
        '''
        Description:
            Gets a socket object which can be used to open a connection to a bitcon node
        Returns:
            s - An instance of the class socket https://docs.python.org/3/library/socket.html
        '''
        try:
            # Create the socket instance and return it 
            s= socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            return s 
        except socket.error as err:
            print("Error in creating the socket")

    def getIPAddress(self):
        '''
        Description:
            Performs a lookup to get a Bitcoin nodes IP address using the lookUpDomain instance variable and socket class 
        Returns:
            ip - The ip address of the given bitcoin node 
        '''
        try:
            # Use the socket function gethostbyname to perform a DNS lookup to get an IP address for a bitcoin node 
            ip = socket.gethostbyname(self.lookUpDomain)
            return ip
        except socket.gaierror:
            print(f'Could not obtain a node IP address from the look up domain {self.lookUpDomain}')

    def connectSocket(self):
        '''
        Description:
            Connects the socket class instance stored in self.socket to a given IP address at the location
            stored in the variable self.peerIP and at the port stored in the variable self.peerPort
        '''
        try:
            self.socket.connect((self.peerIP,self.peerPort))
            print(f'Socket connected successfully to node {self.peerIP} on port {self.peerPort}')
        except:
            print(f'Could not connect to peer at IP {self.peerIP} on port {self.peerPort}')

    def createMessage(self,commandName,payload):
        '''
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
        '''
        # magic - 4 bytes 
        #   The magic value for the origin netowrk, we are using the mainnet 0xD9B4BEF9 sent little endian 
        #   This is held in the self.magic class variable
        # command - 12 bytes, char type 
        #   This is the command name as an ascii charathers
        #   Needs to be padded out to 12 bytes for example if commandName=version then 
        #   command=version\0\0\0\0\0
        #   Encode the commandName as a bytes and add the padding based on lenght 
        command = f'{commandName}'.encode() + ((12-len(commandName)) * b'\x00')
        # lenght - 4 bytes 
        #   This is the lenght of the payload 
        length = struct.pack('I',len(payload))
        # checksum - 4 bytes 
        #   This is the first 4 bytes of the hash of a hash
        #   First take the SHA256 of payload and then the SHA256 of result SHA256(SHA256(payload))
        checksum = hashlib.sha256(payload)
        checksum = hashlib.sha256(checksum.digest()).digest()[0:4]
        # Create the message by adding the individual components and the payload
        message = self.magic + command + length + checksum + payload 
        return message 

    def sendMessage(self,message,msgName=None):
        '''
        Description:
            Sends a message to the connected peer at self.peerIP using the socket established.
        Inputs:
            message - A message which has been created with the function createMessage
            msgName - Optional string which will be used in a console log to print name of message. Useful for keeping track of message flows.
        '''
        try:
            # Send the message using the socket object 
            self.socket.send(message)
            # Print a message if the msgName has been set 
            print(f'{msgName} sent at {datetime.now()}') if msgName else ''
        except Exception as e:
            print(e)
            if msgName:
                print(f'Error sending message {msgName} shown below to peer {self.peerIP}:{self.peerPort}\n{message}')
            else:
                print(f'Error sending message shown below to peer {self.peerIP}:{self.peerPort}\n{message}')

    def connectToPeer(self):
        '''
        Description:
            This function performs the connection to the given node to start receiving messages. 
            To establish a connection there are three steps:
                1. Send version message - The machine wishing to connect sends a version message to the node to connect to. 
                2. Receieve resposne - The response will be a version message and a ver ack message acknowlwdging the initial version message.
                3. Send verack - A version acknowledgment is then sent to the node to acknowledge the version message received. 
        '''
        # Step 1. Send Version message
        #   To initiate the flow we first have to send a version message to the node we want to connect to 
        #   The payload can be created using the createVersionCommand funtion 
        #   The full message including the payload is created using the createMessage function 
        #   The message is then sent using the sendMessage function 
        version_message = self.createMessage('version',self.createVersionCommand())
        self.sendMessage(version_message,'Initial version payload message')
        # Step 2. Receieve the response
        #   The node we are trying to connect to will responed with a version message and then 
        #   a verack message. These can be recieved using the recv function. The first version reponse seems to cutoff so  
        #   so call recv twice and join them to get the two messages in versionRes
        msgVersionResponse = self.socket.recv(1024)
        msgVerackResponse  = self.socket.recv(1024)
        versionRes = msgVersionResponse + msgVerackResponse
        print(f'\nResponse from initial version message, contains version and verack \n{versionRes}\n')
        # Step 3. Send verack
        #   The final step is to acknowledge the version response sent by sending a version acknowledgment 
        #   (verack) payload. The verack payload is created using the createVerackCommand function, it is just an empty payload
        #   The message is then created with createMessage and send with sendMessage 
        verack_message = self.createMessage('verack',self.createVerackCommand())
        self.sendMessage(verack_message,'Verack response to version')

    def createVerackCommand(self):
        '''
        Description:
            Creates a verack payload command which is used to acknowledge the version command sent from the node. 
            A verack command is just a message with an empty payload. This function really just creates an empty 8 
            byte payload. 
        Returns
            verackCMD - Empty 4 byte payload 
        '''
        ## The payload for a verack is an empty 4 bytes 
        return b'\x00\x00\x00\x00'

    def createVersionCommand(self):
        '''
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
        '''
        # Version - 4 Bytes
        #   The protocol versin being used by node, we are connecting to, this is in the class instance variable self.protocolVersion
        # Services - 8 bytes
        #   Refers to capabailities you want to enable on your "node"
        #   For this assignemnt we are specfying that we are not a full node and we just want transactions 
        #   If we where to implement a full node this will need to be changed 
        services = b'\x00'*8
        # timestamp - 8 bytes 
        #   Unix timestamp in seconds using the time function, double 8 bytes long 
        timestamp = struct.pack('d',time.time())
        # addr_recv - 26 bytes 
        #   This is composed of 4 smaller components which make a network address (see https://en.bitcoin.it/wiki/Protocol_documentation#Network_address)
        #       1. time (4 bytes)     - The time -> THIS IS NOT USED IN VERSION MESSAGE HENCE LENGHT 26 BYTES FOR addr_recv 
        #       2. services (8 bytes) - The same as the services mentioned above 
        #       3. IPv6/4 (16 Bytes)  - The IP address of the node which will recieve this message, the one we will be getting transaction data from, if 1pv4 12 bytes of 0's and then 4 bytes of ipv4
        #       4. port (2 bytes)     - The port number for the node message is being sent to 
        service_addr_recv    = b'\x00'*8
        ip_address_addr_recv = (b'\x00'*12)+socket.inet_aton(self.peerIP)
        port_addr_recv       = struct.pack('H',8333) # H is unsigned short which is 2 bytes 
        addr_recv = service_addr_recv + ip_address_addr_recv + port_addr_recv
        # addr_from - 26 bytes 
        #   This is composed of the same 4 smaller components mentioned above for the addr_recv which make a network address
        #   1. time (4 bytes)     - The time -> THIS IS NOT USED IN VERSION MESSAGE HENCE LENGHT 26 BYTES FOR addr_from
        #   2. services (8 bytes) - The same as services mentioned above
        #   3. IPv6/4 (16 Bytes)  - The ip address of the transmitting node, can be set to 127.0.0.1 
        #   4. Port   (2 bytes)   - The port number, 8333 for bitcoin 
        service_addr_from    = b'\x00'*8
        ip_address_addr_from = (b'\x00'*12)+socket.inet_aton('127.0.0.1')
        port_addr_from       = struct.pack('H',8333) # H is unsigned short which is 2 bytes 
        addr_from = service_addr_from + ip_address_addr_from + port_addr_from
        # nonce - 8 Bytes 
        #   This is just a random 8 bytes sent with the version message 
        nonce = os.urandom(8)
        # User Agent - Variable lenght string 
        #   Not sending user agent filed just set to 0 
        user_agent = b'\x00'
        # Start Height - 4 bytes 
        #   This is the height of the last block the transmitting node recieved, in our case havent recived any yet 
        start_height = struct.pack('i',0)
        # Relay - 1 Byte 
        #   Set true so that the remote peer should announce transactions
        relay = b'\x01'
        # Add the individual components 
        versionCMD = struct.pack("i", self.protocolVersion) + services + timestamp + addr_recv + addr_from + nonce + user_agent + start_height + relay 
        return versionCMD

    def parseInvMsg(self,msg,display=True):
        '''
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
        '''
        # Sometimes the message will ony contain the first 24 bytes for some reason
        # Ensure that we have the full amount first, if we only have 24 bytes
        # call recv again the reamining message will be there 
        payload = ''
        # Get the length of the payload from bytes 16 to 20
        lenghtOfPayload = int.from_bytes(msg[16:20],"little")
        # Sometimes only first 24 bytes is sent first 
        if (len(msg) == 24):
            # need to call recover again to get the next part of the message which will be the payload 
            # only accept the next lenghtOfPayload bytes specifiec in the header 
            payload  = self.socket.recv(lenghtOfPayload) 
        else:
            # We got more than 24 bytes, but just to be sure we havent got more than we need
            # only use the lenght of the payload specificied in the header as the source of truth 
            payload = msg[24:24+lenghtOfPayload]
        # invCount        - Number of inventory messages 
        # inventoryLenght - This is how many bytes if in the inventory, each inventory vector is 36 bytes in lenght so this value should be 36 x invCount 
        invCount        = payload[0]
        inventoryLength = len(payload[1:]) 
        # Ensure that the inventory lenght is equal to 36 x inventory count
        # The inventory count tells you how many inventory items you have
        # Each inventory item is 36 bytes in lenght so for a full correct message 
        # we must have 36 x inventory count to trust it, just a precaution seems to be reliable 
        if((36*invCount) == inventoryLength):
            # inventoryVectors - A list where each eleement is a 36 byte inventory vector
            inventoryVectors = self.getInventoryVectors(payload[1:])
            # blockVecsCount  - Used to keep track of the number of block vecs
            # transactionVecs - Used to keep track of the number of transaction vectors 
            # finalVecs       - This is a byte string containg the MSG_TX and MSG_BLOCK vectors
            blockVecsCount       = 0
            transactionVecsCount = 0
            finalVecs       = b''
            # Now iterate through the inventory vectors 
            # Extracting information based upon the docs on inventory vectors https://en.bitcoin.it/wiki/Protocol_documentation#Inventory_Vectors 
            for vec in inventoryVectors:
                # vecType - This is the first 4 bytes of an inventory vector 
                vecType = int.from_bytes(vec[0:4],"little")
                # We only want to parse MSG_TX (vecType = 1) and MSG_BLOCK (vecType=2) data 
                if (vecType == 1):
                    transactionVecsCount +=1
                    finalVecs+=vec
                elif (vecType == 2):
                    blockVecsCount +=1
                    finalVecs+=vec
            # Print out a summary of the inventiry vectorys received 
            if(display):
                print('*******************INV MESSAGE*******************')
                print(f'Length of payload = {len(payload)} Bytes')
                print(f'Inv Count = {invCount}')
                print(f'Length of inventory vectors = {inventoryLength} Bytes')
                print(f'\nSummary Inventory Vectors Received\n\tNumber of MSG_TX vectors = {transactionVecsCount}\n\tNumber of MSG_BLOCK vectors = {blockVecsCount}\n****************END OF INV MESSAGE***************')
            # Return the inventory vectors which can be used to send a getdata message to get tx and block messages 
            return finalVecs
         
    def getInventoryVectors(self,inventory):
        '''
        Description:
            This function returns a list with each element being an inventory vectory.
        Inputs:
            inventory - Byte string of inventory vectors, must be a multiple of 36 as there is 36 bytes in an individual inventory vector
        Returns:
            inventoryVecs - A list where each element is a 36 byte sting reppresenting an inventory vector
        '''
        return list(inventory[0+i:36+i] for i in range(0,len(inventory), 36))

    def createGetDataCMD(self,inventoryVecs):
        '''
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
        '''
        # Check if there are vecs availble, it seems sometimes none are sent very rare
        if inventoryVecs:
            # count - The number of inventoryvecs present in the payload 
            count = int(len(inventoryVecs)/36)
            count = bytes([count])
            # payload - the count and the inventory vectors 
            payload = count+inventoryVecs
            return payload
        else:
            # Return an emty payload 
            return b'\x00'

    def parseTXMsg(self,msg,display=True):
        '''
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
        '''
        # Sometimes the message will ony contain the first 24 bytes for some reasn 
        # Ensure that we have the full amount first, if we only have 24 bytes
        # call recv again the reamining message will be there 
        payload = ''
        # Get the length of the payload from bytes 16 to 20
        lenghtOfPayload = int.from_bytes(msg[16:20],"little")
        # Sometimes only first 24 bytes is sent first 
        if (len(msg) == 24):
            # need to call recover again to get the next part of the message which will be the payload 
            # only accept the next lenghtOfPayload bytes specifiec in the header 
            payload  = self.socket.recv(lenghtOfPayload) # CONVER TFROM UNISGEDN INT 
        else:
            # We got more than 24 bytes, but just to be sure we havent got more than we need
            # only use the lenght of the payload specificied in the header as the source of truth 
            payload = msg[24:24+lenghtOfPayload]
        # version - First 4 bytes of the payload 
        version = payload[0:4]
        # flag    = payload[4:5] ### THIS NEVER SEEMED TO BE PRESENT IN THE MESSAGE SO LEFT OUT 
        # txInCount - The number of transaction inputs 
        txInCount = payload[4:5]
        # tx start is where the transaction data starts from in bytes from start of payload
        txstart = 5
        if txInCount == b'\xfd':
            # 2 byte integer 
            txInCount = payload[5:7] # 2 byte integer
            # update tx start 
            txstart = 7
        elif txInCount == b'\xfe':
            # 4 byte integer 
            txInCount = payload[5:9] # 4 byte integer 
            # update tx start 
            txstart = 9
        elif txInCount == b'\xff':
            # 8 byte integer 
            txInCount = payload[5:13] # 8 byte integer
            # update tx start 
            txstart = 13
        # transactionsIn - This will be a list of transactions where each element is a dictionaryrealting to a transaction 
        transactionsIn = [] 
        # Iterate through each of the transactions using the transaction count information we have for the number of transactions 
        for i in range(int.from_bytes(txInCount,"little")):
            # The previous output is 36 bytes long 
            previousOutput = payload[txstart:txstart+36]
            # The script lenght, 1 byte lenght of script 
            scriptLength  = payload[txstart+36:txstart+37]
            # The script length is optional so only enter this loop if you need to 
            if int.from_bytes(scriptLength,"little") > 0:
                # The script signature is gotten from the scriptLength 
                scriptSignature = payload[txstart+37:txstart+37+int.from_bytes(scriptLength,"little")]
                # The next 4 bytes is then the sequence 
                sequence = payload[txstart+37+int.from_bytes(scriptLength,"little"):txstart+4+37+int.from_bytes(scriptLength,"little")]
                # Append the traansaction to the list of transactions 
                transactionsIn.append({'previous_output':previousOutput,'script length':scriptLength,'signature script':scriptSignature,'sequence':sequence})
                # Need to update tx start -> The start of next tx is the end of the previous tx 
                txstart = txstart+4+37+int.from_bytes(scriptLength,"little")
            else:
                # No script means we only need to take the next 4 bytes which is the sequence 
                sequence = payload[txstart+37:4+txstart+37]
                # Append the traansaction to the list of transactions 
                transactionsIn.append({'previous_output':previousOutput,'script length':scriptLength,'signature script':None,'sequence':sequence})
                # Need to update the start of transaction data
                txstart = 4+txstart+37
        # the tx _out count is the next byte wich is the number of transaction outputs
        txOutCount = payload[txstart:1+txstart]
        # The start of the txout mesages i.e 1 byte on from the end of the transactions, 1 byte in middle being the txOutCount
        txOutStart = 1+txstart
        if txOutCount == b'\xfd':
            # 2 byte integer, +1 because the first byte is the var int coding byte 
            txOutCount = payload[txOutStart+1:3+txOutStart] # 2 byte integer
            # update tx outstart by 2 bytes  
            txOutStart = 3+txOutStart
        elif txOutCount == b'\xfe':
            # 4 byte integer, +1 because the first byte is the var int coding byte
            txOutCount = payload[txOutStart+1:5+txOutStart] # 4 byte integer 
            # update tx start by 4 bytes
            txOutStart = 5+txOutStart
        elif txOutCount == b'\xff':
            # 8 byte integer, +1 because the first byte is the var int coding byte
            txOutCount = payload[1+txOutStart:9+txOutStart] # 8 byte integer
            # update tx out start by 8 bytes
            txOutStart = txOutStart+9
            # Python runs out of memeory if we where to parse these transactions, it is a really big number so just output how many transaction threre are
            # happens very rarely but instead of a stack trace print out this  
            if display:
                print('*******************TX MESSAGE*******************')
                print(f'Warning: 8 byte transaction out count, Python will run out of memory if details shown, summary of transaction shown below. {int.from_bytes(txOutCount,"little")} transaction outputs.')
                print(f'Length of payload  = {len(payload)} Bytes')
                print(f'version ({len(version)} Bytes)  = {int.from_bytes(version,"little")} or {version}')
                print(f'tx_in count ({len(txInCount)} Byte)  = {int.from_bytes(txInCount,"little")} or {txInCount}')
                print(f'tx_out count ({len(txOutCount)} Bytes) = {int.from_bytes(txOutCount,"little")} or {txOutCount}')
                print('******************* END OF TX MESSAGE *******************')
            return 
        # transactionsOut - An array of dictinaries where each dictionary is a transaction output  
        transactionsOut = [] 
        # Loop through each of the transactions out, we know how many output transactions are from txOutCount  
        for i in range(int.from_bytes(txOutCount,"little")):
            # Value - 8 bytes and is the transaction value 
            value = payload[txOutStart:8+txOutStart]
            # pkScriptLenght - The lenght of the pk script 1 Byte  
            pkScriptLength = payload[8+txOutStart:9+txOutStart]
            # If the pkScriptLenght is greater than 0 
            if int.from_bytes(pkScriptLength,"little") > 0:
                # pk_script - The pk script which contains the pucblic key output, the lenght is obtained from the pkScriptLength 
                pkScript = payload[9+txOutStart:9+txOutStart+int.from_bytes(pkScriptLength,"little")]
                # Create the transaction object 
                transactionsOut.append({'value':value,'pk_script length':pkScriptLength,'pk_script':pkScript})
                # Update txOutStart for the next loop to parse the next transaction out
                txOutStart = 9+txOutStart+int.from_bytes(pkScriptLength,"little")
            else:
                # Create the transaction object 
                transactionsOut.append({'value':value,'pk_script length':pkScriptLength,'pk_script':None})
                # Update txOutStart for the next loop to parse the next transaction out
                txOutStart = 9+txOutStart
        # The final four bytes should be the lock_time 
        lockTime = payload[txOutStart:]
        # If display is set true in input then display the transaction in nice format 
        if display:
            self.displayTransaction(payload,version,txInCount,transactionsIn,txOutCount,transactionsOut,lockTime)
        return payload,version,txInCount,transactionsIn,txOutCount,transactionsOut,lockTime

    def displayTransaction(self,payload,version,txInCount,transactionsIn,txOutCount,transactionsOut,lockTime):
        '''
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
        '''
        print('*******************TX MESSAGE*******************')
        print(f'Length of payload  = {len(payload)} Bytes')
        print(f'version ({len(version)} Bytes)  = {int.from_bytes(version,"little")} or {version}')
        print(f'tx_in count ({len(txInCount)} Byte)  = {int.from_bytes(txInCount,"little")} or {txInCount}')
        # Loop through the dictonary of transactions in 
        for i in range(len(transactionsIn)):
            print(f'\tTransaction input {i}')
            previous_output       = transactionsIn[i]['previous_output']
            scriptLength          = transactionsIn[i]['script length']
            signatureScript   = transactionsIn[i]['signature script']
            sequence          =  transactionsIn[i]['sequence']
            print(f'\t\tprevious_output ({len(previous_output)} Bytes) = {previous_output}')
            print(f'\t\tscript length ({len(scriptLength)} Bytes) = {int.from_bytes(scriptLength,"little")} or {scriptLength}')
            if signatureScript:
                print(f'\t\tscript signature ({len(signatureScript)} Bytes) = {signatureScript}')
            else:
                print(f'\t\tscript signature (0 Bytes) = {signatureScript}')
            print(f'\t\tsequence ({len(sequence)} Bytes) = {sequence}')
        print(f'tx_out count ({len(txOutCount)} Bytes) = {int.from_bytes(txOutCount,"little")} or {txOutCount}')
        for i in range(len(transactionsOut)):
            print(f'\tTransaction Output {i}')
            value = transactionsOut[i]['value']
            valueSatoshi = int.from_bytes(value,'little')
            pkScriptLength = transactionsOut[i]['pk_script length']
            pkScript       = transactionsOut[i]['pk_script']
            print(f'\t\tvalue ({len(value)} Bytes) = {valueSatoshi} Satoshis ({valueSatoshi*0.00000001} BTC)')
            print(f'\t\tpk_script length ({len(pkScriptLength)} Bytes) = {int.from_bytes(pkScriptLength,"little")} or {pkScriptLength}')
            if pkScript:
                print(f'\t\tpk_script ({len(pkScript)} Bytes) = {pkScript}')
            else:
                print(f'\t\tpk_script (0 Bytes) = {pkScript}')
        if lockTime ==  b'\x00\x00\x00\x00':
            print(f'lock_time ({len(lockTime)} Bytes) = {lockTime} transaction not locked')
        elif int.from_bytes(lockTime,"little") < 500000000:
            print(f'lock_time ({len(lockTime)} Bytes) = {lockTime}, transaction unlocked at block {int.from_bytes(lockTime,"little")}')
        else:
            print(f'lock_time ({len(lockTime)} Bytes) = {lockTime}, transaction unlocked at {datetime.utcfromtimestamp(int.from_bytes(lockTime,"little"))}')
        print('******************* END OF TX MESSAGE *******************')

    def parseBlockMsg(self,msg,display=True):
        '''
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
        '''
        # Sometimes the message will ony contain the first 24 bytes for some reason (the header)
        # Ensure that we have the full amount first, if we only have 24 bytes
        # call recv again the reamining message will be there 
        payload = ''
        # Get the length of the payload from bytes 16 to 20
        lenghtOfPayload = int.from_bytes(msg[16:20],"little")
        # Sometimes only first 24 bytes is sent first 
        if (len(msg) == 24):
            # need to call recover again to get the next part of the message which will be the payload 
            # only accept the next lenghtOfPayload bytes specifiec in the header 
            payload  = self.socket.recv(lenghtOfPayload)  
        else:
            # We got more than 24 bytes, but just to be sure we havent got more than we need
            # only use the lenght of the payload specificied in the header as the source of truth 
            payload = msg[24:24+lenghtOfPayload]
        # version - 4 bytes relating to the block version 
        version    = payload[0:4]
        # prev_block - 32 bytes relating to the hash value of the previous block 
        prevBlock  = payload[4:36]
        # merkle_root - 32 bytes, reference to merkle tree collection which is hash of all transactions realted to block 
        merkleRoot = payload[36:68] 
        # timestamp - 4 bytes, a unix timestamp for when this block was created
        timestamp = payload[68:72]
        # bits - 4 bytes the calculated difficulty target 
        bits = payload[72:76]
        # nonce - 4 bytes the nonce used to generate this block 
        nonce = payload[76:80]
        # txn_count - The number of transactions in the block 
        txn_count = payload[80:81]
        # parse variable lenght integer see https://wiki.bitcoinsv.io/index.php/VarInt#:~:text=A%20VarInt%20or%20%22Variable%20Integer,of%20the%20object%20being%20defined.
        if txn_count == b'\xfd':
            # 2 byte integer 
            txn_count = payload[81:83] # 2 byte integer
        elif txn_count == b'\xfe':
            # 4 byte integer 
            txn_count = payload[81:85] # 4 byte integer 
        elif txn_count == b'\xff':
            # 8 byte integer 
            txn_count = payload[81:89] # 8 byte integer
        # If you want to get the actual tx messages they are wahtever now remains in the payload 

        # If display passed then display the block message in nice format 
        if display:
            self.displayBlock(payload,version,prevBlock,merkleRoot,timestamp,bits,nonce,txn_count)
        return payload,version,prevBlock,merkleRoot,timestamp,bits,nonce,txn_count

    def displayBlock(self,payload,version,prevBlock,merkleRoot,timestamp,bits,nonce,txn_count):
        '''
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
        '''
        print('*******************BLOCK MESSAGE*******************')
        print(f'Length of payload  = {len(payload)} Bytes')
        print(f'version ({len(version)} Bytes)  = {version}')
        print(f'prev_block hash ({len(prevBlock)} Bytes) = {prevBlock}')
        print(f'merkleRoot ({len(merkleRoot)} Bytes) = {merkleRoot}')
        print(f'timestamp ({len(timestamp)} Bytes) = {datetime.utcfromtimestamp(int.from_bytes(timestamp,"little"))}')
        print(f'difficulty target ({len(bits)} Bytes) = {int.from_bytes(bits,"little")} or {bits}')
        print(f'nonce ({len(nonce)} Bytes) = {int.from_bytes(nonce,"little")} or {nonce}')
        print(f'txn count ({len(txn_count)} Bytes) = {int.from_bytes(txn_count,"little")} or {txn_count}')
        print('****************END OF BLOCK MESSAGE***************')