from LSM6DS3 import LSM6DS3
import time

Axes_Sensor = LSM6DS3()
print("LSM6DS3 Device ID: ", hex(Axes_Sensor.getDeviceID()))

while True:
    accel_data = Axes_Sensor.getXAxes()
    print('Accel X: %.2f' %accel_data[0])
    print('Accel Y: %.2f' %accel_data[1])
    print('Accel Z: %.2f' %accel_data[2])

    print('=====================================')

    gyro_data = Axes_Sensor.getGAxes()
    print('gyro X: %.2f' %gyro_data[0])
    print('gyro Y: %.2f' %gyro_data[1])
    print('gyro Z: %.2f' %gyro_data[2])

    print('=====================================')

    time.sleep(0.3)