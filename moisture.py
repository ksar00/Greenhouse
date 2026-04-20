
import smbus
import time

class MCP3021:
    bus = smbus.SMBus(1)

    def __init__(self, address = 0x4b):
        self.address = address

def read_raw(self):
    try:
        data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
        return (data[0] << 8) | data[1]
    except Exception as e:
        print("Read failed:", e)
        return None
    
def read_raw(self):
    data = self.bus.read_i2c_block_data(self.address, 0x00, 2)
    return ((data[0] << 8) | data[1]) >> 2

adc = MCP3021()

while True:
    raw = adc.read()
    prct = adc.read_prct()
    print("Raw :", raw)
    print("wet: ", prct)
    time.sleep(1)
