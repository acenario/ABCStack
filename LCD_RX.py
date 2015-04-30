import socket as so
import lcd

class UDP_RX(object):
    """1. READ the UDP_TX module before reading or using this one.

This module demonstrates receiving a transmission sent by the UDP_TX module
on a SOCK_DGRAM (UDP) socket.  This module must be started first, so that it
can publish its port address (5280).

2. Run this module before starting UDP_TX.

UDP_TX and UDP_RX will be started on separate (laptop OS) processes.
UDP_TX will prompt for a message, then transmit it to the UDP_RX module over the
loopback IP address ("127.0.0.1").

UDP_RX will receive the message and print it.
While waiting for a message UDP_RX to be started or to send another message, UDP_TX will print a line of "."s one every 2 seonds.


 
 

    """

    
    def __init__(self,IP="127.0.0.1",port=9280):

        socket, AF_INET, SOCK_DGRAM, timeout = so.socket, so.AF_INET, so.SOCK_DGRAM, so.timeout
        
        #with socket(AF_INET, SOCK_DGRAM) as sock:
        sock = socket(AF_INET, SOCK_DGRAM)
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
            
            #print ("UDP Server started on IP Address {}, port {}".format(IP,port))
            
        while True:
            try:
                bytearray_msg, source_address = sock.recvfrom(1024) # 1024 is the buffer length
                                                                 # allocated for receiving the
                                                                 # datagram (i.e., the packet)
                                                                 
                source_IP, source_port = source_address    # the source iaddress is ("127.0.0.1",client port number)
                                                               # where client port number is allocated to the TX process
                                                               # by the Linux kernel as part of the TX network stack))          
                    
                    
                #msg = bytearray_msg.decode("UTF-8")
   
                lcd.LCD_Write(bytearray_msg)

            except timeout: 
                                
                    #print (".",end="",flush=True)  
                                                   
                continue  # go wait again
        sock.close() 

if __name__ == "__main__":
    UDP_RX()
    
                
                
            



            
        
