#!/usr/bin/python
# -*- coding: utf-8 -*-

'''
Ver 2.0 - 2019.05.08
Compatibility: python2 and python3. Nevertheless, python3 is  strongly recommended for better print-out readability characters handling (like °C for example)
Coded by NRu. Please contact through GitHub comments (https://github.com/kalareor/Atlas-Scientific/commit/d98634fbb9e9103ca25f405ddb7e62b3208e853c), GitHub (https://github.com/kalareor) or directly at nicolas.ruffray@gmail.com. Any questions, suggestions or constructive comments are very welcomed

This Python library is meant for using water quality related Atlas Scientific sensors (RTD, pH, EC, DO and ORP). The code is designed for I2C communication only and was developed on a Raspberry Pi 3 B+ using an Atlas Scientific Tentacle T3 hat for RPi hat. This library was not tested without the Tentacle 3 (with EZO modules connected to the RPi through a development board even if it "should" work. Any returns on this topic are very welcomed in the git hub comments or directly by e-mail.

The general idea of the library is to provide tools able to read sensors' values through EZO modules separately or simultaneously as floats to be then used in other Python codes for controlling other systems, IoT, monitoring systems, etc...

Code inspired from following repositories. Special thanks to their developers for their help:
    Morgan Heijdemann (noxqs): https://gist.github.com/noxqs/1cbcc97ac8ba01428ff91c7ace942d43
    AtlasScientific: https://github.com/AtlasScientific/Raspberry-Pi-sample-code/blob/master/i2c.py

NB: This is work in progress... Known bugs were dealt with as efficiently as possible but some might most likely remain. Also I am pretty new to Python and not originally a programmer so there there is for sure a better and more aesthetic way to code these libraries... Any constructive comments or suggestions are very welcomed.

LIBRARY FUNCTIONS' AND ARGUMENTS' DESCRIPTION:

    # ========== CONSTRUCTOR/DESTRUCTOR ==========#

     __init__(mode="op", silent=True, keep_awake=True): Constructor of the class. Initialises the communication protocols and default values. Detecting connected EZO modules and stores their names, I2C addresses, units and versions.
            mode: Not case sensitive string argument, default value: "op". Defining the way the class deals with certain errors. Argument can be "op" for operation or "dev" for development. In development mode all errors are raised for debugging purposes. In operation mode certain error such ones triggered by a faulty EZO module response, addressing a not connected EZO module, etc... are resulting in aberrant negative read values that can still be flagged but avoiding code interruptions. Please refer to _read() function description bellow for more information.
            silent: Boolean argument, default value=False. Determines if functions print out certain information useful for debugging purposes. silent=True: print-out disabled, silent=False: print-out enabled
            keep_awake: Boolean argument, default value: True. Argument controlling the putting to sleep of EZO modules at the end of the code execution. True: EZO modules are kept awake (not put to sleep). False: All connected EZO modules are put to sleep by the destructor.
        used functions: scan()

    __del__(keep awake=True): Destructor of the class.
            keep_awake:  Boolean argument, default value: True. See description in Constructor above. Value transited by constructor at code termination if the destructor is not called separately.

    # ========== PRIVATE FUNCTIONS ==========#

    _check_addr(addr): Checks given address against connected EZO modules. Returns the address of connected EZO module as integer.
            addr: Integer or String argument, no default value. addr should be and EZO module I2C address. Can be an integer in the 1-127 range or a non-case sensitive string among ["rtd", "ph", "ec", "do", "orp"]. If corresponding to a connected EZO module, its' integer address is returned.

    _write(addr, rt=True, temp=default_temp): writes "read" command ("R" or "RT,temp") to EZO module with addr address. Automatically detects sensor type and uses the appropriate command ("R" or "RT")
            addr: see description in _check_addr() function
            rt: Boolean argument, default value: True. Activates temperature compensation command "RT,temp" for pH, EC, DO sensors. If rt=False, temperature compensation will be applied with last transmitted temperature compensation value through rt=true used function, cmd() or set_t(temp) functions (see bellow for more information). If rt=True, temperature compensation will be applied with temp value.
            temp: Float argument, default value: default_temp. If rt=True, is the temperature in °C for witch the compensation will be applied. Can be a float in the range self.minH2Otemp - self.maxH2Otemp (0.0-100.0 by default). If the given value is outside this range or of wrong type, then default_temp (25°C by default) is applied for compensation.
        uses functions: _check_addr()

    _read(addr): Reads measurement from EZO module after a _write() function. Returns measurement as float.
            addr: see description in _check_addr() function
        NB.1: if used right after a _write() function a timeout time is needed in between the two. timeout varies from 300 to 900ms depending on the EZO module and the command. Please refer to Altlas Scientific EZO modules datasheets for more information.
        NB.2: function impacted by class mode. In development mode all exceptions will be raised. In operation mode following error values will be returned as measurements:
                -100.0: returned when addressing an EZO module with valid address(right type, right range) but there is no EZO module connected to this address.
                -200.0: returned when EZO module have nothing to give when tried to be read from. The timeout between _write() and_read() commands is too short or _read() command was executed without prior valid _write() command.
                -1000.0: returned when argument addr corresponds to a connected EZO module's address but is not responding correctly. EZO module was asleep OR is faulty OR its' I2C address was changed without using addr_change() function OR an undetected during debugging process error occurred.

    _query(addr, rt=True, temp=default_temp): Handles the whole measurement process of an EZO module. Returns measurement as a float.
            addr, rt, temp: see respective descriptions _write() function.
        uses functions: _write(), _read()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    _query_multi(addr, rt=True, temp=default_temp): Handles the whole measurement process of multiple EZO modules in one go. Returns measurements as list of floats.
            addr: list of integers or strings, no default value. List of EZO modules I2C addresses. addr elements can be integers in the 1-127 range or not case sensitive strings in ["rtd", "ph", "ec", "do", "orp"].
            rt, temp: see respective descriptions _write() function.
        uses functions: _write()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    # ========== PUBLIC FUNCTIONS ==========#

    scan(): scans all I2C addresses from 1 to 127, detects and stores connected modules types, addresses, versions and default units in private variables accessible through addresses(), sensors(), versions() and units() functions (see description bellow).
        NB.1: detects presence or absence of EZO RTD module (temperature) for "live" temperature compensation option in certain functions described bellow.
        NB.2: NOT TESTED but... supposed to detect presence of "not Atlas Scientific" (3rd party) I2C modules. Their addresses are stored in private variables. Values of their names, versions and units will all be stored respectively as "Unknown sensor", -1.0 and "u".

    read(addr, rt=True, temp=default_temp): returns measurement of addresses EZO module. Calls private function _query() (please refer to description above) with same arguments. Returns measurement as float.
            addr, rt, temp: see respective descriptions _write() function.
        uses functions: _query()

    read_t(): returns measurement of RTD EZO module. Calls read() function (please refer to description above) for RDT EZO module measurement. Returns measurement as float.
        uses function read()
        NB: if RTD EZO module not connected, always returns -100.0. For other error values the function is impacted by class mode. In development mode all other exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_ph(rt=False, temp=default_temp): returns measurement of pH EZO module. Calls read() function (please refer to description above) for PH EZO module measurement. Returns measurement as float.
            rt, temp: see respective descriptions _write() function.
        uses functions: read()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_ec(rt=False, temp=default_temp): returns measurement of EC EZO module. Calls read() function (please refer to description above) for EC EZO module measurement. Returns measurement as float.
            rt, temp: see respective descriptions _write() function.
        uses functions: read()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_do(rt=False, temp=default_temp): returns measurement of DO EZO module. Calls read() function (please refer to description above) for DO EZO module measurement. Returns measurement as float.
            rt, temp: see respective descriptions _write() function.
        uses functions: read()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_orp(): returns measurement of ORP EZO module. Calls read() function (please refer to description above) for ORP EZO module  measurement. Returns measurement as float.
        uses function read()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_multi(addr, mode="seq", rt=True, manual_temp_override=False, override_temp=default_temp): returns measurements of several EZO modules in one go as a list of floats in the same order as the EZO modules addresses in addr list argument.
            manual_temp_override: Boolean argument, default value: False. Allows to manually override temperature compensation even when RTD EZO module is connected.
            addr, mode, rt, override_temp : see respective descriptions of _query_multi() function
        uses functions: check_addr(), read(), read_t(), _query_multi()
        NB.1: This function have a built-in "live" temperature correction option when RTD EZO module is connected that can be used accordingly to the following examples:
                - read_multi(LIST_OF_ADDRESSES) : reads RTD measurement first and uses it to sequentially querying other EZO modules with addresses contained in LIST_OF_ADDRESSES allowing temperature compensation.
                - read_multi(LIST_OF_ADDRESSES, "sim") : reads RTD measurement first and uses it to simultaneously querying other EZO modules with addresses contained in LIST_OF_ADDRESSES allowing temperature compensation
        NB.2: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    read_all(mode="seq", rt=True, manual_temp_override=False, override_temp=default_temp): returns measurements all connected EZO modules by calling read_multi(). Returns measurements as floats list in the following order of connected EZO modules : ["rtd", "ph", "ec", "do", "orp"]
            mode, rt, override_temp : see respective descriptions of _query_multi() function
        uses functions: read_multi()
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode please refer to _read() description of error values.

    set_t(temp=default_temp): manually setting temperature for temperature compensation to all EZO modules allowing this option by sending "T,temp" command to them.
            temp: see description in _write() function.

    sleep(addr): puts EZO module with addr address to sleep.
            addr: see description in _check_addr() function
        uses functions: _check_addr()

    sleep_all(): puts all connected EZO modules to sleep.

    wake(addr): wakes EZO module with addr address.
            addr: see description in _check_addr() function
        uses functions: _check_addr()

    wake all(): wakes all connected EZO modules.

    led(addr, state=1): turns LED of EZO module with addr address on or off.
            addr: see description in _check_addr() function
            state: Integer Argument, default value: 1. Defines the state of the EZO module LED: 1=ON, 0=OFF
        uses functions: _check_addr()

    led_all(state=1): turn LEDs of all connected EZO modules on or off in one go.
            state: see description in led() function
        uses functions: _check_addr()

    addr_change(old_addr, new_addr): changes I2C address of EZO module with old_addr address to new_addr address using "I2C,new_addr" command
            old_addr: see definition of addr in _check_addr() function
            new_addr: Integer argument, default value: none. New desired address for EZO module. Must be an integer in range of 1-127 and not be atributed to an already connected EZO module.
        NB: old_addr is replaced by new_addr in private self._addresses list. However it is NOT replaced automatically in any address list or variable in the code calling this class function! It is very strongly recommended to update any address list or variable with addresses() function right after calling addr_change() function.

    addr_reset(): resets connected EZO modules's addresses to default values.
        NB.1: default addresses are: RTD = 102, pH = 99, EC = 100, DO = 97 and ORP = 98
        NB.2: rather time consuming function. For 3 connected sensors the execution time is about 12 seconds.

    mode_change(mode=""): changes class mode.
            mode: Non-case sensitive string argument, default value: Void. If called without this argument, the function changes class mode from "op" to "dev" or the other way around. If mode argument is given as "op" or "dev" in the function call, it changes the class mode to adequate mode.

    cmd(addr, cmd): sends custom command to EZO module with address addr. USE AT YOUR OWN RISK...
            addr: see definition of addr in _check_addr() function.
            cmd: String argument, no default value. Should correspond to any commands described in Atlas Scientific EZO modules datasheets (examples: "R", "RT,temp", "I", "Find", "Cal,mid,7.00", etc...)
        NB: function impacted by class mode. In development mode all exceptions will be raised. In operation mode NO EXCEPTION WILL BE RAISED WHAT SO EVER...

    addresses(): returns list of connected EZO modules addresses' as list of integers.

    sensors(): returns list of connected EZO modules names' as list of strings.

    versions(): returns list of connected EZO modules versions' as list of floats.

    units(): returns list of connected EZO modules units' as list of strings.

'''

