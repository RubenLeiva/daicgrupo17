import time
from grove.gpio import GPIO


motor =    GPIO(24, GPIO.OUT)

def encenderM():
    print("Motor encendido")
    motor.write(1)
    
def apagarM():
    print("Motor apagado")
    motor.write(0)
    