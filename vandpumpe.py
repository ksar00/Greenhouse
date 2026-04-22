import smbus
import time
import pigpio

pi = pigpio.pi()
pi.write(13, 0)

bus = smbus.SMBus(1)# RPi revision 2 (0 for revision 1)​
i2c_address = 0x4B  # default address​

pump_running = False
while True:
    soil_p = soil_percent()
    print("Data: ", soil_p)
    if soil_p < 10 and pump_running == False:
        pi.write(13, 1)
        pump_running = True
    if soil_p > 60 and pump_running == True:
        pi.write(13, 0)
        pump_running = False
time.sleep(1)