import smbus
import fcntl
import time
import io

class AtlasHydroTools:

    # factory default EZO modules addresses.
    _def_rtd_add = 102  # (102 by default)
    _def_ph_add = 99  # (99 by default)
    _def_ec_add = 100  # (100 by default)
    _def_do_add = 97  # (97 by default)
    _def_orp_add = 98  # (98 by default)

    default_temp = 25.0  # default temperature (in °C) for Atlas Scientific pH, EC and DO EZO modules temperature compensation (25.0 by default).

    # ========== CONSTRUCTOR/DESTRUCTOR (please refer to descriptions in this file header) ==========#

    def __init__(self, mode="op", silent=True, keep_awake=True):

        self.silent = silent  # defining silent behaviour of the class.
        self.keep_awake = keep_awake  # defining class handling of putting to sleep connected EZO modules in class destructor.

        self._def_bus = 1  # default bus (1 by default).
        self._I2C_SLAVE = 0x703  # needed fro the io operations (0x703 by default).
        self._def_sensors = ["rtd", "ph", "ec", "do", "orp"] # default sensors names and their prefered list order (["rtd", "ph", "ec", "do", "orp"] by default).
        self._def_units = ["°C", "", "uS/cm", "mg/L", "mV"]  # list of EZO modules' units for print purposes. Should be same order as in self.def_addresses (["°C", "", "uS/cm", "mg/L", "mV"] by default).
        self._long_timeout = .9  # sleep timeout period for pH (R and RT commands), EC (R and RT commands) and DO (RT command) EZO modules (0.9 sec (900ms) by default).
        self._medium_timeout = .6  # sleep timeout period for RTD (R command), DO (R command) ORP (R command) EZO modules (0.6 sec (600ms) by default).
        self._short_timeout = .3  # sleep timeout period for set_t function and other EZO modules commands (0.3 sec (300ms) by default).

        self._file_write = io.open("/dev/i2c-" + str(self._def_bus), "wb", buffering=0)  # used to send commands to EZO modules of more than one char (eg. "RT,23.2").
        self._bus = smbus.SMBus(self._def_bus)  # used to send one char commands to EZO modules and read from EZO modules.

        # way that the class handles exceptions.
        if mode == "dev":
            self.mode = mode
        else:
            self.mode = "op"

        # min and max water temp (in °C) allowed for temperature compensation of pH, EC and DO sensors. Given/Measured temperatures for temperature compensation outside this range will be considered as faulty and replaced with default_temp.
        self.minH2Otemp = 0.0
        self.maxH2Otemp = 100.0

        self._no_rt = ["rtd", "orp"]  # EZO modules that do not have temperature correction function.

        if not silent:
            print("\nAtlasScientific class constructed with following parameters:")
            print("\tErrors management mode:", self.mode)
            print("\tSilent mode:", self.silent, "(obviously... if you are reading this message)")
            print("\tGoing to keep EZO modules awake at end of code:", self.keep_awake)

        self.scan()  # scanning and initialising connected modules.

    def __del__(self, keep_awake=False):
        keep_awake = self.keep_awake
        if not keep_awake:
            if not self.silent:
                print("Putting to sleep all connected modules...")
            for addr in self._addresses:
                cmd = "sleep" + "\00"
                fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
                self._file_write.write(cmd.encode('latin-1'))
        self._bus.close()


