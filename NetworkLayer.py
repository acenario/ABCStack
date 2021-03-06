from StackLayer import StackLayer
import configparser

class NetworkLayer(StackLayer):
    def __init__(self, below_queue):
        super().__init__(below_queue)

        self.config = configparser.ConfigParser()
        self.config.read('config.ini')
        self.iptable = configparser.ConfigParser()
        self.iptable.read('iptable.ini')
        self.src_ip = self.config['CONFIG']['lan'].replace("'", "") + self.config['CONFIG']['host'].replace("'","")

    def pass_down(self, message):
        return self.append_header(message)

    def receive(self):
        while True:
            message = self.below_queue.get()

            if message:
                src_lan = message[0:1]
                src_host = message[1:2]

                dest_lan = message[2:3]
                dest_host = message[3:4]

                #CHECK TO SEE IF THE PACKET IS PURELY INFORMATIONAL
                if src_host == " ":
                    #STORE INFORMATION
                    config_file = open('config.ini', 'w')
                    self.config.set('CONFIG', 'lan', dest_lan)
                    self.config.set('CONFIG', 'host', dest_host)
                    self.config.write(config_file)
                    config.close()
                else:
                    print('Source IP:', message[0:2])
                    print('Dest IP:', message[2:4])
                    print('Check Sum:', message[4:8])
                    self.create_ip_cache(src_host)

            self.above_queue.put(self.get_payload(message))

    def append_header(self, message):
        dest_ip = 'A0' # TODO: retrieve destination IP from MorseSockets Server
        check_sum = 'CCCC' # TODO: implement check sum
        return self.src_ip + dest_ip + check_sum + message

    def get_payload(self, message):
        if (message):
            return message[8:]
        return message

    def create_ip_cache(self, host):
        import json
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
