import socket
import socketsbase as sb
import json
import queue
import threading
from StackLayer import StackLayer
import configparser 

# Move constants to this namespace
AF_INET = sb.AF_INET
SOCK_DGRAM = sb.SOCK_DGRAM
SOCK_STREAM = sb.SOCK_STREAM
timeout = socket.timeout

# Internal Constants
_MORSOCK_SERVER_ADDR = ('localhost', 5280)  # Default address of the morstack server
_PORT_CAP = 100  # Number of morse ports to make available

class socket(sb.socketbase):
    """
    Serves as a sockets-conforming interface for use by the
    application layer. Implements bind, recvfrom, and sendto
    as expected of a normal socket, but forwards method calls
    to the morse-stack via RPC.
    """

    def __init__(self, network_protocol=AF_INET, transport_protocol=SOCK_DGRAM):
        self.msg_queue = queue.Queue()
        self.CMD_MAP = {
            "exception" : self._raiseException,
            "message" : self._enqueueMessage
        }
        
        super().__init__(network_protocol, transport_protocol) 
        
        self.sock = sb.CN_Socket(2, 2)
        self.recv_thread = threading.Thread(target=self._internalRecv)
        self.recv_thread.start()
        
        # Register this process with the morsockserver
        self._sendCmd("register")
        
    def _internalRecv(self):
        while True:
            #8192 is buffer
            data, addr = self.sock.recvfrom(8192)
            data = deserialize(data)
            self.CMD_MAP[data["instruction"]](**data["params"])
            
    def _sendCmd(self, instruction, params={}):
        serialized = serialize(instruction, params)
        self.sock.sendto(serialized, _MORSOCK_SERVER_ADDR)
            
    def _enqueueMessage(self, message, addr):
        self.msg_queue.put((message, addr))
        
    def _raiseException(self, desc):
        raise Exception(desc)
        
    def bind(self, addr):
        self._sendCmd("bind", {"request_addr": addr})
        
    def close(self):
        self._sendCmd("close")
        
    def sendto(self, message, dest_address):
        self._sendCmd("sendto", {
                "message": forcedecode(message),
                "dest_addr": dest_address
            })
        return len(bytearray(message))

    def recvfrom (self, bufsize):
        if self.timeout:
            try:
                return self.msg_queue.get(True,self.timeout)
            except queue.Empty:
                raise timeout("Socket recvfrom operation timed out.")
        return self.msg_queue.get()
            
    def __exit__ (self, argException, argString, argTraceback):
        self.close()
        self.sock.close()
        super().__exit__(argException, argString, argTraceback)
        
        
