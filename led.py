import pigpio
import time

pi = pigpio.pi()

PWM_RED = 12
PWM_BLUE = 13
FREQ = 1000

pi.set_PWM_frequency(PWM_RED, FREQ)
pi.set_PWM_frequency(PWM_BLUE, FREQ)

#Test - tænd begge på 50%
pi.set_PWM_dutycycle(PWM_RED, 128)   # 50% af 255
pi.set_PWM_dutycycle(PWM_BLUE, 128)  # 50% af 255

print("Lys tændt på 50%")
time.sleep(5)

# Sluk
pi.set_PWM_dutycycle(PWM_RED, 0)
pi.set_PWM_dutycycle(PWM_BLUE, 0)
print("Lys slukket")