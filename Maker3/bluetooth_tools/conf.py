#!/usr/bin/env python

from serial import Serial
from sys import argv

if(len(argv) == 3):
    print "config port : %s" % argv[1]
    s = Serial("%s" % argv[1],baudrate=38400,timeout=1)

    s.write("AT\r\r")
    while(True):
        a = s.read()
        if(a):
            print a
        else:
            break

    print "config bluetooth name : %s" % argv[2]
    s.write("AT+NAME=%s\r\r" % argv[2])
    while(True):
        a = s.read()
        if(a):
            print a
        else:
            break

    print "config bluetooth baud rate" 
    s.write("AT+UART=115200,0,0\r\r" )
    while(True):
        a = s.read()
        if(a):
            print a
        else:
            break

#    s.write("\r")
#    print s.read()
#    print s.read()
#
s.close()

#s = Serial("/dev/" % argv[1],baudrate=11520,timeout=1)
#print "check AT+NAME"
#s.write("AT+NAME\r")
#while(True):
#    c = s.read()
#    if(c):
#        print c
#    else:
#        break
