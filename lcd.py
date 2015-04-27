#!/usr/bin/python
# Example using a character LCD connected to a Raspberry Pi or BeagleBone Black.
import math
import time

import Adafruit_CharLCD as LCD
# Raspberry Pi pin configuration:
lcd_rs        = 27  # Note this might need to be changed to 21 for older revision Pi's.
lcd_en        = 22
lcd_d4        = 25
lcd_d5        = 24
lcd_d6        = 13
lcd_d7        = 19
lcd_backlight = 4
# Define LCD column and row size for 16x2 LCD.
lcd_columns = 20
lcd_rows    = 4
#Initialize the LCD using the pins above.
lcd = LCD.Adafruit_CharLCD(lcd_rs, lcd_en, lcd_d4, lcd_d5, lcd_d6, lcd_d7, lcd_columns, lcd_rows, lcd_backlight)


def LCD_Write(string, blink_cursor=False):

	#Clear the LCD
	lcd.clear()
	lcd.show_cursor(False)
	lcd.blink(False)
	#Write the message
	lcd.message(string)
	if blink_cursor:
		lcd.blink(True)

def kill():
	lcd.clear()

if __name__ == "__main__":
	LCD_Write("Pants Are Cool!\n No they're not!\n Yes they are\nFuck", False)



