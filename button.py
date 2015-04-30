import RPi.GPIO as GPIO
import time
import socket
import CN_Sockets

def no_wait(message,blink=False):
    send_to_lcd(message,blink)

def wait(message,pin=12,blink=False):
    GPIO.setmode(GPIO.BCM)
    #lcd.LCD_Write(message,blink)
    send_to_lcd(message,blink)
    GPIO.setup(pin,GPIO.IN)
    GPIO.wait_for_edge(pin,GPIO.RISING)
    counter = 0
    while(True):
        print(counter)
        if GPIO.input(pin):
            counter = 0
        else:
            counter += 1
            if counter>5:
                break
        time.sleep(.01)
    #lcd.kill()

def send_to_lcd(message, blink):
    Server_Address=("127.0.0.1",9280)
    socket, AF_INET, SOCK_DGRAM = CN_Sockets.socket, CN_Sockets.AF_INET, CN_Sockets.SOCK_DGRAM
        # socket = CN_sockets.socket, which is socket.socket with a slignt modification to allow you to use ctl-c to terminate a test safely
        # CN_sockets.AF_INET is the constant 2, indicating that the address is in IPv4 format
        # CN_sockets.SOCK_DGRAM is the constant 2, indicating that the programmer intends to use the Universal Datagram Protocol of the Transport Layer

    with socket(AF_INET,SOCK_DGRAM) as sock:  # open the socket    
            #str_message = input("Enter message to send to server:\n")
        str_message = message

        bytearray_message = bytearray(str_message,encoding="UTF-8") # note that sockets can only send 8-bit bytes.
                                                                            # Since Python 3 uses the Unicode character set,
                                                                            # we have to specify this to convert the message typed in by the user
                                                                            # (str_message) to 8-bit ascii 

        bytes_sent = sock.sendto(bytearray_message, Server_Address) # this is the command to send the bytes in bytearray to the server at "Server_Address"
                
        print ("{} bytes sent".format(bytes_sent)) #sock_sendto returns number of bytes send.
    

if __name__ == "__main__":
    print("Waiting")
    wait("Hello\nHello\nBye\nBye",12,False)
    print("Done")
