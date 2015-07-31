#!/usr/bin/env python

from serial import Serial
from RPi import GPIO
from LCM import qc1602a
import edu

system_run = 1
cmd_buff = ''

led1_pin = 13
led2_pin = 15
relay_pin = 11
buzzer_pin = 32
button1_pin = 16
button2_pin = 18

ser = Serial("/dev/ttyAMA0",baudrate=115200)
lcm = qc1602a()
led1 = edu.led(led1_pin)
led2 = edu.led(led2_pin)
rel  = edu.relay(relay_pin)
buz  = edu.buzzer(buzzer_pin)


def shutdown():
    global lcm
    global system_run
    lcm.stop = 1
    system_run = 0

def btn1_func(ch):
    global led1
    global lcm
    global ser
    if(GPIO.input(led1.pin) == 1):
        print "led 1 is on"
        led1.off()
        ser.write("led1.1 ")
    elif(GPIO.input(led1.pin) == 0):
        print "led 1 is off"
        led1.on()
        ser.write("led1.0 ")
    lcm.line2_msg = 'btn1 pressed'


def btn2_func(ch):
    global led2
    global lcm
    global ser
    if(GPIO.input(led2.pin) == 1):
        led2.off()
        ser.write("led2.0 ")
        
    elif(GPIO.input(led2.pin) == 0):
        led2.on()
        ser.write("led2.1 ")
    lcm.line2_msg = 'btn2 pressed'



if __name__ == "__main__":
    btn1 = edu.button(button1_pin, btn1_func)
    btn2 = edu.button(button2_pin, btn2_func)
    lcm.run()

    operations = {
            'led1.1'   : led1.on,
            'led1.0'   : led1.off,
            'led2.1'   : led2.on,
            'led2.0'   : led2.off,
            'relay.1'  : rel.on,
            'relay.0'  : rel.off,
            'buzzer.1' : buz.on,
            'buzzer.0' : buz.off,
            'shutdown' : shutdown,
            }

    while(system_run):
        cmd_buff += ser.read()
        print cmd_buff
        if(cmd_buff[-1] == ' '):
            cmd = cmd_buff.strip()
            cmd_buff = ''
            lcm.line2_msg = cmd
            if(operations.get(cmd)):
                operations.get(cmd)()
    ser.close()

