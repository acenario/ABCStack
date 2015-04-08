from PhysicalLayer import PhysicalLayer
from DatalinkLayer import DatalinkLayer
from RouterDatalinkLayer import RouterDatalinkLayer
from NetworkLayer import NetworkLayer
from RouterNetworkLayer import RouterNetworkLayer
from TransportLayer import TransportLayer

import configparser

class ABCStack(object):
    def __init__(self, classes):

        iptable = configparser.ConfigParser()
        iptable.read('iptable.ini')
        config = configparser.ConfigParser()
        config.read('config.ini')
    
        iptable_file = open('iptable.ini', 'w')
        iptable.remove_section('IPTABLE')
        iptable.add_section('IPTABLE')
        iptable.write(iptable_file)
        iptable_file.close()

        config_file = open('config.ini', 'w')
        if not config.has_section('CONFIG'):
            config.add_section('CONFIG')
        if not config.has_option('CONFIG', 'mac'):
            config.set('CONFIG', 'mac', 'Z')
            print('Set MAC Address in config.ini')
        config.write(config_file)
        config_file.close()
        
        self.layers = []
        for index, layer_class in enumerate(classes):
            if index > 0:
                self.layers.append(layer_class(below_queue=self.layers[index-1].above_queue))
            else:
                self.layers.append(layer_class(below_queue=None))

    def pass_down(self, i, message):
        if i < 0:
            return
        return self.pass_down(i-1, self.layers[i].pass_down(message))

    def prompt(self, informational=False):
        if informational:
            message = " "
        else:
            message = input('Message: ')
        self.pass_down(len(self.layers)-1, message)
