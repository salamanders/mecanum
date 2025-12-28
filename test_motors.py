import time
from motor_driver import MotorDriver

# Initialize the driver (will mock if no hardware)
driver = MotorDriver()

print("Testing M1 (Front Left) - Forward")
# Drive M1 full speed, others 0
driver.drive(0.7, 0, 0, 0)
time.sleep(2)
# Stop
driver.drive(0, 0, 0, 0)

print("Testing M2 (Front Right) - Forward")
driver.drive(0, 0.7, 0, 0)
time.sleep(2)
driver.drive(0, 0, 0, 0)

print("Testing M3 (Back Left) - Forward")
driver.drive(0, 0, 0.7, 0)
time.sleep(2)
driver.drive(0, 0, 0, 0)

print("Testing M4 (Back Right) - Forward")
driver.drive(0, 0, 0, 0.7)
time.sleep(2)
driver.drive(0, 0, 0, 0)
