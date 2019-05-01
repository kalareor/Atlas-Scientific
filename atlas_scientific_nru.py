#!/usr/bin/python
# -*- coding: utf-8 -*-

# Ver 1.0 - 2019.05.01
# Coded by NRu (contact through git hub comments please)
#
# This code is meant for water control unit controlled by an RPi 3 B+ and using following Atlas Scientific components : Tentacle T3 for Raspberry Pi, EZO RTD, pH and EC modules, PT-1000 Temperature Probe, pH Probe and Conductivity Probe K 0.1
# The idea of the code is to be able to read sensors separately or simultaneously as floats to be then used in other codes for controling other components of the system.
# No DO EZO module or sensor was attached to the Tentacle T3 while developing this code. The presence of DO sensor in this code is purely for debugging purposes.
#
# Code inspired from following repositories. Special thanks to their developers for their help:
#       https://gist.github.com/noxqs/1cbcc97ac8ba01428ff91c7ace942d43
#       https://github.com/AtlasScientific/Raspberry-Pi-sample-code/blob/master/i2c.py
#
# NB: I am far from being a developer or even a programmer and basically just begun with Python after only knowing/using C/C++, so this code is far from perfect.

import io  # used to create file streams
import fcntl  # used to access I2C parameters like addresses
import time  # used for sleep delay and timestamps


class ASI2C:
    timeout = 1.5  # the timeout needed to query readings
    default_bus = 1  # the default bus for I2C on the Raspberry Pi 3 B+ is 1. On some older models it is 0
    I2C_SLAVE = 0x703  # whatever the heck this is...

    # default address for the sensors (97: EZO DO, 98: EZO ORP, 99: EZO pH, 100: EZO EC, 102: EZO RTD, 103: EZO PMP)
    DOadd = 98
    pHadd = 99
    ECadd = 100
    RTDadd = 102

    R = ("R" + "\00").encode('latin-1')  # esoteric char operation for the EZO so the EZO modules understand "R" command

    def __init__(self, bus=default_bus):
        # open two file streams, one for reading and one for writing
        # the specific I2C channel is selected with bus
        # wb and rb indicate binary read and write
        self.file_read = io.open("/dev/i2c-" + str(bus), "rb", buffering=0)
        self.file_write = io.open("/dev/i2c-" + str(bus), "wb", buffering=0)

    def read(self, num_of_bytes=31):
        # reads a specified number of bytes from I2C, then parses and returns the result as a float
        try:
            res = self.file_read.read(num_of_bytes)  # read from the board
            if type(res[0]) is str:  # if python2 read
                response = [i for i in res if i != '\x00']
                if ord(response[0]) == 1:  # if the response isn't an error
                    char_list = list(map(lambda x: chr(ord(x) & ~0x80), list(response[1:])))  # esoteric mambo-jumbo
                    return float(''.join(char_list))  # esoteric conversion
                else:
                    return -300.0  # error message if something went wrong with esoteric sring/float convertion

            else:  # if python3 read
                if res[0] == 1:
                    char_list = list(map(lambda x: chr(x & ~0x80), list(res[1:])))  # esoteric mambo-jumbo
                    return float(''.join(char_list))  # esoteric conversion
                else:
                    return -300.0  # error message if something went wrong with esoteric char/string/float conversion
        except IOError:
            return -200.0  # error message if read was tried with the EZO module having nothing to give (too early, not enough timeout after "R" command, etc...)

    def query(self):  # write a "R" to the board, wait the correct timeout, and read the response
        try:
            self.file_write.write(self.R)
            time.sleep(self.timeout)
            return self.read()
        except IOError:
            return -100.0  # error message if the EZO module is missing

    def setadd(self, add):  # setting I2C communication address to desired sensor add address
        fcntl.ioctl(self.file_read, self.I2C_SLAVE, add)
        fcntl.ioctl(self.file_write, self.I2C_SLAVE, add)

    def readT(self):  # make separate reading of RTD sensor
        self.setadd(self.RTDadd)  # setting read/write address to RTD sensor(102)

        res = self.query()  # making the measurement on RTD sensor

        return res

    def readpH(self):  # make separate reading of pH sensor
        self.setadd(self.pHadd)  # setting read/write adress to pH sensor(99)

        res = self.query()   # making the measurement on pH sensor

        return res

    def readEC(self):  # make separate reading of EC sensor
        self.setadd(self.ECadd)  # setting read/write adress to EC sensor (100)

        res = self.query()  # making the measurement on EC sensor

        return res

    def readDO(self):   # make separate reading of DO sensor (no DO EZO module was connected to the tentacle while testing this code for debugging purposes)
        self.setadd(self.DOadd)  # setting read/write adress to EC sensor (98)

        res = self.query()  # making the measurement on DO sensor

        return res
    
    def readALL(self):  # make "simultaneous reading on all sensors. Returning float list with results in this order [RTD, pH, EC, DO]

        resRTD = respH = resEC = resDO = -400.0  # initialising result values. If -400.0 is returned in the results, something went really wrong somewhere...

        self.setadd(self.RTDadd)  # change I2C address to RTD sensor address
        try:
            self.file_write.write(self.R)  # write a "R" to the board
        except IOError:
            resRTD = -100.0  # error message if the EZO module is missing

        self.setadd(self.pHadd)  # change I2C address to pH sensor address
        try:
            self.file_write.write(self.R)  # write a "R" to the board
        except IOError:
            respH = -100.0  # error message if the EZO module is missing

        self.setadd(self.ECadd)  # change I2C address to EC sensor address
        try:
            self.file_write.write(self.R)  # write a "R" to the board
        except IOError:
            resEC = -100.0  # error message if the EZO module is missing

        self.setadd(self.DOadd)  # change I2C address to DO sensor address
        try:
            self.file_write.write(self.R)  # write a "R" to the board
        except IOError:
            resDO = -100.0  # error message if the EZO module is missing

        time.sleep(1.5)

        if resRTD != -100.0:  # testing for missing EZO module error message
            self.setadd(self.RTDadd)  # change I2C address to RTD sensor address
            resRTD = self.read()

        if respH != -100.0:  # testing for missing EZO module error message
            self.setadd(self.pHadd)  # change I2C address to pH sensor address
            respH = self.read()

        if resEC != -100.0:  # testing for missing EZO module error message
            self.setadd(self.ECadd)  # change I2C address to EC sensor address
            resEC = self.read()

        if resDO != -100.0:  # testing for missing EZO module error message
            self.setadd(self.DOadd)  # change I2C address to DO sensor address
            resDO = self.read()

        return [resRTD, respH, resEC, resDO]


if __name__ == '__main__':

    tentacle = ASI2C()

    print "Separate readings of each sensor:"

    Te = tentacle.readT()
    pH = tentacle.readpH()
    EC = tentacle.readEC()
    DO = tentacle.readDO()

    print "T  =", Te, "°C"
    print "pH =", pH
    print "EC =", EC, "uS/cm"
    print "DO =", DO, "mg/L"

    print " "

    print "\"Simultaneous\" readings of all sensor:"
    all = tentacle.readALL()
    print "T  =", all[0], "°C"
    print "pH =", all[1]
    print "EC =", all[2], "uS/cm"
    print "DO =", all[3], "mg/L"
