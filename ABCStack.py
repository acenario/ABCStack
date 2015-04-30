from PhysicalLayer import PhysicalLayer
from DatalinkLayer import DatalinkLayer
from RouterDatalinkLayer import RouterDatalinkLayer
from NetworkTransportLayer import NetworkTransportLayer
from RouterNetworkLayer import RouterNetworkLayer
from MorseSocket import SocketServerLayer
import RPi.GPIO as GPIO
import queue
import configparser
import threading
import button

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
            config.set('CONFIG', 'mac', '*')
            print('Please set your MAC Address in config.ini')
        if not config.has_option('CONFIG', 'router'):
            config.set('CONFIG', 'router', "' '")
        if not config.has_option('CONFIG', 'lan'):
            config.set('CONFIG', 'lan', "' '")
        if not config.has_option('CONFIG', 'host'):
            config.set('CONFIG', 'host', "' '")
        config.set('CONFIG', 'router', "' '")
        config.write(config_file)
        config_file.close()


        self.sockets_queue = queue.Queue()
        socket_queue_thread = threading.Thread(target=self.start_pass_down)
        socket_queue_thread.start()
        
        self.layers = []
        last_layer = len(classes)-1
        for index, layer_class in enumerate(classes):
            if index > 0:
                self.layers.append(layer_class(below_queue=self.layers[index-1].above_queue))
                if index == last_layer:
                    layer_class.sockets_message = self.sockets_queue
            else:
                self.layers.append(layer_class(below_queue=None))

    def start_pass_down(self):
        while True:
            message = self.sockets_queue.get()
            self.pass_down(len(self.layers)-2, message)

    def pass_down(self, i, message):
        if i < 0:
            return
        return self.pass_down(i-1, self.layers[i].pass_down(message))

    def prompt(self, informational=False):
        if informational:
            message = " "
            self.pass_down(len(self.layers)-2, message)
        else:
            button.no_wait("Stack has started!")
            message = input('=== ABC Stack has initialized ===')
