import smbus
import time
import pigpio

pi = pigpio.pi()
pi.write(13, 0)

bus = smbus.SMBus(1)# RPi revision 2 (0 for revision 1)​
i2c_address = 0x4B  # default address​

dry = 767
wet = 297

def soil_raw_adc():
# Reads word (2 bytes) as int - 0 is comm byte​
    rd = bus.read_word_data(i2c_address, 0)
    # Exchanges high and low bytes​
    data = ((rd & 0xFF) << 8) | ((rd & 0xFF00) >> 8)
    # Ignores two least significiant bits​
    data = data >> 2
    return data

def soil_percent():
    data = soil_raw_adc()
    if data < wet:
        data = 100

else:
    # tør måling - ADC måling * 100.0 / tør måling - våd måling. ​
    percentage = (dry - data) * 100.0 / (dry - wet) 
    data = round(percentage, 2)
    if percentage < 0:
        data = 0

return data

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