# ========== PRIVATE FUNCTIONS (please refer to descriptions in this file header) ==========#

    def _check_addr(self,addr):
        if isinstance(addr, bool):
            raise AddrTypeError
        elif isinstance(addr, int):
            if addr in range(1, 128):
                if addr in self._addresses:
                    return addr
                else:
                    raise EZOnotConnected
            else:
                raise AddrRangeError
        elif isinstance(addr, str):
            if addr in self._sensors:
                return self._addresses[self._sensors.index(addr)]
            elif addr in self._def_sensors:
                raise EZOnotConnected
            else:
                raise AddrRangeError
        else:
            raise AddrTypeError

    def _write(self, addr, rt=True, temp=default_temp):
        addr = self._check_addr(addr)
        if not rt or self._sensors[self._addresses.index(addr)] in self._no_rt:  # queries of RTD and ORP sensors are made with "R" command as they don't have temperature compensation function.
            self._bus.write_byte(addr, ord("R"))
            if not self.silent:
                print("cmd sent: \"R\" to I2C address", addr)
        else:  # queries of all other sensor is made with "RT,temperature" command for temperature compensation.
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            if self.minH2Otemp < temp < self.maxH2Otemp:
                pass
            else:
                temp = self.default_temp
            cmd = "RT," + str(temp) + "\00"
            self._file_write.write(cmd.encode('latin-1'))
            if not self.silent:
                print("cmd sent: \"", cmd, "\" to I2C address", addr)

    def _read(self, addr):
        try:
            addr = self._check_addr(addr)
            res = self._bus.read_i2c_block_data(addr, 0x32, 16)
            char_list = "".join(chr(x) for x in res[1:] if x != 0)
            return float(char_list)
        except EZOnotConnected:
            if self.mode == "op" or (not self._rtd and (addr == self._def_sensors[self._def_sensors.index("rtd")] or addr == self._def_rtd_add)):
                return -100.0  # error value in operation mode when no EZO module connected to this address.
            else:
                raise EZOnotConnected
        except ValueError:
            if self.mode == "op":
                return -200.00  # error value in operation mode when EZO module had nothing to give when tried to be read from.
            else:
                return EZOnotReady
        except OSError:
            if self.mode == "op":
                return -1000.0  # argument addr corresponds to a connected EZO module's address but is not responding correctly.
            else:
                raise EZOError

    def _query(self, addr, rt=True, temp=default_temp):
        try:
            self._write(addr, rt, temp)
        except EZOnotConnected:
            if self.mode == "op" or (not self._rtd and (addr == self._def_sensors[self._def_sensors.index("rtd")] or addr == self._def_rtd_add)):
                return -100.0 # error value in operation mode when no EZO module connected to this address.
            else:
                raise EZOnotConnected
        except OSError:
            if self.mode == "op":
                return -1000.0 # argument addr corresponds to a connected EZO module's address but is not responding correctly.
            else:
                raise EZOError

        if self._sensors[self._addresses.index(self._check_addr(addr))] == "rtd" or (not rt and self._sensors[self._addresses.index(self._check_addr(addr))] in ["ec", "do"]):
            if not self.silent:
                print("Sleeping for", self._medium_timeout * 1000, "msec...")
            time.sleep(self._medium_timeout)
        else:
            if not self.silent:
                print("Sleeping for", self._long_timeout * 1000, "msec...")
            time.sleep(self._long_timeout)

        return self._read(addr)

    def _query_multi(self, addr, rt=True, temp=default_temp):
        readings = [-2000.0] * len(addr)  # initialisation of readings list. A final reading resulting in -2000.0 would mean the value in this list was not replaced. Technically something went wrong somewhere...

        for address in addr:
            try:
                self._write(address, rt, temp)
            except EZOnotConnected:
                if self.mode == "op" or (not self._rtd and (addr == self._def_sensors[self._def_sensors.index("rtd")] or addr == self._def_rtd_add)):
                    readings[addr.index(address)] = -100.0  # error value in operation mode when no EZO module connected to this address.
                else:
                    raise EZOnotConnected
            except OSError:
                if self.mode == "op":
                    readings[addr.index(address)] = -1000.0  # argument addr corresponds to a connected EZO module's address but is not responding correctly. EZO module was asleep OR is faulty OR its' I2C address was changed without using addr_change() function OR an undetected during debugging process error occurred.
                else:
                    raise EZOError

        sensors = []
        for address in addr:
            try:
                sensors.append(self._sensors[self._addresses.index(address)])
            except ValueError:
                sensors.append(addr)

        if (rt and any(elem in sensors for elem in ["ph", "ec", "do"])) or (not rt and any(elem in sensors for elem in ["ph", "orp"])):
            if not self.silent:
                print("Sleeping for", self._long_timeout*1000, "msec...")
            time.sleep(self._long_timeout)
        else:
            if not self.silent:
                print("Sleeping for", self._medium_timeout*1000, "msec...")
            time.sleep(self._medium_timeout)

        for address in addr:
            if readings[addr.index(address)] != -100.0:
                    readings[addr.index(address)] = self._read(address)

        return readings


