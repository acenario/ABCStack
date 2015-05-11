import ABCStack as stack
import atexit
import RPi.GPIO as GPIO
import time
import configparser
import time
import sys
import button

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
        button.no_wait("Please set MAC", True)
    
    while mac == '*':
        sys.stdout.write('.')
        sys.stdout.flush()
        config.read('config.ini')
        mac = config['CONFIG']['mac'].replace("'", "")
        time.sleep(2) 
    
    if router == ' ':
        print('Sending Informational Packet...')
        button.no_wait("DHCP Initializing\nAsking for IP...", True)
        abc.prompt(informational=True)

    #Checking to see if I received a packet from the router
    #Tries again every 30 seconds
    count = 1
    attempts = 1
    while router == ' ':
        config.read('config.ini')
        router = config['CONFIG']['router'].replace("'", "")
        if (count % 16 == 0):
            print('\n Sending Informational Packet again...')
            attempts += 1
            m = "DHCP Initializing\nAsking for IP...\nAgain... " + " ( " + str(attempts) + ")"
            button.no_wait(m, True)
            abc.prompt(informational=True)
            count = 0
        count += 1
        time.sleep(2)
        
    print('ROUTER FOUND:', router)
    b = "DHCP Initialized\nRouter MAC: " + str(router)
    button.no_wait(b)
    c = "Push to start:\nABC Stack"
    button.wait(c, blink=True)
    
    while True:
        abc.prompt()
