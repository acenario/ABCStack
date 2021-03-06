from NetworkLayer import NetworkLayer

class RouterNetworkLayer(NetworkLayer):
    
    def receive(self):

        message=self.below_queue.get()

        #creating new ip for newly connected pi
        lan = self.config['CONFIG']['lan'].replace("'","")
        host = str(len(self.iptable['IPTABLE']))

        iptable_file = open('iptable.ini', 'w')
        self.iptable.set('IPTABLE', host, message[0])
        self.iptable.write(iptable_file)
        iptable_file.close()

        src_ip = lan + self.config['CONFIG']['host'].replace("'","") 
        dest_ip = lan + host

        # TODO: Calculate checksum
        check_sum = 'CCCC'

        message = message[0:3] + src_ip + dest_ip + check_sum + message[11:]
        #self.pass_down(message)

        print('Router Network Receive:', message) 

    def pass_down(self, message):
        print('Router Network Pass Down:', message) 
        return message
