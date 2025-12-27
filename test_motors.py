import time
from adafruit_motorkit import MotorKit

kit = MotorKit()

print("Testing M1 (Front Left) - Forward")
kit.motor1.throttle = 0.5
time.sleep(1)
kit.motor1.throttle = 0

print("Testing M2 (Front Right) - Forward")
kit.motor2.throttle = 0.5
time.sleep(1)
kit.motor2.throttle = 0

print("Testing M3 (Back Left) - Forward")
kit.motor3.throttle = 0.5
time.sleep(1)
kit.motor3.throttle = 0

print("Testing M4 (Back Right) - Forward")
kit.motor4.throttle = 0.5
time.sleep(1)
kit.motor4.throttle = 0
