from StackLayer import StackLayer
import configparser

class DatalinkLayer(StackLayer):
    def __init__(self, below_queue):
        super().__init__(below_queue)

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')

        self.iptable = configparser.ConfigParser()
        self.iptable.read('iptable.ini')

        self.src_mac = self.config['CONFIG']['mac'].replace("'", "")

    def pass_down(self, message):
        return self.append_header(message)

    def receive(self):
        while True:
            message = self.below_queue.get()
            if message:
                print('Message from Physical:', message)
                src_mac = message[0]
                dest_mac = message[1]
                
                if dest_mac == self.src_mac:
                    ip_protocol = message[2]

                    #CHECKS TO SEE IF INFORMATIONAL PROTOCOL
                    if ip_protocol == "C":
                        #STORE ROUTER MAC ADDRESS
                        self.config.read('config.ini')
                        config_file = open('config.ini', 'w')
                        self.config.set('CONFIG', 'router', src_mac)
                        self.config.write(config_file)
                        config_file.close()
                    else:
                        print('Source MAC:', message[0])
                        print('Dest MAC:', message[1])
                        print('IP Protocol:', message[2])

                        self.temp_store(src_mac)
                    self.above_queue.put(self.get_payload(message))

                else:
                    print('Routed to', message[1])
                    self.temp_store(src_mac)
            #self.above_queue.put(self.get_payload(message))

    def append_header(self, message):
        ip_protocol = 'A'
        self.iptable.read('iptable.ini')
        try:
            #CHECK CACHE FOR MESSAGE
            dest_mac = self.iptable['IPTABLE'][message[3]].replace("'", "")
            print('DEST MAC FROM CACHE:', dest_mac)
            print('IP LOOKUP:', message[3])
        except:
            #SEND MESSAGE TO ROUTER
            self.config.read('config.ini')
            dest_mac = self.config['CONFIG']['router'].replace("'", "")
            if dest_mac == ' ':
                #INDICATE THAT THE PACKET IS PURELY INFORMATIONAL
                ip_protocol = 'C'

        self.config.read('config.ini')
        self.src_mac = self.config['CONFIG']['mac'].replace("'", "")
        
        return self.src_mac + dest_mac + ip_protocol + message

    def get_payload(self, message):
        if (message):
            return message[3:]
        return message

    def temp_store(self, mac):
        import json
        pair = {mac: None}
        with open('temp.txt', 'w') as tempfile:
            json.dump(pair, tempfile,indent=4)