# ========== PUBLIC FUNCTIONS (please refer to descriptions in this file header) ==========#

    def scan(self):  # waking up, scanning and detecting ports on witch EZO modules are connected. Storing EZO modules addresses, types, units and version.
        # initialisation list of connected EZO modules' addresses.
        self._init_addresses = []

        time.sleep(self._short_timeout)

        # waking up any asleep connected EZO modules with default addresses
        for addr in range(1, 128):
            try:
                cmd = "L,1" + "\00"
                fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
                self._file_write.write(cmd.encode('latin-1'))
            except (IOError, OSError):
                pass
        time.sleep(self._short_timeout)

        # scanning for connected EZO modules
        if not self.silent:
            print("\nScanning for connected EZO modules...")
        for addr in range(1, 128):
            try:
                self._bus.read_byte(addr)
                self._init_addresses.append(addr)
            except (IOError, OSError):
                pass
        time.sleep(self._short_timeout)

        # initialisation lists of connected EZO modules' names, units and versions.
        self._init_sensors = [" "] * len(self._init_addresses)
        self._init_units = [" "] * len(self._init_addresses)
        self._init_versions = [0.0] * len(self._init_addresses)

        # initialisation of the lists of connected EZO modules' names, units and versions.
        for addr in self._init_addresses:
            self._bus.write_byte(addr, ord("I"))
        time.sleep(self._medium_timeout)

        for addr in self._init_addresses:
            res = self._bus.read_i2c_block_data(addr, 0x32, 16)
            info = "".join(chr(x) for x in res[1:] if x != 0)
            if len(info) > 0 and info[0] == "?" and info.count(",") == 2:
                self._init_sensors[self._init_addresses.index(addr)] = str(info.split(",")[1]).lower()
                self._init_versions[self._init_addresses.index(addr)] = float(info.split(",")[2])
                self._init_units[self._init_addresses.index(addr)] = self._def_units[self._def_sensors.index(self._init_sensors[self._init_addresses.index(addr)])]
            else:
                self._init_sensors[self._init_addresses.index(addr)] = "Unknown Sensor"
                self._init_versions[self._init_addresses.index(addr)] = -1.0
                self._init_units[self._init_addresses.index(addr)] = "u"

        # detecting presence of connected RTD EZO module
        self._rtd = "rtd" in self._init_sensors

        self._addresses = []
        self._sensors = []
        self._versions = []
        self._units = []

        # reordering connected EZO sensors in following order : rtd, ph, ec, do, orp
        for sensor in self._def_sensors:
            if sensor in self._init_sensors:
                self._addresses.append(self._init_addresses[self._init_sensors.index(sensor)])
                self._sensors.append(sensor)
                self._versions.append(self._init_versions[self._init_sensors.index(sensor)])
                self._units.append(self._init_units[self._init_sensors.index(sensor)])

        if not self.silent:
            print("\n" + str(len(self._addresses)) + " connected EZO modules detected:")
            for i in range(len(self._addresses)):
                print("\t", self._sensors[i], "\b, address:", self._addresses[i], "\b, version:", self._versions[i], "\b, unit:", self._units[i])

        time.sleep(self._short_timeout)

    def read(self, addr, rt=True, temp=default_temp):
        return self._query(addr, rt, temp)

    def read_t(self):
        if self._rtd:
            return self.read(self._addresses[self._sensors.index("rtd")])
        else:
            return -100.0

    def read_ph(self, rt=False, temp=default_temp):
        try:
            return self.read(self._addresses[self._sensors.index("ph")], rt, temp)
        except ValueError:
            if self.mode =="op":
                return -100.00
            else:
                raise EZOnotConnected

    def read_ec(self, rt=False, temp=default_temp):
        try:
            return self.read(self._addresses[self._sensors.index("ec")], rt, temp)
        except ValueError:
            if self.mode =="op":
                return -100.00
            else:
                raise EZOnotConnected

    def read_do(self, rt=False, temp=default_temp):
        try:
            return self.read(self._addresses[self._sensors.index("do")], rt, temp)
        except ValueError:
            if self.mode =="op":
                return -100.00
            else:
                raise EZOnotConnected

    def read_orp(self):
        try:
            return self.read(self._addresses[self._sensors.index("orp")])
        except ValueError:
            if self.mode =="op":
                return -100.00
            else:
                raise EZOnotConnected

    def read_multi(self, addr, mode="seq", rt=True, manual_temp_override=False, override_temp=default_temp):  # reads multiple sensors in one go.
        if mode.lower() in ["seq", "sim"]:
            readings = [-2000.0] * len(addr)

            for i in range(len(addr)):
                try:
                    addr[i] = self._check_addr(addr[i])
                except EZOnotConnected:
                    if self.mode == "op" or (not self._rtd and (addr == self._def_sensors[self._def_sensors.index("rtd")] or addr == self._def_rtd_add)):
                        readings[i] = -100.0  # error value in operation mode when no EZO module connected to this address.
                    else:
                        raise EZOnotConnected
                except OSError:
                    if self.mode == "op":
                        readings[i] =  -1000.0  # argument addr corresponds to a connected EZO module's address but is not responding correctly
                    else:
                        raise EZOError

            if rt and not manual_temp_override:
                try:
                    readings[addr.index(self._addresses[self._sensors.index("rtd")])] = self.read_t()
                    override_temp = readings[addr.index(self._addresses[self._sensors.index("rtd")])]
                except ValueError:
                    pass

            if mode.lower() == "seq":
                for address in addr:
                    if readings[addr.index(address)] == -2000.0:
                        readings[addr.index(address)] = self.read(address, rt, override_temp)
            elif mode.lower() == "sim":
                readings = self._query_multi(addr, rt, override_temp)
        else:
            raise ReadMultiError

        return readings

    def read_all(self, mode="seq", rt=True, manual_temp_override=False, override_temp=default_temp):  # reads all connected EZO modules by calling read_multi() function.
        return self.read_multi(self._addresses, mode, rt, manual_temp_override, override_temp)

    def set_t(self, temp=default_temp):
        cmd = "T," + str(temp) + "\00"
        for addr in self._addresses:
            if not (self._sensors[self._addresses.index(addr)] in ["rtd", "orp"]):
                fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
                self._file_write.write(cmd.encode('latin-1'))
                if not self.silent:
                    print("cmd sent : \"", cmd, "\" to I2C address", addr)
        time.sleep(self._short_timeout)

    def sleep(self, addr):
        try:
            addr = self._check_addr(addr)
        except Exception:
            pass

        cmd = "sleep" + "\00"
        try:
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            self._file_write.write(cmd.encode('latin-1'))
            if not self.silent:
                print("cmd sent: \"", cmd, "\" to I2C address", addr)
            time.sleep(self._short_timeout)
        except (IOError, OSError):
            pass

    def wake(self,addr):
        try:
            addr = self._check_addr(addr)
        except Exception:
            pass

        cmd = "L,1" + "\00"
        try:
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            self._file_write.write(cmd.encode('latin-1'))
        except (IOError, OSError):
            if not self.silent:
                print("waking-up cmd sent: \"", cmd, "\" to I2C address", addr)
                time.sleep(self._short_timeout)
            pass

    def sleep_all(self):
        for addr in self._addresses:
            cmd = "sleep" + "\00"
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            self._file_write.write(cmd.encode('latin-1'))
            if not self.silent:
                print("cmd sent: \"", cmd, "\" to I2C address", addr)
        time.sleep(self._short_timeout)

    def wake_all(self):
        for addr in self._addresses:
            cmd = "L,1" + "\00"
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            try:
                self._file_write.write(cmd.encode('latin-1'))
                if not self.silent:
                    print("cmd sent: \"", cmd, "\" to I2C address", addr)
            except OSError:
                pass
        time.sleep(self._short_timeout)

    def led(self, addr, state=1):
        try:
            addr = self._check_addr(addr)
        except Exception:
            pass

        cmd = "L," + str(state) + "\00"
        try:
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            self._file_write.write(cmd.encode('latin-1'))
            if not self.silent:
                print("cmd sent: \"", cmd, "\" to I2C address", addr)
            time.sleep(self._short_timeout)
        except (IOError, OSError):
            pass

    def led_all(self, state=1):

        for addr in self._addresses:
            try:
                addr = self._check_addr(addr)
            except Exception:
                pass

            cmd = "L," + str(state) + "\00"
            try:
                fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
                self._file_write.write(cmd.encode('latin-1'))
                if not self.silent:
                    print("cmd sent: \"", cmd, "\" to I2C address", addr)
            except (IOError, OSError):
                pass
        time.sleep(self._short_timeout)

    def addr_change(self, old_addr, new_addr):
        old_addr = self._check_addr(old_addr)

        time.sleep(self._short_timeout)

        if new_addr in self._addresses or not isinstance(new_addr, int) or new_addr not in range(1,128):
            raise AddrChangeError

        cmd = "I2C," + str(new_addr) + "\00"
        fcntl.ioctl(self._file_write, self._I2C_SLAVE, old_addr)
        self._file_write.write(cmd.encode('latin-1'))
        self._addresses[self._addresses.index(old_addr)] = new_addr
        if not self.silent:
            print("cmd sent: \"", cmd, "\" to I2C address", old_addr)
            print(self._sensors[self._addresses.index(new_addr)].upper(),"EZO module I2C address changed from", old_addr, "to", new_addr)
            print("IMPORTANT: don't forget to update your local address list and/or variable...")
        time.sleep(self._long_timeout)

    def addr_reset(self):
        if not self.silent:
            print("\n-!-!-!-!-!-!-!- RESETTING EZO MODULES ADDRESSES TO DEFAULT VALUES -!-!-!-!-!-!-!-")

        self._def_addresses = [self._def_rtd_add, self._def_ph_add, self._def_ec_add, self._def_do_add, self._def_orp_add]

        time.sleep(self._short_timeout)

        self.scan()

        if not self.silent:
            print("\n")

        i = 1
        for addr in self._addresses:
            continue_looping = True
            while continue_looping:
                try:
                    self._bus.read_byte(i)
                except (IOError, OSError):
                    time.sleep(self._short_timeout)
                    self.addr_change(addr, i)
                    continue_looping = False
                i += 1

        self.scan()

        if not self.silent:
            print("\n")

        for n in range(len(self._addresses)):
            self.addr_change(self._addresses[n], self._def_addresses[self._def_sensors.index(self._sensors[n])])
            self._addresses[n] = self._def_addresses[self._def_sensors.index(self._sensors[n])]
            if not self.silent:
                print(self._sensors[n].upper(), "I2C address reset to default value:", self._addresses[n])

        if not self.silent:
            print("\n-!-!-!-!-!-!-!- RESETTING COMPLETE -!-!-!-!-!-!-!-")
        time.sleep(self._long_timeout)

    def mode_change(self, mode=""):
        if not isinstance(mode, str) or not mode.lower() in ["", "dev", "op"]:
            raise ModeError
        elif mode == "":
            if self.mode == "op":
                self.mode = "dev"
                if not self.silent:
                    print("Mode switched to development. All known errors will be raised.")
            else:
                self.mode = "op"
                if not self.silent:
                    print("Mode switched to operation. Certain known errors will be returned as absurd negative values. Please refer to library header for more information")
        elif mode.lower() == "op":
            self.mode = "op"
            if not self.silent:
                print("Mode switched to operation. Certain known errors will be returned as absurd negative values. Please refer to library header for more information")
        elif mode.lower() == "dev":
            self.mode = "dev"
            if not self.silent:
                print("Mode switched to development. All known errors will be raised.")

    def cmd(self, addr, cmd):
        if self.mode =="op":
            try:
                addr = self._check_addr(addr)
                cmd = str(cmd) + "\00"
                fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
                self._file_write.write(cmd.encode('latin-1'))
                if not self.silent:
                    print("custom cmd sent: \"", cmd, "\" to I2C address", addr)
                time.sleep(self._long_timeout)
            except Exception:
                pass
        elif self.mode == "dev":
            addr = self._check_addr(addr)
            cmd = str(cmd) + "\00"
            fcntl.ioctl(self._file_write, self._I2C_SLAVE, addr)
            self._file_write.write(cmd.encode('latin-1'))
            if not self.silent:
                print("custom cmd sent: \"", cmd, "\" to I2C address", addr)
            time.sleep(self._long_timeout)

    def addresses(self):
        return self._addresses

    def sensors(self):
        return self._sensors

    def versions(self):
        return self._versions

    def units(self):
        return self._units


