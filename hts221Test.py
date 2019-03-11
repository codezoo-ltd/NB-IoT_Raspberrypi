from CZNBIoT.HTS221 import HTS221

TH_Sensor = HTS221()

print('HTS221 Device ID : ', hex(TH_Sensor.getDeviceID()))
print('Humidity: %.2f %%' %TH_Sensor.getHumidity())
print('Temperature in Celsius: %.2f C' %TH_Sensor.getCTemperature())
print('Temperature in fahrenheit: %.2f F' %TH_Sensor.getFTemperature())
