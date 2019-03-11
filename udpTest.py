from CZNBIoT.NB_IoT import NBIoT
import time 

server_ip = "195.34.89.241"
server_port = 7

node = NBIoT()

#print("reset start")
#node.resetModem()
#print("reset end")

print("AT: " + node.sendATCmd("AT", "OK\r\n"))
print("IMEI: " + node.getIMEI()) 
print("FW Ver: " + node.getFirmwareInfo())
print("HW model: " + node.getHardwareInfo())

if node.isAttachNetwork():
    print("Network connect")
else:
    print("Network disconnect")
    node.attachNetwork()

node.closeUDPSocket(0)
socket = node.openUDPSockect()

node.setPortNum(server_port)
node.setIPAddress(server_ip)
node.sendUDPData(socket, "Hi There")
print(node.recevieUDPData(socket))

node.closeUDPSocket(socket)
