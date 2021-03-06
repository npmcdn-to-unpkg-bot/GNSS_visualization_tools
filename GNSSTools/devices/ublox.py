# Tampere University of Technology
#
# DESCRIPTION
# Configuration of ublox: enabling or disabling messages output
# Read data from ublox and store them into matrix
#
# AUTHOR
# Anne-Marie Tobie

import serial
import time
import binascii
import math
import json
from GNSSTools.devices.device import Device
import GNSSTools.tools as tools


class Ublox(Device):

    def __init__(self, com, baud_rate=4800, data_bits=8, parity='N', stop_bit=1, timeout=1,
                 rawdatafile='datatxt/ublox_raw_data.txt', procdatafile='datatxt/ublox_processed_data.txt'):
        super(Ublox, self).__init__()
        self.com = com
        self.baud_rate = baud_rate
        self.data_bits = data_bits
        self.parity = parity
        self.stop_bit = stop_bit
        self.timeout = timeout
        self.rawdatafile = rawdatafile
        self.procdatafile = procdatafile
        try:
            self.device = serial.Serial(self.com, timeout=timeout, stopbits=stop_bit, write_timeout=None,
                                        bytesize=data_bits, rtscts=False, xonxoff=False, parity=parity,
                                        baudrate=baud_rate, inter_byte_timeout=None, dsrdtr=False)
        except:
            raise ValueError('connexion with Ublox device failed')

    def find_message(self):
        # look after a ack or nack message
        # Return:
        # Nak or ack received
        msgsent = time.time()
        wait = 1
        while time.time() < wait + msgsent:
            line = self.device.readline()
            if line[0:4] == b'\xb5b\x05\x01':
                print('ack received')
            elif line[0:4] == b'\xb5b\x05\x00':
                print('nak received')

    def reset(self, command):
        # Permits to make a cold, warm or a hot start reset on the Ublox receiver
        # Input:
        # command: which reset you want to, valid commands: 'Cold RST', 'Warm RST', 'Hot RST'
        # Raise:
        # an error is raised if the command is not valid
        if command == 'Cold RST':
            reset = b'\xB5\x62\x06\x04\x04\x00\xFF\xA1\x02\x00\xB0\x47'
            self.device.write(reset)
            self.find_message()

        elif command == 'Warm RST':
            reset = b'\xB5\x62\x06\x04\x04\x00\x01\x00\x02\x00\x11\x6C'
            self.device.write(reset)
            self.find_message()

        elif command == 'Hot RST':
            reset = b'\xB5\x62\x06\x04\x04\x00\x00\x00\x02\x00\x10\x68'
            self.device.write(reset)
            self.find_message()

        else:
            raise ValueError('Unknown resetting command')

    def enable(self, command):
        # Sets enable messages specified by the command argument
        # Input:
        # command: which message to set enable, valid commands are:
        #               'EPH' to set ephemerides enable
        #               'HUI' to set ionosphere enable
        #               'RAW' to set pseudo range enable
        #               'GGA' to set GGA messages enable
        #               'UBX' to set all ubx messages enable
        #               'NMEA' to set al nmea messages enable
        # Raise:
        # an error is raised if the command is not valid
        if command == 'EPH':
            eph_on = b'\xB5\x62\x06\x01\x03\x00\x0B\x31\x01\x47\xC3'
            self.device.write(eph_on)
            self.find_message()

        elif command == 'HUI':
            hui_on = b'\xB5\x62\x06\x01\x03\x00\x0B\x02\x01\x18\x65 '
            self.device.write(hui_on)
            self.find_message()

        elif command == 'RAW':
            raw_on = b'\xB5\x62\x06\x01\x03\x00\x02\x10\x01\x1D\x66'
            self.device.write(raw_on)
            self.find_message()

        elif command == 'GGA':
            gga = b'\xB5\x62\x06\x01\x03\x00\xF0\x00\x01\xFB\x10'
            self.device.write(gga)
            self.find_message()

        elif command == 'NMEA':  # receive an ack when test
            # DTM   GBS    GGA    GLL    GRS    GSA    GST    GSV    RMC
            # VTG   ZDA    PUBX 00     PUBX 03    PUBX 04
            nmea_on = b'\xB5\x62\x06\x01\x03\x00\xF0\x0A\x01\x05\x24'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x09\x01\x04\x22'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x00\x01\xFB\x10'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x01\x01\xFC\x12'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x06\x01\x01\x1C'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x02\x01\xFD\x14'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x07\x01\x02\x1E'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x03\x01\xFE\x16'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x04\x01\xFF\x18'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x05\x01\x00\x1A'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x08\x01\x03\x20'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x00\x01\xFC\x13'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x03\x01\xFF\x19'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x04\x01\x00\x1B'
            self.device.write(nmea_on)
            self.find_message()
        elif command == 'UBX':
            ubx_on = b'\xB5\x62\x06\x01\x03\x00\x0B\x30\x01\x46\xC1'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x50\x01\x66\x01'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x33\x01\x49\xC7'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x31\x01\x47\xC3'\
                     b'\xB5\x62\x06\x01\x03\x00\x10\x02\x01\x1D\x74'\
                     b'\xB5\x62\x06\x01\x03\x00\x10\x10\x01\x2B\x90'\
                     b'\xB5\x62\x06\x01\x03\x00\x28\x00\x01\x33\xB8'\
                     b'\xB5\x62\x06\x01\x03\x00\x21\x0E\x01\x3A\xBF'\
                     b'\xB5\x62\x06\x01\x03\x00\x21\x08\x01\x34\xB3'\
                     b'\xB5\x62\x06\x01\x03\x00\x21\x0B\x01\x37\xB9'\
                     b'\xB5\x62\x06\x01\x03\x00\x21\x0F\x01\x3B\xC1'\
                     b'\xB5\x62\x06\x01\x03\x00\x21\x0D\x01\x39\xBD'\
                     b'\xB5\x62\x06\x01\x03\x00\x13\x80\x01\x9E\x79'\
                     b'\xB5\x62\x06\x01\x03\x00\x13\x21\x01\x3F\xBB'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x05\x01\x1A\x68'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x09\x01\x1E\x70'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x0B\x01\x20\x74'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x02\x01\x17\x62'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x06\x01\x1B\x6A'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x07\x01\x1C\x6C'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x21\x01\x36\xA0'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x2E\x01\x43\xBA'\
                     b'\xB5\x62\x06\x01\x03\x00\x0A\x08\x01\x1D\x6E'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x60\x01\x6C\x03'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x22\x01\x2E\x87'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x31\x01\x3D\xA5'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x04\x01\x10\x4B'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x40\x01\x4C\xC3'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x01\x01\x0D\x45'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x02\x01\x0E\x47'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x32\x01\x3E\xA7'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x06\x01\x12\x4F'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x03\x01\x0F\x49'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x30\x01\x3C\xA3'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x20\x01\x2C\x83'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x21\x01\x2D\x85'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x11\x01\x1D\x65'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x12\x01\x1E\x67'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x30\x01\x3D\xA6'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x31\x01\x3E\xA8'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x10\x01\x1D\x66'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x13\x01\x20\x6C'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x20\x01\x2D\x86'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x04\x01\x1C\x6F'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x03\x01\x1B\x6D'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x01\x01\x19\x69'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x06\x01\x1E\x73'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x32\x01\x48\xC5'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x02\x01\x18\x65'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x01\x01\x17\x63'\
                     b'\xB5\x62\x06\x01\x03\x00\x0B\x00\x01\x16\x61'\
                     b'\xB5\x62\x06\x01\x03\x00\x10\x15\x01\x30\x9A'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x05\x01\x11\x4D'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x3A\x01\x46\xB7'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x61\x01\x6D\x05'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x39\x01\x45\xB5'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x09\x01\x15\x55'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x34\x01\x40\xAB'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x07\x01\x13\x51'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x3C\x01\x48\xBB'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x35\x01\x41\xAD'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x3B\x01\x47\xB9'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x24\x01\x30\x8B'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x25\x01\x31\x8D'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x23\x01\x2F\x89'\
                     b'\xB5\x62\x06\x01\x03\x00\x01\x26\x01\x32\x8F'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x61\x01\x6E\x08'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x14\x01\x21\x6E'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x15\x01\x22\x70'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x59\x01\x66\xF8'\
                     b'\xB5\x62\x06\x01\x03\x00\x02\x11\x01\x1E\x68'\
                     b'\xB5\x62\x06\x01\x03\x00\x27\x01\x01\x33\xB7'\
                     b'\xB5\x62\x06\x01\x03\x00\x27\x03\x01\x35\xBB'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x11\x01\x29\x89'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x16\x01\x2E\x93'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x13\x01\x2B\x8D'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x12\x01\x2A\x8B'\
                     b'\xB5\x62\x06\x01\x03\x00\x0D\x15\x01\x2D\x91'\
                     b'\xB5\x62\x06\x01\x03\x00\x09\x14\x01\x28\x83'
            self.device.write(ubx_on)
            self.find_message()
        else:
            raise ValueError('Unknown Enabling Command')

    def poll(self, command):
        # poll messages
        # Input:
        # command: which message to poll, valid commands are:
        #               'EPH' to set ephemerides enable
        #               'HUI' to set ionosphere enable
        #               'RAW' to set pseudo range enable
        #               'random' to set CFG-NAV5,NAV-DOP and RXM-SVSI available
        # Raise:
        # an error is raised if the command is not valid
        if command == 'EPH':
            eph_get = b'\xB5\x62\x0B\x31\x00\x00\x3C\xBF'
            self.device.write(eph_get)

        elif command == 'HUI':
            hui_get = b'\xB5\x62\x0B\x02\x00\x00\x0D\x32'
            self.device.write(hui_get)

        elif command == 'RAW':
            raw_get = b'\xB5\x62\x02\x10\x00\x00\x12\x38'
            self.device.write(raw_get)

        elif command == 'random':
            # CFG-NAV5  NAV-DOP  RXM-SVSI
            random_get = b'\xB5\x62\x06\x24\x00\x00\x2A\x84'\
                         b'\xB5\x62\x01\x04\x00\x00\x05\x10'\
                         b'\xB5\x62\x02\x20\x00\x00\x22\x68'
            self.device.write(random_get)

        else:
            raise ValueError('Unknown Polling Command')

    def disable(self, command):
        # disable UBX or NMEA message
        # Input:
        # command: which message to disable, valid commands are:
        #               'UBX' to set all UBX messages disable
        #               'NMEA' to set all NMEA messages disable
        # Raise:
        # an error is raised if the command is not valid
        if command == 'UBX':  # Receive a Nac when test -- pb : UBX msg turn off by default
            disable = b'\xB5\x62\x06\x01\x03\x00\x0B\x30\x01\x45\xC0'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x50\x00\x65\x00'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x33\x00\x48\xC6'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x31\x00\x46\xC2'\
                      b'\xB5\x62\x06\x01\x03\x00\x10\x02\x00\x1C\x73'\
                      b'\xB5\x62\x06\x01\x03\x00\x10\x10\x00\x2A\x8F'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x05\x00\x19\x67'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x09\x00\x1D\x6F'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x0B\x00\x1F\x73'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x02\x00\x16\x61'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x06\x00\x1A\x69'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x07\x00\x1B\x6B'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x21\x00\x35\x9F'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x08\x00\x1C\x6D'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x60\x00\x6B\x02'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x22\x00\x2D\x86'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x31\x00\x3C\xA4'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x04\x00\x0F\x4A'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x40\x00\x4B\xC2'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x01\x00\x0C\x44'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x02\x00\x0D\x46'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x32\x00\x3D\xA6'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x06\x00\x11\x4E'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x03\x00\x0E\x48'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x30\x00\x3B\xA2'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x20\x00\x2B\x82'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x21\x00\x2C\x84'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x11\x00\x1C\x64'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x12\x00\x1D\x66'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x30\x00\x3C\xA5'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x31\x00\x3D\xA7'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x10\x00\x1C\x65'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x11\x00\x1D\x67'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x13\x00\x1F\x6B'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x20\x00\x2C\x85'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x04\x00\x1B\x6E'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x03\x00\x1A\x6C'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x01\x00\x18\x68'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x06\x00\x1D\x72'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x32\x00\x47\xC4'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x02\x00\x17\x64'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x01\x00\x16\x62'\
                      b'\xB5\x62\x06\x01\x03\x00\x0B\x00\x00\x15\x60'\
                      b'\xB5\x62\x06\x01\x03\x00\x10\x15\x00\x2F\x99'\
                      b'\xB5\x62\x06\x01\x03\x00\x28\x00\x00\x32\xB7'\
                      b'\xB5\x62\x06\x01\x03\x00\x21\x0E\x00\x39\xBE'\
                      b'\xB5\x62\x06\x01\x03\x00\x21\x08\x00\x33\xB2'\
                      b'\xB5\x62\x06\x01\x03\x00\x21\x0B\x00\x36\xB8'\
                      b'\xB5\x62\x06\x01\x03\x00\x21\x0F\x00\x3A\xC0'\
                      b'\xB5\x62\x06\x01\x03\x00\x21\x0D\x00\x38\xBC'\
                      b'\xB5\x62\x06\x01\x03\x00\x13\x80\x00\x9D\x78'\
                      b'\xB5\x62\x06\x01\x03\x00\x13\x21\x00\x3E\xBA'\
                      b'\xB5\x62\x06\x01\x03\x00\x0A\x2E\x00\x42\xB9'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x05\x00\x10\x4C'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x3A\x00\x45\xB6'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x61\x00\x6C\x04'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x39\x00\x44\xB4'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x09\x00\x14\x54'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x34\x00\x3F\xAA'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x07\x00\x12\x50'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x3C\x00\x47\xBA'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x35\x00\x40\xAC'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x3B\x00\x46\xB8'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x24\x00\x2F\x8A'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x25\x00\x30\x8C'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x23\x00\x2E\x88'\
                      b'\xB5\x62\x06\x01\x03\x00\x01\x26\x00\x31\x8E'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x61\x00\x6D\x07'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x14\x00\x20\x6D'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x15\x00\x21\x6F'\
                      b'\xB5\x62\x06\x01\x03\x00\x02\x59\x00\x65\xF7'\
                      b'\xB5\x62\x06\x01\x03\x00\x27\x01\x00\x32\xB6'\
                      b'\xB5\x62\x06\x01\x03\x00\x27\x03\x00\x34\xBA'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x11\x00\x28\x88'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x16\x00\x2D\x92'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x13\x00\x2A\x8C'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x12\x00\x29\x8A'\
                      b'\xB5\x62\x06\x01\x03\x00\x0D\x15\x00\x2C\x90'\
                      b'\xB5\x62\x06\x01\x03\x00\x09\x14\x00\x27\x82'
            self.device.write(disable)
            self.find_message()

        elif command == 'NMEA':
            # DTM   GBS    GGA    GLL    GRS    GSA    GST    GSV    RMC
            # VTG   ZDA    PUBX 00     PUBX 03    PUBX 04
            disable = b'\xB5\x62\x06\x01\x03\x00\xF0\x0A\x00\x04\x23'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x09\x00\x03\x21'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x00\x00\xFA\x0F'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x01\x00\xFB\x11'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x06\x00\x00\x1B'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x02\x00\xFC\x13'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x07\x00\x01\x1D'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x03\x00\xFD\x15'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x04\x00\xFE\x17'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x05\x00\xFF\x19'\
                      b'\xB5\x62\x06\x01\x03\x00\xF0\x08\x00\x02\x1F'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x00\x00\xFB\x12'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x03\x00\xFE\x18'\
                      b'\xB5\x62\x06\x01\x03\x00\xF1\x04\x00\xFF\x1A'
            self.device.write(disable)
            self.find_message()

        else:
            raise ValueError('Unknown Disabling Command')

    def miseenforme(self):
        # UBX messages doesn't include \n at the end of each messages, this function explicitly put them
        data = self.fileopen(self.rawdatafile)
        thing = data.read()
        data.close()

        first = thing.replace('b562', '\nb562')
        second = first.replace('2447', '\n2447')
        third = second.replace('0d0a$G', '\n$G')

        data = open(self.procdatafile, 'w')
        data.write(third)
        data.close()

    def klobuchar_data(self):
        # creates the dictionnary of ionospheric data decimal values
        # Return:
        # klobuchar: {
        #    "0": {
        #        "utcls":  UTC - time difference due to leap seconds before event,
        #        "kloa1": Klobuchar - alpha 1 - second/semicircle,
        #        "kloa0": Klobuchar - alpha 0 - second,
        #        "utcwnf": UTC - week number when next leap second event occurs,
        #        "health": Bitmask, every bit represents a GPS SV (1-32). If the bit is set the SV is healthy.,
        #        "kloa3": Klobuchar - alpha 3 - second/semicircle^3,
        #        "klob1": Klobuchar - beta 1 - second/semicircle,
        #        "klob3": Klobuchar - beta 3 - second/semicircle^3,
        #        "utclsf": UTC - time difference due to leap seconds after event,
        #        "kloa2": Klobuchar - alpha 2 - second/semicircle^2,
        #        "klob2": Klobuchar - beta 2 - second/semicircle^2,
        #        "klob0": Klobuchar - beta 0 - second,
        #        "utcwn": UTC - reference week number,
        #        "utca0": UTC - parameter A0,
        #        "utcdn": UTC - day of week when next leap second event occurs,
        #        "utca1": UTC - parameter A1,
        #        "utctow": reference time of week
        #    }
        # }
        #file = self.fileopen(self.procdatafile)
        file = open(self.procdatafile, 'r')
        join = ''
        klobuchar = {}
        i = 0
        for line in file:
            if line[0:12] == 'b5620b024800':
                health = (join.join((line[18:20], line[16:18], line[14:16], line[12:14])))
                utctow = int(join.join((line[58:60], line[56:58], line[54:56], line[52:54])), 16)
                utcwn = int(join.join((line[62:64], line[60:62])), 16)
                utcls = int(join.join((line[66:68], line[64:66])), 16)
                utcwnf = int(join.join((line[70:72], line[68:70])), 16)
                utcdn = int(join.join((line[74:76], line[72:74])), 16)
                utclsf = int(join.join((line[78:80], line[76:78])), 16)
                utca0 = tools.r8(join.join((line[34:36], line[32:34], line[30:32], line[28:30],
                                            line[26:28], line[24:26], line[22:24], line[20:22])))
                utca1 = tools.r8(join.join((line[50:52], line[48:50], line[46:48], line[44:46],
                                            line[42:44], line[40:42], line[38:40], line[36:38])))
                kloa0 = tools.r4(join.join((line[90:92], line[88:90], line[86:88], line[84:86])))
                kloa1 = tools.r4(join.join((line[98:100], line[96:98], line[94:96], line[92:94])))
                kloa2 = tools.r4(join.join((line[106:108], line[104:106], line[102:104], line[100:102])))
                kloa3 = tools.r4(join.join((line[114:116], line[112:114], line[110:112], line[108:110])))
                klob0 = tools.r4(join.join((line[122:124], line[120:122], line[118:120], line[116:118])))
                klob1 = tools.r4(join.join((line[130:132], line[128:130], line[126:128], line[124:126])))
                klob2 = tools.r4(join.join((line[138:140], line[136:138], line[134:136], line[132:134])))
                klob3 = tools.r4(join.join((line[146:148], line[144:146], line[142:144], line[140:142])))

                klobuchar[i] = {'health': health, 'utcwn': utcwn, 'utcls': utcls, 'utcwnf': utcwnf, 'utcdn': utcdn,
                                'utclsf': utclsf, 'utctow': utctow, 'utca0': utca0, 'utca1': utca1, 'kloa0': kloa0,
                                'kloa1': kloa1, 'kloa2': kloa2, 'kloa3': kloa3,
                                'klob0': klob0, 'klob1': klob1, 'klob2': klob2, 'klob3': klob3}
                i += 1
        file.close()
        return klobuchar

    @staticmethod
    def uratometer(uraindex):
        if uraindex <= 6:
            if uraindex == 1:
                ura = 2.8
            elif uraindex == 3:
                ura = 5.7
            elif uraindex == 5:
                ura = 11.3
            else:
                ura = pow(2, (1 + uraindex/2))
        elif 6 < uraindex < 15:
            ura = pow(2, (uraindex - 2))
        else:
            ura = 'no accuracy'
        return ura

    @staticmethod
    def healthmean(healthvalue):
        if healthvalue[0] == '0':
            health = 'Data ok'
        else:
            health = 'Some bad data', healthvalue
        return health

    @staticmethod
    def l2mean(l2):
        if l2 == '00':
            l2say = 'Reserved'
        elif l2 == '01':
            l2say = 'P code ON'
        elif l2 == '10':
            l2say = 'C/A code ON'
        else:
            l2say = 'No idea find yourself!'
        return l2say

    @staticmethod
    def fitintervalmean(flag):
        if flag == 0:
            flagsay = 'Curvefit interval of 4 hours'
        else:
            flagsay = 'Curvefit interval greater than 4 hours'
        return flagsay

    @staticmethod
    def getSignedNumber(number, bitLength):
        mask = (2 ** bitLength) - 1
        if number & (1 << (bitLength - 1)):
            return number | ~mask
        else:
            return number & mask

    def ephemeris_data(self):
        # Stores the EPH data under this way :
        # Return:
        # ephemeris: {'svid': svid, 'wn': wn, 'l2': l2, 'ura': ura, 'health': health,
        #             'iodc': iodc, 'tgd': tgd, 'toc': toc, 'af2': af2, 'af1': af1,
        #             'af0': af0, 'iodesf2': iodesf2, 'crs': crs, 'deltan': deltan,
        #             'm0': m0, 'cuc': cuc, 'e': e, 'cus': cus, 'sqrta': sqrta,
        #             'toe': toe, 'flag': flag, 'aodo': aodo, 'cic': cic, 'omega0': omega0,
        #             'cis': cis, 'i0': i0, 'crc': crc, 'omega': omega, 'omegadot': omegadot,
        #             'iodesf3': iodesf3, 'idot': idot}
        # where:
        #       svid - satellite ID for which this ephemeris data is valid
        #       wn - Week number
        #       l2 -
        #       ura - User Range Accuracy
        #       health
        #       iodc - Issue Of Data Clock
        #       tgd - Estimated group delay differential - seconds
        #       toc - Clock data reference time - seconds
        #       af2 - polynomial coefficient - second/second^2
        #       af1 - polynomial coefficient - second/second
        #       af0 - polynomial coefficient - second
        #       iodesf2 - issue of data ephemeris - subframe 2
        #       crs - amplitude of the sine harmonic correction term to the orbit radius - meters
        #       deltan - mean motion difference from computed value - radians/sec
        #       m0 - mean anomay at reference time - radians
        #       cuc - amplitude of the cosine harmonic correction term to the argument of latitude - radians
        #       e - eccentricity
        #       cus - amplitude of the sine harmonic correction term to the argument of latitude - radians
        #       sqrta - square root of semi major axis - meters^(1/2)
        #       toe - reference time ephemeris - seconds
        #       flag - fit interval flag
        #       aodo - Age Of Data Offset
        #       cic - amplitude of the cosine harmonic correction term to the angle of inclination - radians
        #       omega0 - longitude of ascending node of orbit plane at weekly epoch - radians
        #       cis - amplitude of the sine harmonic correction term to the angle of inclination - radians
        #       i0 - inclinaison angle at reference time - radians
        #       crc - amplitude of the cosine harmonic correction term to the orbit radius - meters
        #       omega - argument of perigee - radians
        #       omegadot - rate of right ascension - radians/second
        #       iodesf3 - issue of data ephemeris subframe 3
        #       idot - rate of inclination angle - radians/second
        file = self.fileopen(self.procdatafile)
        ephemeris = {}
        i = 0
        inter = {}
        j = 0

        def collect(line):
                join = ''
                svid = int(join.join((line[18:20], line[16:18], line[14:16], line[12:14])), 16)
                # SF1D0
                sf1d0 = '{0:024b}'.format(int(join.join((line[32:34], line[30:32], line[28:30])), 16), 2)
                health = self.healthmean(sf1d0[16:22])
                iodcmsb = sf1d0[22:24]
                wn = int(sf1d0[0:10], 2) % 1024
                l2 = self.l2mean(sf1d0[10:12])
                ura = self.uratometer(int(sf1d0[12:16], 2))
                # SF1D4
                sf1d4 = '{0:024b}'.format(int(join.join((line[64:66], line[62:64], line[60:62])), 16), 2)
                tgd = (self.getSignedNumber(int(sf1d4[16:24], 2), 8))*pow(2, -31)
                if tgd != 0:
                    # SF1D5
                    sf1d5 = '{0:024b}'.format(int(join.join((line[72:74], line[70:72], line[68:70])), 16), 2)
                    iodc = int(join.join((iodcmsb, sf1d5[0:8])), 2)
                    toc = int(sf1d5[8:24], 2)*pow(2, 4)
                    # SF1D6
                    sf1d6 = '{0:024b}'.format(int(join.join((line[80:82], line[78:80], line[76:78])), 16), 2)
                    af2 = (self.getSignedNumber(int(sf1d6[0:8], 2), 8))*pow(2, -55)
                    af1 = (self.getSignedNumber(int(sf1d6[8:24], 2), 16))*pow(2, -43)
                    # SF1D7
                    sf1d7 = '{0:024b}'.format(int(join.join((line[88:90], line[86:88], line[84:86])), 16), 2)
                    af0 = (self.getSignedNumber(int(sf1d7[0:22], 2), 22))*pow(2, -31)
                    # SF2D0
                    sf2d0 = '{0:024b}'.format(int(join.join((line[96:98], line[94:96], line[92:94])), 16), 2)
                    iodesf2 = int(sf2d0[0:8], 2)
                    crs = (self.getSignedNumber(int(sf2d0[8:24], 2), 16))*pow(2, -5)
                    # SF2D1
                    sf2d1 = '{0:024b}'.format(int(join.join((line[104:106], line[102:104], line[100:102])), 16), 2)
                    deltan = (self.getSignedNumber(int(sf2d1[0:16], 2), 16))*pow(2, -43)*math.pi
                    m0msb = sf2d1[16:24]
                    # SF2D2
                    sf2d2 = '{0:024b}'.format(int(join.join((line[112:114], line[110:112], line[108:110])), 16), 2)
                    m0 = (self.getSignedNumber(int(join.join((m0msb, sf2d2)), 2), 32))*pow(2, -31)*math.pi
                    # SF2D3
                    sf2d3 = '{0:024b}'.format(int(join.join((line[120:122], line[118:120], line[116:118])), 16), 2)
                    emsb = sf2d3[16:24]
                    cuc = (self.getSignedNumber(int(sf2d3[0:16], 2), 16))*pow(2, -29)
                    # SF2D4
                    sf2d4 = '{0:024b}'.format(int(join.join((line[128:130], line[126:128], line[124:126])), 16), 2)
                    e = (int(join.join((emsb, sf2d4)), 2))*pow(2, -33)
                    # SF2D5
                    sf2d5 = '{0:024b}'.format(int(join.join((line[136:138], line[134:136], line[132:134])), 16), 2)
                    sqrtamsb = sf2d5[16:24]
                    cus = (self.getSignedNumber(int(sf2d5[0:16], 2), 16))*pow(2, -29)
                    # SF2D6
                    sf2d6 = '{0:024b}'.format(int(join.join((line[144:146], line[142:144], line[140:142])), 16), 2)
                    sqrta = (int(join.join((sqrtamsb, sf2d6)), 2))*pow(2, -19)
                    # SF2D7
                    sf2d7 = '{0:024b}'.format(int(join.join((line[152:154], line[150:152], line[148:150])), 16), 2)
                    flag = self.fitintervalmean(sf2d7[17])
                    aodo = int(sf2d7[18:23], 2)
                    toe = int(sf2d7[0:16], 2)*pow(2, 4)
                    # SF3D0
                    sf3d0 = '{0:024b}'.format(int(join.join((line[160:162], line[158:160], line[156:158])), 16), 2)
                    omega0msb = sf3d0[16:24]
                    cic = (self.getSignedNumber(int(sf3d0[0:16], 2), 16))*pow(2, -29)
                    # SF3D1
                    sf3d1 = '{0:024b}'.format(int(join.join((line[168:170], line[166:168], line[164:166])), 16), 2)
                    omega0 = (self.getSignedNumber(int(join.join((omega0msb, sf3d1)), 2), 32))*pow(2, -31)*math.pi
                    # SF3D2
                    sf3d2 = '{0:024b}'.format(int(join.join((line[176:178], line[174:176], line[172:174])), 16), 2)
                    i0msb = sf3d2[16:24]
                    cis = (self.getSignedNumber(int(sf3d2[0:16], 2), 16))*pow(2, -29)
                    # SF3D3
                    sf3d3 = '{0:024b}'.format(int(join.join((line[184:186], line[182:184], line[180:182])), 16), 2)
                    i0 = (self.getSignedNumber(int(join.join((i0msb, sf3d3)), 2), 32))*pow(2, -31)*math.pi
                    # SF3D4
                    sf3d4 = '{0:024b}'.format(int(join.join((line[192:194], line[190:192], line[188:190])), 16), 2)
                    omegamsb = sf3d4[16:24]
                    crc = (self.getSignedNumber(int(sf3d4[0:16], 2), 16))*pow(2, -5)
                    # SF3D5
                    sf3d5 = '{0:024b}'.format(int(join.join((line[200:202], line[198:200], line[196:198])), 16), 2)
                    omega = (self.getSignedNumber(int(join.join((omegamsb, sf3d5)), 2), 32))*pow(2, -31)*math.pi
                    # SF3D6
                    sf3d6 = '{0:024b}'.format(int(join.join((line[208:210], line[206:208], line[204:206])), 16), 2)
                    omegadot = (self.getSignedNumber(int(sf3d6, 2), 24))*pow(2, -43)*math.pi
                    # SF3D7
                    sf3d7 = '{0:024b}'.format(int(join.join((line[216:218], line[214:216], line[212:214])), 16), 2)
                    idot = int(sf3d7[8:22], 2)*pow(2, -43)*math.pi
                    iodesf3 = int(sf3d7[0:8], 2)

                    inter[j] = {'svid': svid, 'wn': wn, 'l2': l2, 'ura': ura, 'health': health,
                                    'iodc': iodc, 'tgd': tgd, 'toc': toc, 'af2': af2, 'af1': af1,
                                    'af0': af0, 'iodesf2': iodesf2, 'crs': crs, 'deltan': deltan,
                                    'm0': m0, 'cuc': cuc, 'e': e, 'cus': cus, 'sqrta': sqrta,
                                    'toe': toe, 'flag': flag, 'aodo': aodo, 'cic': cic, 'omega0': omega0,
                                    'cis': cis, 'i0': i0, 'crc': crc, 'omega': omega, 'omegadot': omegadot,
                                    'iodesf3': iodesf3, 'idot': idot}
        for line in file:
            if line[0:12] == 'b5620b316800':
                if line[0:14] == 'b5620b31680001':
                        inter = {}
                        j = 0
                        collect(line)
                        j += 1
                elif line[0:14] != 'b5620b31680020':
                    collect(line)
                    j += 1
                else:
                    collect(line)
                    ephemeris[i] = inter
                    i += 1


        file.close()
        return ephemeris

    def raw_data(self):
        # Stores the PRN data under this way :
        # Return:
        # raw: {{rcvtow, week, numsv, {{cpmes, prmes, domes, sv, mesqi, cno, lli},{...}}}{...}}
        # where:
        #       rcvtow in ms, Measurement time of week in receiver local time
        #       week in weeks,  Measurement week number in receiver local time
        #       numsv,
        #       cpmes in cycles, Carrier phase measurement [L1 cycles]
        #       prmes in m, Pseudorange measurement [m]
        #       domes in Hz, Doppler measurement (positive sign for approaching satellites) [Hz]
        #       sv, Space Vehicle number
        #       mesqi,  Nav Measurements Quality Indicator: >=4 : PR+DO OK   >=5 : PR+DO+CP OK
        #                                   <6 : likely loss of carrier lock in previous interval
        #       cno in dBHz,  Signal strength C/No
        file = self.fileopen(self.procdatafile)
        raw = {}
        r = 0
        join = ''
        for line in file:
            if line[0:8] == 'b5620210':
                # RXM-RAW
                inter = {}
                i = 0
                rcvtow = int(line[12:20], 16)
                week = int(line[20:24], 16)
                numsv = int(line[24:26], 16)
                for sat in range(numsv):
                    cpmes = int(join.join((line[(42 + 24*sat):(44 + 24*sat)], line[(40 + 24*sat):(42 + 24*sat)],
                                           line[(38 + 24*sat):(40 + 24*sat)], line[(36 + 24*sat):(38 + 24*sat)],
                                           line[(34 + 24*sat):(36 + 24*sat)], line[(32 + 24*sat):(34 + 24*sat)],
                                           line[(30 + 24*sat):(32 + 24*sat)], line[(28 + 24*sat):(30 + 24*sat)])), 16)
                    prmes = int(join.join((line[(58 + 24*sat):(60 + 24*sat)], line[(56 + 24*sat):(58 + 24*sat)],
                                           line[(54 + 24*sat):(56 + 24*sat)], line[(52 + 24*sat):(54 + 24*sat)],
                                           line[(50 + 24*sat):(52 + 24*sat)], line[(48 + 24*sat):(50 + 24*sat)],
                                           line[(46 + 24*sat):(48 + 24*sat)], line[(44 + 24*sat):(46 + 24*sat)])), 16)
                    domes = int(join.join((line[(66 + 24*sat):(68 + 24*sat)], line[(64 + 24*sat):(66 + 24*sat)],
                                           line[(62 + 24*sat):(64 + 24*sat)], line[(60 + 24*sat):(62 + 24*sat)])), 16)
                    sv = int(line[(68 + 24*sat):(70 + 24*sat)], 16)
                    mesqi = int(line[(70 + 24*sat):(72 + 24*sat)], 16)
                    cno = int(line[(72 + 24*sat):(74 + 24*sat)], 16)
                    lli = int(line[(74 + 24*sat):(76 + 24*sat)], 16)
                    inter[i] = {'cpmes': cpmes, 'prmes': prmes, 'domes': domes, 'sv': sv,
                                'mesqui': mesqi, 'C/N0': cno, 'lli': lli}
                    i += 1
                raw[r] = {rcvtow, week, numsv, inter}
                r += 1
        file.close()
        return json.dumps(raw, indent=4)

    def random_data(self):
        # Stores navigation data, DOP data and SVSI data into dictionaries
        # Return:
        # nav: {{dynmodel, fixmode, fixedalt, fixedaltvar, minelev, pdop, tdop,
        #           pacc, tacc, staticholdthresh, dgpstimeout, cnothreshnumsv, cnothresh}{...}}
        # dop: {{itow, gdop, pdop, tdop, vdop, hdop, ndop, edop}{...}}
        # svsi: {{itow, week, numvis, numsv, {{svid, elev, az, age}{...}}}{...}}
        file = self.fileopen(self.procdatafile)
        nav = {}
        n = 0
        dop = {}
        d = 0
        svsi = {}
        s = 0
        join = ''
        for line in file:
            if line[0:12] == 'b56206242400':
                # CFG-NAV5
                # fixedalt in m, fixedaltvar in m^2, minelev in deg, pacc and tacc in m,
                # staticholdthresh in cm/s, dgpstimeout in s, cnothresh in dBHz
                dynmodel = int(line[16:18], 16)
                fixmode = int(line[18:20], 16)
                fixedalt = int(join.join((line[26:28], line[24:26], line[22:24], line[20:22])), 16) * 0.01
                fixedaltvar = int(join.join((line[34:36], line[32:34], line[30:32], line[28:30])), 16) * 0.0001
                minelev = int(line[36:38], 16)
                pdop = int(join.join((line[42:44], line[40:42])), 16) * 0.1
                tdop = int(join.join((line[46:48], line[44:46])), 16) * 0.1
                pacc = int(join.join((line[50:52], line[48:50])), 16)
                tacc = int(join.join((line[54:56], line[52:54])), 16)
                staticholdthresh = int(line[56:58], 16)
                dgpstimeout = int(line[58:60], 16)
                cnothreshnumsv = int(line[60:62], 16)
                cnothresh = int(line[62:64], 16)
                nav[n] = {'Dynmodel': dynmodel, 'fixmode': fixmode, 'fixedalt': fixedalt,
                          'fixedaltvar': fixedaltvar, 'minelev': minelev, 'pdop': pdop,
                          'tdop': tdop, 'pacc': pacc, 'tacc': tacc, 'staticholdthresh': staticholdthresh,
                          'dgpstimeout': dgpstimeout, 'cnothreshnumsv': cnothreshnumsv,
                          'cnothresh': cnothresh}
                n += 1

            if line[0:12] == 'b56201041200':
                # NAV-DOP
                itow = int(join.join((line[18:20], line[16:18], line[14:16], line[12:14])), 16)  # in ms
                gdop = int(join.join((line[22:24], line[20:22])), 16)/100
                pdop = int(join.join((line[26:28], line[24:26])), 16)/100
                tdop = int(join.join((line[30:32], line[28:30])), 16)/100
                vdop = int(join.join((line[34:36], line[32:34])), 16)/100
                hdop = int(join.join((line[38:40], line[36:38])), 16)/100
                ndop = int(join.join((line[42:44], line[40:42])), 16)/100
                edop = int(join.join((line[46:48], line[44:46])), 16)/100
                dop[d] = {'itow': itow, 'gdop': gdop, 'pdop': pdop, 'tdop': tdop, 'vdop': vdop,
                          'hdop': hdop, 'ndop': ndop, 'edop': edop}
                d += 1

            if line[0:8] == 'b5620220':
                # RXM-SVSI
                # itow in ms, week in weeks
                itow = int(join.join((line[18:20], line[16:18], line[14:16], line[12:14])), 16)
                week = int(join.join((line[22:24], line[20:22])), 16)
                numvis = int(line[24:26], 16)
                numsv = int(line[26:28], 16)
                inter = {}
                i = 0
                for sat in range(numsv):
                    svid = int(line[(28+12*sat):(30+12*sat)], 16)
                    azim = self.getSignedNumber(int(join.join((line[(34+12*sat):(36+12*sat)], line[(32+12*sat):(34+12*sat)])), 16), 16)
                    elev = self.getSignedNumber(int(line[(36+12*sat):(38+12*sat)], 16), 8)
                    age = int(line[(38+12*sat):(40+12*sat)], 16)
                    inter[i] = {'svid': svid, 'azim': azim, 'elev': elev, 'age': age}
                    i += 1
                svsi[s] = {'itow': itow, 'week': week, 'numvis': numvis, 'numsv': numsv,
                           'info': inter}
                s += 1
        file.close()
        return nav, dop, svsi

    def navclock_data(self):
        # Stores clock solution data into a dictionary
        # Return:
        # clock:{
        #    "0": {
        #        "itow": GPS time of week of the navigation epoch in ms,
        #        "clockbias": Clock bias inns,
        #        "clockdrift": Clock drift in ns/s,
        #        "tacc": Time accuracy estimate in ns,
        #     }
        #     {...}
        # }
        file = self.fileopen(self.procdatafile)
        clock = {}
        clk = 0
        join = ''
        for line in file:
            if line[0:12] == 'b5620122':
                itow = int(join.join((line[18:20], line[16:18], line[14:16], line[12:14])), 16)  # in ms
                clockbias = int(join.join((line[26:28], line[24:26], line[22:24], line[20:22])), 16)  # in ns
                clockdrift = int(join.join((line[34:36], line[32:34], line[30:32], line[28:30])), 16)  # in ns/s
                tacc = int(join.join((line[42:44], line[40:42], line[38:40], line[36:38])), 16)  # in ns
                clock[clk] = {'itow': itow, 'clockbias': clockbias, 'clockdrift': clockdrift, 'tacc': tacc}
                clk += 1
        file.close()
        return clock

    def nmea_data_gbs(self):
        # Stores NMEA GBS data into a dictionary
        # Return:
        # satfaultdetection:{
        #    "0": {
        #        "Errlat": expected error in latitude in meters,
        #        "Errlong": expected error in longitude in meters,
        #        "Erralt": expected error in altitude in meters,
        #        "time": time in seconds,
        #        "SatIDfailed": gives the sat ID of most likely failed sat
        #     }
        #     {...}
        # }
        file = self.fileopen(self.procdatafile)
        satfaultdetection = {}
        i = 0
        for line in file:
            if line[3:6] == 'GBS':
                data = line.split(',')
                tme = data[1]
                errlat = data[2]
                errlong = data[3]
                erralt = data[4]
                svid = data[5]
                satfaultdetection[i] = {'time': tme, 'Errlat': errlat, 'Errlong': errlong,
                                        'Erralt': erralt, 'SatIDfailed': svid}
                i += 1
        file.close()
        return satfaultdetection

    def nmea_data_gsa(self):
        # Stores NMEA GSA data into a dictionary
        # Return:
        # dopandactivesat:{
        # "0": {
        #        "PDOP": "5.72",
        #        "active sat": [
        #            "09",
        #            "27",
        #            "12"
        #        ],
        #        "HDOP": "5.64",
        #        "VDOP": "1.00"
        #    }
        #    "1": {...}
        # }
        file = self.fileopen(self.procdatafile)
        dopandactivesat = {}
        i = 0
        for line in file:
            if line[3:6] == 'GSA':
                data = line.split(',')
                j = 0
                while data[3 + j] != '' and j < 14:
                    j += 1
                activesat = data[3: (3 + j)]
                pdop = data[15]
                hdop = data[16]
                k = 0
                while data[17][k] != '*':
                    k += 1
                vdop = data[17][0: k]
                dopandactivesat[i] = {'active sat': activesat, 'PDOP': pdop, 'HDOP': hdop,
                                      'VDOP': vdop}
                i += 1
        file.close()
        return dopandactivesat

    def nmea_data_vtg(self):
        # Stores NMEA VTG data into a dictionary
        # Return:
        # courseandspeed: {
        #    "0": {
        #        "speed in knots": speed over ground in knots,
        #        "speed in km per hour": speed over ground in kilometer per hour,
        #        "course over ground": course over ground true in degrees
        #    },
        #    "1":{...
        #    }
        # }
        file = self.fileopen(self.procdatafile)
        courseandspeed = {}
        i = 0
        for line in file:
            if line[3:6] == 'VTG':
                data = line.split(',')
                cogt = data[1]
                spd = data[5]
                kph = data[7]
                courseandspeed[i] = {'course over ground': cogt, 'speed in knots': spd,
                                     'speed in km per hour': kph}
                i += 1
        file.close()
        return courseandspeed

    def nmea_data_pubx3(self):
        # Stores NMEA PUBX 03 data into a dictionary
        # Return:
        # satinview: {
        #    "0": {
        #        "nb of sat": 1,
        #        "info": {
        #            "0": {
        #                "azimuth": azimut in degrees,
        #                "SV ID": ,
        #                "elevation": elevation in degrees,
        #                "SV status": ,
        #                "C/N0": cno in dBHz
        #            }
        #        }
        #    },
        #    "1": {...
        #       }
        #   }
        # where: az =
        #        elev =
        #
        file = self.fileopen(self.procdatafile)
        satinview = {}
        k = 0
        for line in file:
            if line[0:8] == '$PUBX,03' and len(line) > 17:
                data = line.split(',')
                inter = {}
                j = 0
                nbsat = int(data[2])
                for i in range(nbsat):
                    svid = data[3 + i*6]
                    svstatus = data[4 + i*6]
                    az = data[5 + i*6]
                    elev = data[6 + i*6]
                    cno = data[7 + i*6]
                    inter[j] = {'SV ID': svid, 'SV status': svstatus, 'azimuth': az,
                                'elevation': elev, 'C/N0': cno}
                    j += 1
                satinview[k] = {'nb of sat': nbsat, 'info': inter}
                k += 1
        file.close()
        return satinview

    def pos_with_eph(self):
        # Compute the ECEF position from ephemeris :
        # Return:
        # pos: {
        #    "0": {
        #        "y": ECEF y ,
        #        "z": ECEF z,
        #        "x": ECEF x,
        #        "svid":
        #    },
        pos = {}
        p = 0

        dic = self.ephemeris_data()

        for eph in range(len(dic)):
            tow = self.klobuchar_data()[eph]['utctow']
            keys = []
            for key in self.ephemeris_data()[0]:
                keys.append(key)
            for seq in range(len(keys)):
                sequence = keys[seq]
                mu = 3.986005*(10**14)  # WGS84 value for the earth's universal gravitational parameter for GPS user in meters^3/sec^2
                omegaedot = 7.2921151467*(10**-5)  # WGS84 value of the earth's rotation rate in rad/sec
                A = (dic[eph][sequence]['sqrta'])**2  # Semi-major axis in meters
                n0 = math.sqrt(mu/(A**3))  # Computed mean motion in rad/sec
                if (tow - dic[eph][sequence]['toe']) > 302400:
                    tk = tow - dic[eph][sequence]['toe'] - 604800  # Time from ephemeris reference epoch in sec
                elif (tow - dic[eph][sequence]['toe']) < - 302400:
                    tk = tow - dic[eph][sequence]['toe'] + 604800
                else:
                    tk = tow - dic[eph][sequence]['toe']

                n = n0 + (dic[eph][sequence]['deltan'])  # Corrected mean motion in rad/sec
                Mk = dic[eph][sequence]['m0'] + n * tk  # Mean anomaly
                Ek = 0 # eccentric anomaly
                # solve equation Mk by iteration
                e = dic[eph][sequence]['e']

                while Ek != Mk:
                    Ek = Mk
                    Mk = Ek + e * math.sin(Ek)  # Kepler's Equation for Eccentric Anomaly in radians
                vk = math.atan((math.sqrt(1 - e**2) * math.sin(Ek))/((math.cos(Ek) - e)))  # true anomaly
                Ek = math.acos((e + math.cos(vk))/(1 + e * math.cos(vk)))
                phik = vk + dic[eph][sequence]['omega']  # argument of latitude
                deltauk = dic[eph][sequence]['cus']*math.sin(2*phik) + dic[eph][sequence]['cuc']*math.cos(2*phik)  # argument of latitude correction
                deltark = dic[eph][sequence]['crs']*math.sin(2*phik) + dic[eph][sequence]['crc']*math.cos(2*phik)  # radius correction
                deltaik = dic[eph][sequence]['cis']*math.sin(2*phik) + dic[eph][sequence]['cic']*math.cos(2*phik)  # inclination correction
                uk = deltauk + phik  # corrected argument of latitude
                rk = A * (1 - e * math.cos(Ek)) + deltark  # corrected radius
                ik = dic[eph][sequence]['i0'] + deltaik + dic[eph][sequence]['idot'] * tk  # corrected inclination
                xkp = rk * math.cos(uk)  # Positions in orbital plane
                ykp = rk * math.sin(uk)
                omegak = dic[eph][sequence]['omega0'] + (dic[eph][sequence]['omegadot'] - omegaedot) * tk - omegaedot * dic[eph][sequence]['toe']  # corrected longitude of ascending node
                xk = xkp * math.cos(omegak) - ykp * math.cos(ik) * math.sin(omegak)
                yk = xkp * math.sin(omegak) - ykp * math.cos(ik) * math.cos(omegak)
                zk = ykp * math.sin(ik)
                #print(math.sqrt(xk**2+yk**2+zk**2))
                #print(math.sqrt(xkp**2+ykp**2))
                #print(rk)
                pos[p] = {'svid': dic[eph][sequence]['svid'], 'Ek': Ek, 'x': xk, 'y': yk, 'z': zk}
                p += 1
        return pos

    def store_data(self, file):
        # Store into a file data comming from the receiver and make data processing if data are UBX message
        # Input:
        # file: open file where data will be written
        info = self.device.readline()
        if info[0:2] != b'$P' and info[0:2] != b'$G':
            file.write(binascii.hexlify(info))
        else:
            file.write(info)