class SocketServerLayer(StackLayer):
    
    def __init__(self, below_queue, sockets_message=None, addr=_MORSOCK_SERVER_ADDR, verbose=False):
        super().__init__(below_queue)
        self.verbose = verbose
        self.verbose = True
        self.port_map = {}
        self.port_counter = 0
        self.CMD_MAP = {
            "sendto" : self.pass_down,
            "bind" : self.bind,
            "register" : self.register,
            "close" : self.close
        }

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.iptable = configparser.ConfigParser()
        self.iptable.read('iptable.ini')
        self.src_ip = self.config['CONFIG']['lan'].replace("'", "") + self.config['CONFIG']['host'].replace("'","")

        self.sock = sb.CN_Socket(2,2)
        self.sock.bind(addr)
        
        rpc_listen = threading.Thread(target=self.receive_rpc)
        rpc_listen.start()           

    def receive_rpc(self):
        while True:
            data, addr = self.sock.recvfrom(8192)
            cmd_obj = deserialize(data)
            cmd_obj['params']['addr'] = addr
            self.CMD_MAP[cmd_obj['instruction']](**cmd_obj['params'])
            if self.verbose: print("Received the command {} from {}".format(data, addr))

    def receive(self):
        """
        Grab IP/Port data and forward through internal socket to the
        related process in the port_map.
        """
        while True:
            message = self.below_queue.get()
            if message:
                src_ip = message[0:2]
                dest_ip = message[2:4]
                src_port = message[9:11]
                dest_port = message[11:13]
                self.sendMessage(message, (sb.morse2ipv4(src_ip), src_port), (sb.morse2ipv4(dest_ip), dest_port))
                self.config.read('config.ini')
                #CHECK TO SEE IF THE PACKET IS PURELY INFORMATIONAL
                if src_ip[1] == " ":
                    #STORE MY LAN AND MY HOST INFORMATION
                    config_file = open('config.ini', 'w')
                    self.config.set('CONFIG', 'lan', dest_ip[0])
                    self.config.set('CONFIG', 'host', dest_ip[1])
                    self.config.write(config_file)
                    config_file.close()

                    #SET MY SRC_IP
                    self.config.read('config.ini')
                    self.src_ip = self.config['CONFIG']['lan'].replace("'", "") + self.config['CONFIG']['host'].replace("'","")
                else:
                    print('Source IP:', message[0:2])
                    print('Dest IP:', message[2:4])
                    print('Check Sum:', message[5:9])
                    given_checksum = message[5:9]
                    calculated_checksum = self.checksum(message[0:2] + message[2:4])
                    print('Calculated Check Sum:', calculated_checksum)
                    if given_checksum == calculated_checksum:
                        print("CHECKSUM VALIDATED!")
                    else:
                        print("CHECKSUM NOT VALID!")
                        
                    self.create_ip_cache(src_ip[1])

        
    def pass_down(self, message, dest_addr, addr):

        morse_source_port = str(self.port_map[addr[1]])
        morse_dest_port = str(dest_addr[1])
        morse_dest_ip = sb.ipv42morse(dest_addr[0])

        if len(morse_source_port) == 1:
            morse_source_port = '0' + morse_source_port
        if len(morse_dest_port) == 1:
            morse_dest_port = '0' + morse_dest_port

        #TODO CALCULATE CHECKSUM
        checksum = 'CCCC'
        checksum = self.checksum(self.src_ip + morse_dest_ip)
        transport = morse_source_port + morse_dest_port + message

        
        message = self.src_ip + morse_dest_ip + sb.SOCK_DGRAM + checksum + transport
        self.sockets_message.put(message)
        return message

    def checksum(self,header):
        xheader=[]
        nxheader= 0
        #convert from header to hex
        for c in header:
                xheader.append(hex(ord(c))[2:].zfill(2))
        # take sum
        for x in xheader:
                nxheader += int(x, 16)

        carry = nxheader >> 8
        value = nxheader & 0b000011111111

        bsum = value + carry
        thing = hex(~bsum)
        checksum = str(thing)
        if checksum[0] == "-":
                checksum = checksum[2:]
        checksum = checksum[1:]
        checksum = checksum.upper()
        checksum = "00" + checksum
        return checksum

    def bind(self, request_addr, addr):
        """
        Binds a process to the requested (ip, port) address if that combination
        is not already in use by another process. Returns a serialized exception
        to the requesting morstackclient if the address is not available
        """
        if request_addr in self.port_map.values():
            exception = "Port in use"
        elif request_addr[1] > _PORT_CAP:
            exception = "Port number out of range. Ports numbers must be >0 and <{}".format(_PORT_CAP)
        else:
            del self.port_map[addr[1]]  # Clear old port reservation
            self.port_map[addr[1]] = request_addr[1]  # Reserve new port
            if self.verbose: print("Process on OS port {} bound to morse port {}".format(addr[1], request_addr[1]))
            return
        
        self.sendException(exception, addr)
            
    
    def register(self, addr):
        """
        Assign a morse port to a process when it starts up. The ports
        are assigned from 0 to _PORT_CAP and will find an available port
        if available. If a port is not available, it will return a serialized
        exception to the morstackclient.
        """
        
        for i in range(self.port_counter, self.port_counter + _PORT_CAP):
            port = i % _PORT_CAP
            
            # If an available port if found, adjust the port_counter for
            # future searches, and register the process to the port
            if port not in self.port_map:
                self.port_counter = port + 1
                self.port_map[addr[1]] = port
                if self.verbose: print("New process registered on OS port {} bound to morse port {}".format(addr[1], port))
                return
        
        # If no ports are available, forward an exception to the requesting client
        self.sendException("No ports available", addr)
        
    def close(self, addr):
        if addr[1] in self.port_map: del self.port_map[addr[1]]  # Close port reservation
    
    def sendException(self, desc, addr):
        self.sock.sendto(serialize("exception", {"desc": desc}), addr)

    def sendMessage(self, message, src_addr, dest_addr):
        for port, morse_port in self.port_map.items():
            if len(str(morse_port)) == 1:
                morse_port = "0" + str(morse_port)
            if str(dest_addr[1]) == str(morse_port):
                rpc = serialize("message", {"message": message, "addr": src_addr})
                self.sock.sendto(rpc, ("localhost", port))
                break

    def create_ip_cache(self, host):
        with open('temp.txt', 'r+') as tempfile:
            temp = json.load(tempfile)
            temp_mac = list(temp.keys())[0]

            #ADD MESSAGE TO CACHE
            iptable_file = open('iptable.ini', 'w')
            self.iptable.set('IPTABLE', host, temp_mac)
            self.iptable.write(iptable_file)
            iptable_file.close()
            tempfile.seek(0)
            tempfile.truncate()
        
def serialize(instruction, parameters={}):
    return json.dumps(
        {"instruction": instruction,
         "params": parameters
        }).encode('utf-8')
        
def deserialize(serialized):
    return json.loads(serialized.decode('utf-8'))
    
def forcedecode (encoded):
    try:
        return encoded.decode('utf-8')
    except TypeError:
        return encoded
    
    
# ----- TESTING CODE ----- #
if __name__ == "__main__":
    print("-- Testing: ")
    with socket(AF_INET, SOCK_DGRAM) as test_sock:
        pass
