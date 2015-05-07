from ABCStack import ABCStack
from PhysicalLayer import PhysicalLayer
from RouterDatalinkLayer import RouterDatalinkLayer
import configparser
from threading import Thread
import CN_Sockets
import button

class RouterABCStack(ABCStack):
    def __init__(self, classes):
        super().__init__(classes)

        iptable = configparser.ConfigParser()
        iptable.read('iptable.ini')
        config = configparser.ConfigParser()
        config.read('config.ini')

        iptable_file = open('iptable.ini', 'w')
        iptable.set('IPTABLE', '0', config['CONFIG']['mac'].replace("'", ""))
        iptable.write(iptable_file)
        iptable_file.close()

        config_file = open('config.ini', 'w')
        config.set('CONFIG', 'router', config['CONFIG']['mac'].replace("'", ""))
        config.write(config_file)
        config_file.close()

        listen_thread = Thread(target=self.receive, args=())
        listen_thread.start()
        
        while(True):
            message = self.layers[len(self.layers)-1].above_queue.get()
            print("STACK RECEIVED: " + message)
            m = "ABC Router\nStack Received:\n" + message
            button.no_wait(m)
            #SENDING MESSAGE FROM DATALINKLAYER TO PHYSICAL
            self.pass_down(len(self.layers)-2, message)
        
    def network_receive_pass_down(self, message):
        trimmed = self.layers[1].socket_passdown(message)
        self.layers[0].pass_down(trimmed)
    
    def receive(self):
        socket, AF_INET, SOCK_DGRAM = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM
        sock = socket(AF_INET,SOCK_DGRAM)
        sock.bind(("192.168.128.103", 2048))
        while True:
            try:
                bytearray_msg, source_address = sock.recvfrom(1024)

                source_IP, source_port = source_address

                payload = bytearray_msg.decode("UTF-8")


                print("\n" + "=== MESSAGE RECEIVED ===")
                out = "\n" + payload
                print(out)
                print("\n" + "=== MESSAGE ENDED ===" + "\n")
                
                self.pass_down(len(self.layers)-1, payload)
               
            except timeout:

                #print (".",end="",flush=True)  # if process times out, just print a "dot" and continue waiting.  The effect is to have the server print  a line of dots
                                               # so that you can see if it's still working.
                continue  # go wait again
    
