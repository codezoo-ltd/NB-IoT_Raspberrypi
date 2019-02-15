import time
import serial
import re
import RPi.GPIO as GPIO

#ser = serial.Serial()

ATCmdList = {
    'IMEI': {'CMD': "AT+CGSN=1", 'REV': "\r\nOK\r\n"},
    'FWInfo': {'CMD': "AT+CGMR", 'REV': "\r\nOK\r\n"},
    'HWInfo': {'CMD': "AT+CGMM", 'REV': "\r\nOK\r\n"},
    'AttachNet' : {'CMD': "AT+CGATT=1", 'REV': "OK\r\n"},
    'DetachNet' : {'CMD': "AT+CGATT=0", 'REV': "OK\r\n"},
    'IsAttachNet' : {'CMD': "AT+CGATT?", 'REV': "+CGATT:1\r\n"},
    'OpenUDP' : {'CMD': "AT+NSOCR=DGRAM,17,", 'REV': "OK\r\n"},
    'CloseUDP' : {'CMD': "AT+NSOCL=", 'REV': "\r\n"},   # OK, ERROR ??
    'SendUDP' : {'CMD': "AT+NSOST=", 'REV': "\r\n"},
    'RecevieUDP' : {'CMD': "AT+NSORF=", 'REV': "OK\r\n"},
}