# ========== LIBRARY RELATED EXCEPTIONS ==========#

class AddrTypeError(Exception):
    def __init__(self, msg=": argument addr is of wrong type. The address argument should be an INTEGER in the range of 1 to 127 OR a STRING containing one of the following : \"rtd\", \"ph\", \"ec\", \"do\", \"orp\" (except for _query_multi() for which the address argument should be a list of one there types with values within mentioned ranges)"):
        super(AddrTypeError, self).__init__(msg)

class AddrRangeError(Exception):
    def __init__(self, msg=": argument addr is not in acceptable range. The address argument should be an INTEGER in the range of 1 to 127 OR a STRING containing one of the following : \"rtd\", \"ph\", \"ec\", \"do\", \"orp\" (except for _query_multi() for which the address argument should be a list of one there types with values within mentioned ranges)"):
        super(AddrRangeError, self).__init__(msg)

class EZOError(Exception):
    def __init__(self, msg=": argument addr corresponds to a connected EZO module's address but is not responding correctly. EZO module was asleep OR is faulty OR its' I2C address was changed without using addr_change() function OR an undetected during debugging process error occurred."):
        super(EZOError, self).__init__(msg)

class EZOnotConnected(Exception):
    def __init__(self, msg=": no EZO module connected to this address."):
        super(EZOnotConnected, self).__init__(msg)

