import ABCStack as stack
import atexit
import RPi.GPIO as GPIO
import time
import configparser
import time
import sys

if __name__ == '__main__':
    config = configparser.ConfigParser()
    
    atexit.register(GPIO.cleanup)
    abc = stack.ABCStack([stack.PhysicalLayer, stack.DatalinkLayer, stack.SocketServerLayer])

    config.read('config.ini')
    router = config['CONFIG']['router'].replace("'", "")
    mac = config['CONFIG']['mac'].replace("'", "")
    if mac == '*':
        sys.stdout.write('Waiting for you to set your mac')
        sys.stdout.flush()
    
    while mac == '*':
        sys.stdout.write('.')
        sys.stdout.flush()
        config.read('config.ini')
        mac = config['CONFIG']['mac'].replace("'", "")
        time.sleep(2) 
    
    if router == ' ':
        print('Sending Informational Packet...')
        abc.prompt(informational=True)

    #Checking to see if I received a packet from the router
    #Tries again every 30 seconds
    count = 1
    while router == ' ':
        config.read('config.ini')
        router = config['CONFIG']['router'].replace("'", "")
        if (count % 16 == 0):
            print('\n Sending Informational Packet again...')
            abc.prompt(informational=True)
            count = 0
        count += 1
        time.sleep(2)
        
    print('ROUTER FOUND:', router)
    
    while True:
        abc.prompt()
