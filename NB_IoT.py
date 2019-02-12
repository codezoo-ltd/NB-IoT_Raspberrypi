import time
import serial
import RPi.GPIO as GPIO

#ser = serial.Serial()

ATCmdList = {
    'IMEI': {'CMD': "AT+CGSN=1", 'REV': "OK\r\n"},
    'FWInfo': {'CMD': "AT+CGMR", 'REV': "OK\r\n"},
    'HWInfo': {'CMD': "AT+CGMM", 'REV': "OK\r\n"},
    'AttachNet' : {'CMD': "AT+CGATT=1", 'REV': "OK\r\n"},
    'DetachNet' : {'CMD': "AT+CGATT=0", 'REV': "OK\r\n"},
    'IsAttachNet' : {'CMD': "AT+CGATT?", 'REV': "+CGATT:1\r\n"},
    'OpenUDP' : {'CMD': "AT+NSOCR=DGRAM,17,", 'REV': "OK\r\n"},
    'CloseUDP' : {'CMD': "AT+NSOCL=", 'REV': "\r\n"},   # OK, ERROR ??
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
                print("read response: " + self.response)
                return True

    def __sendATCmd(self, command):
        ''' Sending at AT command to module '''
        self.compose = ""
        self.compose = str(command) + "\r"
        NBIoT.ser.reset_input_buffer()
        NBIoT.ser.write(self.compose.encode())
        print(self.compose)
    
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
        return self.sendATCmd(ATCmdList['IMEI']['CMD'], ATCmdList['IMEI']['REV'])

    def getFirmwareInfo(self):
        ''' get FW version '''
        return self.sendATCmd(ATCmdList['FWInfo']['CMD'], ATCmdList['FWInfo']['REV'])

    def getHardwareInfo(self):
        ''' get modem model info '''
        return self.sendATCmd(ATCmdList['HWInfo']['CMD'], ATCmdList['HWInfo']['REV'])
    
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
    def openUDPSockect(self):
        command = ATCmdList['OpenUDP']['CMD'] + self.portNum + ',1'
        mySocket = self.sendATCmd(command, ATCmdList['OpenUDP']['REV'])

        if(mySocket != "Error"):
            return int(mySocket[0])
        else:
            return -1
    
    def closeUDPSocket(self, mySocket):
        command = ATCmdList['CloseUDP']['CMD'] + str(mySocket)
        self.sendATCmd(command, ATCmdList['CloseUDP']['REV'])
        