class NBIoT:
    ser = None
    isConectSerial = False
    __TimeOut = 3     # seconds

    def __init__(self, serialPort='/dev/ttyS0', baudrate=9600, resetPinNum=4):
        # serial port setup
        if(NBIoT.isConectSerial == False):
            NBIoT.ser = serial.Serial()
            NBIoT.ser.port = serialPort
            NBIoT.ser.baudrate = baudrate
            NBIoT.ser.parity = serial.PARITY_NONE
            NBIoT.ser.stopbits = serial.STOPBITS_ONE
            NBIoT.ser.bytesize = serial.EIGHTBITS
            NBIoT.isConectSerial = True

        # Modem reset Pin Number
        self.resetPinNum = resetPinNum

        self.compose = ""
        self.response = ""
        self.timeout = NBIoT.__TimeOut

        self.ipAddress = ""
        self.portNum = ""

    def getResetPinNum(self):
        ''' get modem reset pin number '''
        return self.resetPinNum

    def setIPAddress(self, ip):
        ''' set ip address'''
        self.ipAddress = ip
    
    def setPortNum(self, port):
        ''' set port number '''
        self.portNum = str(port)

    def __getMillSec(self):
        ''' get miliseconds '''
        return int(time.time())
    
    def __delay(self, ms):
        ''' delay as millseconds '''
        time.sleep(float(ms/1000.0))

    def __readATResponse(self, cmd_response):
        ''' getting respnse of AT command from modem '''
        while True:
            self.response = ""
            while(NBIoT.ser.inWaiting()):
                try:
                    self.response += NBIoT.ser.read(NBIoT.ser.inWaiting()).decode('utf-8', errors='ignore')
                    self.__delay(50)
                except Exception as e:
                    print(e)
                    return False
            if(self.response.find(cmd_response) != -1):
                #print("read response: " + self.response)
                return True

    def __sendATCmd(self, command):
        ''' Sending at AT command to module '''
        self.compose = ""
        self.compose = str(command) + "\r"
        NBIoT.ser.reset_input_buffer()
        NBIoT.ser.write(self.compose.encode())
        #print(self.compose)
    
    def sendATCmd(self, command, cmd_response, timeout = None):
        ''' Send AT command & Read command response ''' 
        if(NBIoT.ser.isOpen() == False):
            NBIoT.ser.open()

        if timeout is None:
            timeout = self.timeout
        
        self.__sendATCmd(command)

        timer = self.__getMillSec()

        while True: 
            if((self.__getMillSec() - timer) > timeout):
                # error rasie
                print(command + " / Send failed ")
                return "Error"
            
            if(self.__readATResponse(cmd_response)):
                return self.response
            
    # AT command methods
    def getIMEI(self):
        ''' get IMEI number'''
        rev = self.sendATCmd(ATCmdList['IMEI']['CMD'], ATCmdList['IMEI']['REV'])
        data = rev.split(':')
        return data[1][:data[1].index(ATCmdList['IMEI']['REV'])]

    def getFirmwareInfo(self):
        ''' get FW version '''
        data =  self.sendATCmd(ATCmdList['FWInfo']['CMD'], ATCmdList['FWInfo']['REV'])
        return data[:data.index(ATCmdList['FWInfo']['REV'])]

    def getHardwareInfo(self):
        ''' get modem model info '''
        data = self.sendATCmd(ATCmdList['HWInfo']['CMD'], ATCmdList['HWInfo']['REV'])
        return data[:data.index(ATCmdList['HWInfo']['REV'])]
    
    def attachNetwork(self, connect=True):
        ''' connect/disconnect base station fo operator '''
        if(connect):
            return self.sendATCmd(ATCmdList['AttachNet']['CMD'], ATCmdList['AttachNet']['REV'], 8)
        else:
            return self.sendATCmd(ATCmdList['DetachNet']['CMD'], ATCmdList['DetachNet']['REV'], 8)
    
    def isAttachNetwork(self):
        ''' true : NB-IoT Network attached, false : NB-IoT Network detached ''' 
        return (self.sendATCmd(ATCmdList['IsAttachNet']['CMD'], ATCmdList['IsAttachNet']['REV']) != "Error")

    # UDP methods 
    def openUDPSockect(self, port=10):
        ''' port = 0~65535 (reserve 5683) '''
        command = ATCmdList['OpenUDP']['CMD'] + str(port) + ',1'
        mySocket = self.sendATCmd(command, ATCmdList['OpenUDP']['REV'])

        if(mySocket != "Error"):
            return int(mySocket[0])
        else:
            return -1
    
    def closeUDPSocket(self, mySocket):
        command = ATCmdList['CloseUDP']['CMD'] + str(mySocket)
        self.sendATCmd(command, ATCmdList['CloseUDP']['REV'])
        
    # data type????
    def sendUDPData(self, mySocket, data, ip_address=None, ip_port=None):
        ''' send UDP data 
            max data size: 256bytes -> recomand 250bytes 
            send data is Nibble type (ex, "A" -> 0x41)'''
        command = ATCmdList['SendUDP']['CMD'] + str(mySocket) + ","
        if ip_address is None:
            command += self.ipAddress
        else:
            command += str(ip_address)
        command += ","
        if ip_port is None:
            command += self.portNum
        else:
            command += str(ip_port)
        command += ","
        command += str(len(data)) + "," + data.encode().hex()

        self.sendATCmd(command, ATCmdList['SendUDP']['REV'])

    def recevieUDPData(self, mySocket, rev_length=256, rev_timeOut=3):
        ''' recevie buffer size : 512 bytes 
        return : ['ip','port','data length', 'data', 'renainnig length']'''
        duration = 500
        count = ((rev_timeOut*1000)/duration)
        datareceve = False
        data_length = ""

        for i in range(0,int(count)):
            if(self.__readATResponse("+NSONMI")):
                datareceve = True
                data = self.response.split(',')
                data_length = data[len(data)-1]
                break
            else:
                print("wait index {}".format(i))
                self.__delay(duration)

        if(datareceve):
            if int(data_length) > rev_length :
                data_length = str(rev_length)
            command = ATCmdList['RecevieUDP']['CMD'] + str(mySocket) + "," + data_length
            if (self.sendATCmd(command, ATCmdList['RecevieUDP']['REV']) != "Error"):
               data = self.response.split(',')
               data[4] = bytes.fromhex(data[4]).decode('utf-8')
               data[5] = re.search(r'\d+', data[5]).group()
               return data[1:]

        print("Data read fail")
        return ['-1','-1','-1','-1','-1']