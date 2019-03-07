import smbus
import time

HTS221_ADDR = 0x5F
HTS221_WHO_AM_I = 0x0F
HTS221_ID = 0xBC
HTS221_AV_CONF = 0x10
HTS221_CTRL_REG1 = 0x20
# Humidity
HTS221_H0_rH_x2 = 0x30
HTS221_H1_rH_x2 = 0x31
HTS221_H0_T0_OUT_L = 0x36
HTS221_H0_T0_OUT_H = 0x37
HTS221_H1_T0_OUT_L = 0x3A 
HTS221_H1_T0_OUT_H = 0x3B
HTS221_H_OUT_L = 0x28
HTS221_H_OUT_H = 0x29
# Temperature
HTS221_T0_DEGC_X8 = 0x32
HTS221_T1_DEGC_X8 = 0x33
HTS221_T0_T1_MSB = 0x35
HTS221_T0_OUT_L = 0x3C
HTS221_T0_OUT_H = 0x3D
HTS221_T1_OUT_L = 0x3E
HTS221_T1_OUT_H = 0x3F
HTS221_T_OUT_L = 0x2A
HTS221_T_OUT_H = 0x2B


class HTS221:
    def __init__(self):
        self.bus = smbus.SMBus(1)
        # Temperature average samples = 16(MAX 256), Humidity average samples = 32(MAX 512)
        self.bus.write_byte_data(HTS221_ADDR, HTS221_AV_CONF, 0x1B)
        # Power ON, Continuous update, Data ouput rate = 1Hz
        self.bus.write_byte_data(HTS221_ADDR, HTS221_CTRL_REG1, 0x81)
        time.sleep(0.5)

    def getDeviceID(self):
        return self.bus.read_byte_data(HTS221_ADDR, HTS221_WHO_AM_I)
    
    def getHumidity(self):
        val = self.bus.read_byte_data(HTS221_ADDR, HTS221_H0_rH_x2)
        H0 = val / 2
        val = self.bus.read_byte_data(HTS221_ADDR, HTS221_H1_rH_x2)
        H1 = val /2
        
        val0 = self.bus.read_byte_data(HTS221_ADDR, HTS221_H0_T0_OUT_L)
        val1 = self.bus.read_byte_data(HTS221_ADDR, HTS221_H0_T0_OUT_H)
        H2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)
        
        val0 = self.bus.read_byte_data(HTS221_ADDR, HTS221_H1_T0_OUT_L)
        val1 = self.bus.read_byte_data(HTS221_ADDR, HTS221_H1_T0_OUT_H)
        H3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)
        
        Hl = self.bus.read_byte_data(HTS221_ADDR, HTS221_H_OUT_L)
        Hh = self.bus.read_byte_data(HTS221_ADDR, HTS221_H_OUT_H)
        humidity = (Hh * 256) + Hl
        
        humidity = ((1.0 * H1) - (1.0 * H0)) * (1.0 * humidity - 1.0 * H2) / (1.0 * H3 - 1.0 * H2) + (1.0 * H0)
        
        return humidity
    
    def getCTemperature(self):
        T0 =  self.bus.read_byte_data(HTS221_ADDR, HTS221_T0_DEGC_X8)
        T0 = (T0 & 0xFF)
        T1 =  self.bus.read_byte_data(HTS221_ADDR, HTS221_T1_DEGC_X8)
        T1 = (T1 & 0xFF)
        raw =  self.bus.read_byte_data(HTS221_ADDR, HTS221_T0_T1_MSB)
        raw = (T1 & 0xFF)
        T0 = ((raw & 0x03) * 256) + T0
        T1 = ((raw & 0x0C) * 64) + T1
        
        val0 = self.bus.read_byte_data(HTS221_ADDR, HTS221_T0_OUT_L)
        val1 = self.bus.read_byte_data(HTS221_ADDR, HTS221_T0_OUT_H)
        T2 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)
        
        val0 = self.bus.read_byte_data(HTS221_ADDR, HTS221_T1_OUT_L)
        val1 = self.bus.read_byte_data(HTS221_ADDR, HTS221_T1_OUT_H)
        T3 = ((val1 & 0xFF) * 256) + (val0 & 0xFF)
        
        Tl = self.bus.read_byte_data(HTS221_ADDR, HTS221_T_OUT_L)
        Th = self.bus.read_byte_data(HTS221_ADDR, HTS221_T_OUT_H)
        temperature = (Th * 256) + Tl
        if temperature > 32767:
            temperature -= 65536
        
        cTemp = ((T1 - T0) / 8.0) * (temperature - T2) / (T3 - T2) + (T0 / 8.0)
        return cTemp
    
    def getFTemperature(self):
        return (self.getCTemperature() * 1.8) + 32