class EZOnotReady(Exception):
    def __init__(self, msg=": EZO module had nothing to give when tried to be read from. Time_out too short or _read() command executed without period valid _write() command"):
        super(EZOnotReady, self).__init__(msg)

class ModeError(Exception):
    def __init__(self, msg="ERROR: incorrect mode argument. Please use \"op\" or \"dev\""):
        super(ModeError, self).__init__(msg)

class ReadMultiError(Exception):
    def __init__(self, msg="ERROR: incorrect read_all() mode argument. Please use \"seq\" or \"sim\""):
        super(ReadMultiError, self).__init__(msg)

class AddrChangeError(Exception):
    def __init__(self, msg="ERROR: new address already taken by other EZO module OR new address is not an integer OR new address in not in range 1-127 !"):
        super(AddrChangeError, self).__init__(msg)


# Example of library functions usage. Runs flawlessly (so far...) on an RPi 3 B+ with an Atlas Scientific Tentacle T3 hat and three EZO modules (RTD, pH and EC) connected to Atlas Scientific PT-1000, pH and K0.1 probes.
if __name__ == '__main__':

    tentacle = AtlasHydroTools("op", False, False)

    addresses = tentacle.addresses()
    sensors = tentacle.sensors()
    units = tentacle.units()
    versions = tentacle.versions()

    n = len(addresses)

    print("\n========== EZO MODULES SPECIFIC FUNCTIONS ==========")

    tentacle.set_t(82.4)
    print("\nChanged temperature compensation value to to 82.4°C")

    print("\nSeparate readings with EZO modules specific functions with last transmitted valid temperature used for temperature compensation:")
    print(sensors[0], "=", tentacle.read_t(), units[0])
    print(sensors[1], "=", tentacle.read_ph(), units[1])
    print(sensors[2], "=", tentacle.read_ec(), units[2])

    print("\nSeparate readings with EZO modules specific functions functions with default temperature for temperature compensation (25°C by default):")
    print(sensors[0], "=", tentacle.read_t(), units[0])
    print(sensors[1], "=", tentacle.read_ph(True), units[1])
    print(sensors[2], "=", tentacle.read_ec(True), units[2])

    print("\nSeparate readings with EZO modules specific functions functions with \"live\" temperature compensation from RTD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default):")
    print(sensors[0], "=", tentacle.read_t(), units[0])
    print(sensors[1], "=", tentacle.read_ph(True, tentacle.read_t()), units[1])
    print(sensors[2], "=", tentacle.read_ec(True, tentacle.read_t()), units[2])

    print("\nSeparate readings with with EZO modules specific functions functions with \"live\" temperature compensation from RTD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default) (quicker but for not very fast temperature changing systems):")
    temp = tentacle.read_t()
    print(sensors[0], "=", temp, units[0])
    print(sensors[1], "=", tentacle.read_ph(True, temp), units[1])
    print(sensors[2], "=", tentacle.read_ec(True, temp), units[2])

    print("\nSeparate readings with EZO modules specific functions functions with manually given temperature (42.0) for temperature compensation or default_temp if manually given temperature value is outside allowed water temperature (0.0-100.0°C by default):")
    manual_temp = 42.0
    print(sensors[0], "=", tentacle.read_t(), units[0])
    print(sensors[1], "=", tentacle.read_ph(True, manual_temp), units[1])
    print(sensors[2], "=", tentacle.read_ec(True, manual_temp), units[2])

    tentacle.mode_change()
    tentacle.addr_change("ph", 3)
    addresses = tentacle.addresses()
    print("Changed pH EZO module address to 3")

    print("\n========== EZO MODULES ADDRESSES ADDRESSING FUNCTION ==========")

    print("\nSeparate readings with EZO module address addressing function with last transmitted valid temperature used for temperature compensation:")
    print(sensors[0], "=", tentacle.read("rtd"), units[0])
    print(sensors[1], "=", tentacle.read_ph(False), units[1])
    print(sensors[1], "=", tentacle.read("ph", False), units[1])
    print(sensors[2], "=", tentacle.read(tentacle._addresses[2], False), units[2])

    tentacle.led_all(0)
    print("Turned all EZO module LEDs off")

    print("\nSeparate readings with EZO module address addressing function with default temperature compensation (25°C by default):")
    print(sensors[0], "=", tentacle.read(addresses[0]), units[0])
    print(sensors[1], "=", tentacle.read(addresses[1]), units[1])
    print(sensors[2], "=", tentacle.read("ec"), units[2])

    print("\nSeparate readings with EZO module address addressing function with manually given temperature (36.6) for temperature compensation or default_temp if manually given temperature value is outside allowed water temperature (0.0-100.0°C by default):")
    manual_temp = 36.6
    print(sensors[0], "=", tentacle.read(102), units[0])
    print(sensors[1], "=", tentacle.read(3, True, manual_temp), units[1])
    print(sensors[2], "=", tentacle.read(addresses[2], True, manual_temp), units[2])

    print("\nSeparate readings with EZO module address addressing function with \"live\" temperature compensation from TRD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default):")
    print(sensors[0], "=", tentacle.read(tentacle._def_rtd_add), units[0])
    print(sensors[1], "=", tentacle.read(tentacle._addresses[tentacle._sensors.index("ph")], True, tentacle.read_t()), units[1])
    print(sensors[2], "=", tentacle.read(100, True, tentacle.read_t()), units[2])

    tentacle.led_all(1)
    print("Turned all EZO module LEDs on")

    print("\nSeparate readings with EZO module address addressing function with \"live\" temperature compensation from RTD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default) (quicker but for not very fast temperature changing systems):")
    temp = tentacle.read("rtd")
    print(sensors[0], "=", temp, units[0])
    print(sensors[1], "=", tentacle.read("ph", True, temp), units[1])
    print(sensors[2], "=", tentacle.read("ec", True, temp), units[2])

    tentacle.mode_change("op")

    tentacle.sleep(102)
    time.sleep(2)
    tentacle.wake(102)

    print("\n========== SEQUENTIAL EZO MODULES READING FUNCTION ==========")

    print("\nSequential readings of all connected EZO modules with \"live\" temperature used for temperature compensation taken from RTD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default):")
    seq = tentacle.read_all()
    for i in range(len(seq)):
        print(sensors[i], "=", seq[i], units[i])

    tentacle.addr_change("ec", 65)
    addresses[sensors.index("ec")] = 65
    print("Changed EC EZO module address to 65")

    print("\nSequential readings of all connected EZO modules with default_temperature (25°C by default) used for temperature compensation:")
    seq = tentacle.read_all("seq", True, True)
    for i in range(len(seq)):
        print(sensors[i], "=", seq[i], units[i])

    tentacle.scan()

    print("\nSequential readings of all connected EZO modules with manually given temperature (3.5) for temperature compensation or default_temp (25°C by default) if manually given temperature value is outside allowed water temperature (0.0-100.0°C by default):")
    manual_temp = 3.5
    seq = tentacle.read_all("seq", True, True, manual_temp)
    for i in range(len(seq)):
        print(sensors[i], "=", seq[i], units[i])

    tentacle.set_t(99.9)
    print("\nChanged temperature compensation value to 99.9°C")

    print("\nSequential readings of all connected EZO modules with last transmitted valid temperature used for temperature compensation:")
    seq = tentacle.read_all("seq", False)
    for i in range(len(seq)):
        print(sensors[i], "=", seq[i], units[i])

    tentacle.mode_change("dev")
    tentacle.led("ec", 0)
    print("Turned EC EZO module LED off")

    print("\n========== SIMULTANEOUS EZO MODULES READING FUNCTION ==========")

    print("\nSimultaneous reading of all EZO modules (except RTD read before that) with \"live\" temperature used for temperature compensation taken from RTD sensor or default_temp if RTD EZO module missing or RTD sensor return values outside allowed water temperature (0.0-100.0°C by default):")
    sim = tentacle.read_all("sim")
    for i in range(len(sim)):
        print(sensors[i], "=", sim[i], units[i])

    tentacle.set_t(50.0)
    print("\nChanged temperature compensation value to 50.0°C")

    print("\nSimultaneous reading of all EZO modules with last transmitted valid temperature used for temperature compensation:")
    sim = tentacle.read_all("sim", False)
    for i in range(len(sim)):
        print(sensors[i], "=", sim[i], units[i])

    tentacle.led("ec", 0)
    print("Turned EC EZO module LED on")

    print("\nSimultaneous reading of all EZO modules with default_temperature (25°C by default) used for temperature compensation:")
    sim = tentacle.read_all("sim", True, True)
    for i in range(len(sim)):
        print(sensors[i], "=", sim[i], units[i])

    tentacle.addr_reset()
