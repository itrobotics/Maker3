#!/usr/bin/env python

import RPi.GPIO as GPIO
from time import sleep
from sys import argv
from subprocess import check_output
from threading import Thread

class qc1602a:

    def __init__(self):
        # use the BCM mode pinout setup
        GPIO.setmode(GPIO.BOARD)
        self.LCD_RS = 38
        self.LCD_RW = 40
        self.LCD_E  = 29
        self.LCD_D4 = 31
        self.LCD_D5 = 33
        self.LCD_D6 = 35
        self.LCD_D7 = 37
        self.CMD_DELAY = 0.0002
        self.CMD_CLEAR_DELAY = 0.001
        self.lcd_init()
        self.stop = 0
        self.line1_msg = ''
        self.line2_msg = ''

    def lcd_write_byte(self , cmd , RS):
        GPIO.output(self.LCD_RS, RS)
        GPIO.output(self.LCD_RW, 0)
        GPIO.output(self.LCD_E , 0)

        # write high 4 bits
        if((cmd & 0x10) == 0x10):
            GPIO.output(self.LCD_D4, 1)
        else:
            GPIO.output(self.LCD_D4, 0)
        if((cmd & 0x20) == 0x20):
            GPIO.output(self.LCD_D5, 1)
        else:
            GPIO.output(self.LCD_D5, 0)
        if((cmd & 0x40) == 0x40):
            GPIO.output(self.LCD_D6, 1)
        else:
            GPIO.output(self.LCD_D6, 0)
        if((cmd & 0x80) == 0x80):
            GPIO.output(self.LCD_D7, 1)
        else:
            GPIO.output(self.LCD_D7, 0)

        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 1)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)

        # write low 4 bits
        if((cmd & 0x01) == 0x01):
            GPIO.output(self.LCD_D4, 1)
        else:
            GPIO.output(self.LCD_D4, 0)
        if((cmd & 0x02) == 0x02):
            GPIO.output(self.LCD_D5, 1)
        else:
            GPIO.output(self.LCD_D5, 0)

        if((cmd & 0x04) == 0x04):
            GPIO.output(self.LCD_D6, 1)
        else:
            GPIO.output(self.LCD_D6, 0)

        if((cmd & 0x08) == 0x08):
            GPIO.output(self.LCD_D7, 1)
        else:
            GPIO.output(self.LCD_D7, 0)

        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 1)
        sleep(0.000001)
        GPIO.output(self.LCD_E, 0)

        sleep( self.CMD_DELAY )

    def lcd_write_data(self, data):
        self.lcd_write_byte(data, 1)

    def lcd_write_command(self, cmd):
        self.lcd_write_byte(cmd, 0)

    def lcd_init(self):
        # setup the pin out
        GPIO.setup(self.LCD_E,  GPIO.OUT) # E
        GPIO.setup(self.LCD_RS, GPIO.OUT) # RS
        GPIO.setup(self.LCD_RW, GPIO.OUT) # RW
        GPIO.setup(self.LCD_D4, GPIO.OUT) # DB4
        GPIO.setup(self.LCD_D5, GPIO.OUT) # DB5
        GPIO.setup(self.LCD_D6, GPIO.OUT) # DB6
        GPIO.setup(self.LCD_D7, GPIO.OUT) # DB7

        # initialize the level of all pin
        GPIO.output(self.LCD_D4,0)
        GPIO.output(self.LCD_D5,0)
        GPIO.output(self.LCD_D6,0)
        GPIO.output(self.LCD_D7,0)
        GPIO.output(self.LCD_RS,0)
        GPIO.output(self.LCD_RW,0)
        GPIO.output(self.LCD_E,0)
        
        sleep(0.1)
        GPIO.output(self.LCD_E,1)
        sleep(0.000001)
        GPIO.output(self.LCD_E,0)
        sleep(0.000001)

        ### reset the LCD and use the 4 bit (4-lines) mode
        sleep(0.002)
        self.lcd_write_byte(0x03,0)
        sleep(0.001)
        self.lcd_write_byte(0x03,0)
        sleep(0.0001)
        self.lcd_write_byte(0x03,0)
        sleep(0.0001)
        self.lcd_write_byte(0x02,0)
        sleep(0.0001)
        ### end reset procedure
        
        # function setup 
        self.lcd_write_command(0x28)
        
        self.lcd_write_command(0x0c)
        self.lcd_write_command(0x01)
        sleep(self.CMD_CLEAR_DELAY)

        self.lcd_write_command(0x06)

    def lcd_move(self,line,col):
        _pos = 0x80 + (line-1) * 0x40 + (col-1)
        self.lcd_write_command(_pos)

    def lcd_writeStr(self,_str):
        ch_list = [ord(i) for i in _str]
        for i in ch_list:
            self.lcd_write_data(i)
    
    def lcd_close(self):
        GPIO.output(self.LCD_D4,0)
        GPIO.output(self.LCD_D5,0)
        GPIO.output(self.LCD_D6,0)
        GPIO.output(self.LCD_D7,0)
        GPIO.output(self.LCD_RS,0)
        GPIO.output(self.LCD_RW,0)
        GPIO.output(self.LCD_E,0)

    def lcd_clear(self):
        self.lcd_write_command(0x01)
        sleep(self.CMD_CLEAR_DELAY)

    def lcd_clear_line_1(self):
        self.lcd_move(1,1)
        self.lcd_writeStr('                 ')

    def lcd_clear_line_2(self):
        self.lcd_move(2,1)
        self.lcd_writeStr('                 ')

    def lcm_serv_loop(self):
        self.lcd_init()
        while(self.stop == 0):
            ip_list = get_IP_list()
            for i in ip_list:
                self.line1_msg = i
                self.lcd_clear_line_1()
                self.lcd_clear_line_2()
                self.lcd_move(1,1)
                self.lcd_writeStr(self.line1_msg)
                self.lcd_move(2,1)
                self.lcd_writeStr(self.line2_msg)
                sleep(1)

    def run(self):
        self.stop = 0
        self.thread = Thread(target = self.lcm_serv_loop, args=())
        self.thread.start()

    def stop(self):
        self.stop = 1

            
def get_IP_list():
    ip_list = [ i[5:] for i in check_output('ifconfig').split() if 'addr:' in i]
    return ip_list


if __name__ == '__main__':
    myLCD = qc1602a()
    myLCD.lcd_init()
    myLCD.run()
