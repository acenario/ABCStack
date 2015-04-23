import MorseSocket as CN_Sockets   
import socketsbase as sb
import sys
import socket as st
timeout = st.timeout

class UDP_Server(object):
    """Run this module first (it is the server) but read UDP_TX module before using this one.
This module demonstrates receiving a transmission sent by the UDP_TX module
on a SOCK_DGRAM (UDP) socket.  This module must be started first, so that it
can publish its port address (5280).

    """

    def __init__(self):
        self.clients = set()

    def listen(self,IP="127.0.0.1",port=45):

        socket, AF_INET, SOCK_DGRAM, timeout = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM, CN_Sockets.timeout

        with socket(AF_INET, SOCK_DGRAM) as sock:
            sock.bind((IP,port))  # bind sets up a relationship in the linux
                                  # kernel between the process running
                                  # UCP_RX and the port number (5280 by default)
                                  # 5280 is an arbitrary port number.
                                  # It is possible to register a protocol
                                  # with the IANA.  Such registered ports
                                  # are lower than 5000. e.g. HTTP (
                                  # for browser clients and web servers)
                                  # is registered by IANA as port 80
                                  #

            sock.settimeout(2.0) # create a 2 second timeout so that we
                                 # can use ctrl-c to stop a blocked server
                                 # if, for example, the client doesn't work.

            print ("UDP Server started on IP Address {}, port {}".format(IP,port))

            while True:
                try:
                    bytearray_msg, source_address = sock.recvfrom(1024) # 1024 is the buffer length
                                                                 # allocated for receiving the
                                                                 # datagram (i.e., the packet)
                    source_address = (source_address[0], source_address[1])

                    source_IP, source_port = source_address    # the source iaddress is ("127.0.0.1",client port number)
                                                               # where client port number is allocated to the TX process
                                                               # by the Linux kernel as part of the TX network stack))

                    print("SOURCE ADDRESS: ", source_address)
                    self.clients.add(source_address) #appending the client in a unique list
                    print("CLIENTS: ", str(self.clients))
                    print ("\nMessage received from ip address {}, port {}:".format(
                        source_IP,source_port))
                    #print (bytearray_msg.decode("UTF-8")) # print the message sent by the user of the  UDP_TX module.
                    print (bytearray_msg) # print the message sent by the user of the  UDP_TX module.


                    self.send_message_to_clients(source_address, bytearray_msg, sock)

                except timeout:
                    sys.stdout.write('.')
                    sys.stdout.flush()
                    #print (".",end="",flush=True)  # if process times out, just print a "dot" and continue waiting.  The effect is to have the server print  a line of dots
                                                   # so that you can see if it's still working.
                    continue  # go wait again


    def send_message_to_clients(self, source_address, bytearray_msg, sock):
        payload = bytearray_msg[13:]
        print("payload: ", payload)
        print("plen: ", str(len(payload)))
        if (len(payload) != 0):
            print("BARRAY: ", bytearray_msg)
            bytearray_msg = bytearray(payload, encoding="UTF-8")
            print("SRC ADDRESS: ", str(source_address))
            for c in self.clients:
                if (c != source_address):
                    bytes_sent = sock.sendto(bytearray_msg, c) # this is the command to send the bytes in bytearray to the server at "Server_Address"
                    print ("{} bytes sent".format(bytes_sent)) #sock_sendto returns number of bytes send.

            #Remove empty clients eventually
            print("Sent to: " + str(len(self.clients)) + " client(s)")


if __name__ == "__main__":
    #address = input("Enter local address: ")
    
    import configparser
    config = configparser.ConfigParser()
    config.read('config.ini')
    my_lan = config['CONFIG']['lan']
    my_host = config['CONFIG']['host']
    my_morse_ip = my_lan + my_host
    my_ip = sb.morse2ipv4(my_morse_ip)
    print("MY MORSE IP: ", my_morse_ip)
    print("MY REAL IP: ", my_ip)
    
    address = my_ip
    
    UDP_Server = UDP_Server()
    UDP_Server.listen(IP=address)
