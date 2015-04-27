import RPi.GPIO as GPIO
import time
import lcd

def wait(pin,message,blink):
    GPIO.setmode(GPIO.BCM)
    lcd.LCD_Write(message,blink)
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
    lcd.kill()
if __name__ == "__main__":
    print("Waiting")
    wait(12,"Hello\nHello\nBye\nBye",False)
    print("Done")
