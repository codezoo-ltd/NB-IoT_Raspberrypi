import smbus

LSM6DS3_ADDR = 0x6A
LSM6DS3_WHO_AM_I = 0x0F
LSM6DS3_CTRL1_XL = 0x10
# Accelerometer 
LSM6DS3_OUT_X_L_XL = 0x28
LSM6DS3_OUT_X_H_XL = 0x29
LSM6DS3_OUT_Y_L_XL = 0x2A
LSM6DS3_OUT_Y_H_XL = 0x2B
LSM6DS3_OUT_Z_L_XL = 0x2C
LSM6DS3_OUT_Z_H_XL = 0x2D
# Gyroscope
LSM6DS3_OUT_X_L_G = 0x22
LSM6DS3_OUT_X_H_G = 0x23
LSM6DS3_OUT_Y_L_G = 0x24
LSM6DS3_OUT_Y_H_G = 0x25
LSM6DS3_OUT_Z_L_G = 0x26
LSM6DS3_OUT_Z_H_G = 0x27


class LSM6DS3:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        # Accelerometer init (104Hz, 2G)
        self.bus.write_byte_data(LSM6DS3_ADDR, LSM6DS3_CTRL1_XL, 0x40)

    def __int_to_signed_short(self, value):
        return -(value & 0x8000) | (value & 0x7fff)

    def __calcGyro(self, rawInput):
        gyroRangeDivisor = 245 / 125 #500 is the gyro range (DPS)
        output = rawInput * 4.375 * (gyroRangeDivisor) / 1000
        return output
    
    def __calcAccel(self, rawInput):
        senfityvity2G = 0.061
        return (rawInput*senfityvity2G)/1000

    def getDeviceID(self):
        return self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_WHO_AM_I)

    def getXAxes(self):
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_X_L_XL)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_X_H_XL)
        xAxes = self.__int_to_signed_short( (datah<<8) + datal )
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Y_L_XL)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Y_H_XL)
        yAxes = self.__int_to_signed_short( (datah<<8) + datal )
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Z_L_XL)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Z_H_XL)
        zAxes = self.__int_to_signed_short( (datah<<8) + datal )

        return (self.__calcAccel(xAxes), self.__calcAccel(yAxes), self.__calcAccel(zAxes))

    def getGAxes(self):
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_X_L_G)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_X_H_G)
        xAxes = self.__int_to_signed_short( (datah<<8) + datal )
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Y_L_G)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Y_H_G)
        yAxes = self.__int_to_signed_short( (datah<<8) + datal )
        datal = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Z_L_G)
        datah = self.bus.read_byte_data(LSM6DS3_ADDR, LSM6DS3_OUT_Z_H_G)
        zAxes = self.__int_to_signed_short( (datah<<8) + datal )

        return (self.__calcGyro(xAxes), self.__calcGyro(yAxes), self.__calcGyro(zAxes) )