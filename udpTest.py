from NB_IoT import NBIoT
import time 

server_ip = "195.34.89.241"
server_port = 7

node = NBIoT()

print("AT: " + node.sendATCmd("AT", "OK\r\n"))
print("IMEI: " + node.getIMEI()) 
print("FW Ver: " + node.getFirmwareInfo())
print("HW model: " + node.getHardwareInfo())

if node.isAttachNetwork():
    print("Network connect")
else:
    print("Network disconnect")
    node.attachNetwork()

node.setIPAddress(server_ip)
node.setPortNum(server_port)

node.closeUDPSocket(0)
socket = node.openUDPSockect()

echo_data = "Hi There"
node.sendUDPData(socket, echo_data)
data = node.recevieUDPData(socket)
print(data)