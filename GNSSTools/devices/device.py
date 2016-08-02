# Tampere University of Technology
#
# DESCRIPTION
#
#
# AUTHOR
# Anne-Marie Tobie

import GNSSTools.tools as tools


class Device:

    def __init__(self, datafile='datatxt/spectracom_data.nmea'):
        self.datafile = datafile

    def open(self):
        pass

    def close(self):
        pass

    def nmea_gga_store(self):
        # Read file and take only the information GGA (global positioning system fix data) data
        # Return:
        # gga: list of GGA data parsing this way:
        #      gga = [[time in HHMMSS.DD, LAT in DD, LONG in DD, ALT in m][...]]
        read = open(self.datafile, 'r')
        gga = []
        a = 1
        b = 1
        for line in read.readlines():
            if line[3:6] == 'GGA':
                split = line.split(',')
                if split[2] != '' or split[4] != '':
                    if split[3] == 'S':
                        a = -1
                    if split[5] == 'W':
                        b = -1
                    gga.append([split[1], a*tools.dm_to_dd(float(split[2])/100),
                                b*tools.dm_to_dd(float(split[4])/100), split[9]])
        read.close()
        return gga

    def nmea_rmc_store(self):
        # Read data collected and store into matrix RMC data
        # Return:
        # rmc: [[time, lat, NS, long, EW, speed_over_ground, course_over_ground][...]]
        # where:
        file = open(self.datafile, 'r')
        rmc = []
        for line in file:
            if line[3:6] == 'GBS':
                data = line.split(',')
                time = data[1]
                lat = data[2]
                ns = data[3]
                long = data[4]
                ew = data[5]
                speed_over_ground = data[6]
                course_over_ground = data[7]
                rmc.append([time, lat, ns, long, ew, speed_over_ground, course_over_ground])
        file.close()
        return rmc

    def nmea_gsv_store(self):
        file = open('datatxt/ublox_processed_data.txt', 'r')
        rmc = []

        def collect(nsat):
            for i in range(nsat):
                sv = data[4 + 4*i]
                elev = data[5 + 4*i]
                az = data[6 + 4*i]
                cno = data[7 + 4*i]
                satif = [sv, elev, az, cno]
                first.append(satif)
            return first

        for line in file:
            if line[3:6] == 'GSV' and len(line)>17:
                data = line.split(',')
                if (int(data[1]) > 1) and (data[1] != data[2]):
                    nsat = 4
                else:
                    nsat = int(data[3])%4
                if data[2] == '1':
                    first = []
                    collect(nsat)
                    if data[2] == data[1]:
                        rmc.append(first)
                elif data[2] != data[1]:
                    collect(nsat)
                else:
                    collect(nsat)
                    rmc.append(first)
        return rmc
