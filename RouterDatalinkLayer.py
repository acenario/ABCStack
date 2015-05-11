from DatalinkLayer import DatalinkLayer
import CN_Sockets
import button


class RouterDatalinkLayer(DatalinkLayer):

    def pass_down(self, message):
        print('Datalink Pass Down:', message)
        if message:
            print('Passing from Datalink to Physical')
            return self.append_header(message)
        return message

    def append_header(self, message):
        self.iptable.read('iptable.ini')
        src_lan = message[0]
        src_host = message[1]
        dest_lan = message[2]
        dest_host = message[3]
         
        try:
            dest_mac = self.iptable['IPTABLE'][dest_host]
        except:
            dest_mac = ' '

        ip_protocol = 'A'
        m = self.src_mac + dest_mac + ip_protocol + message
        button.no_wait(m)
        return self.src_mac + dest_mac + ip_protocol + message

    def receive(self):
        while True:
            message = self.below_queue.get()
            if message:
                self.iptable.read('iptable.ini')
                
                if message[1] == ' ':
                    print ('Source MAC:', message[0])
                    print ('Dest MAC:', message[1])
                    print ('IP Protocol:', message[2])

                     # sending back the ip to the transmiting pi

                     # getting src of router from config

                    src_mac = self.src_mac
                    dest_mac = message[0]
                    ip_protocol = message[2]

                    set_ip_protocol = 'C'

                     # creating new ip for newly connected pi

                    self.config.read('config.ini')
                    lan = self.config['CONFIG']['lan'].replace("'", '')
                    host = str(len(self.iptable['IPTABLE']))

                    iptable_file = open('iptable.ini', 'w')
                    self.iptable.set('IPTABLE', host, message[0])
                    self.iptable.write(iptable_file)
                    iptable_file.close()

                     # SET SOURCE_HOST BLANK TO INDICATE INFO PACKET TO CLIENT
                     # src_ip = lan + self.config['DEFAULT']['host'].replace("'","")

                    src_ip = lan + ' '
                    dest_ip = lan + host

                     # TODO: Calculate checksum

                    check_sum = 'CCCC'

                    print('DEST MAC: ' + dest_mac)
                    message = self.src_mac + dest_mac + set_ip_protocol \
                        + src_ip + dest_ip + check_sum + message[11:]
                    print ('MESSAGE TO BE SENT: ', message)

                    self.above_queue.put(message)
                elif message[1] == self.src_mac:

                 # CHECK TO SEE IF MATCHING ROUTER'S MAC

                    self.config.read('config.ini')
                    dest_lan = message[5]
                    dest_host = message[6]
                    my_lan = self.config['CONFIG']['lan'].replace("'", '')
                    
                    # if your lan is my lan ...
                    if dest_lan == my_lan:
                        self.iptable.read('iptable.ini')
                        #iptable_file = open('iptable.ini', 'w')
                        #self.iptable.set('IPTABLE', '1', 'B')
                        #self.iptable.write(iptable_file)
                        #iptable_file.close()
                        #self.iptable.read('iptable.ini')                        

                        try:
                            print('DESTINATION HOST:', str(dest_host))
                            dest_mac = self.iptable['IPTABLE'][dest_host]
                        except:
                            dest_mac = "1"
                            print('BAD EXCEPTION. GO HOME.')
                            
                        message = message[0] + dest_mac + message[2:]

                        print ('Router Data Link Modified Message:',
                               message)

                          # passing down routed message with found mac address
                        button.no_wait(message)

                        self.above_queue.put(message)
                    else:
                        lans = {
                            'A': '192.168.128.103',
                            'B': '192.168.128.110',
                            'C': '192.168.128.111',
                            'D': '192.168.128.102',
                            }
                        dest_ip = lans[dest_lan]
                        port = 2048
                        print("DEST IP: " + dest_ip + " PORT: " + str(port))

                         # SOCKETS CODE

              
                        socket, AF_INET, SOCK_DGRAM = \
                            (CN_Sockets.socket, CN_Sockets.AF_INET,
                             CN_Sockets.SOCK_DGRAM)
                        sock = socket(AF_INET, SOCK_DGRAM)
                        packet_message = message[3:]
                        bytearray_message = bytearray(packet_message,
                                encoding='UTF-8')
                        bytes_sent = sock.sendto(bytearray_message,
                                (dest_ip,port))  # this is the command to send the bytes in bytearray to the server at "Server_Address"

                        print('{} bytes sent'.format(bytes_sent))  # sock_sendto returns number of bytes send.
                        print('=== MESSAGE SENT ===' + '\n')
