import time
from grove.gpio import GPIO

led =    GPIO(22, GPIO.OUT)

def encenderL():
    print("LED encendido")
    led.write(0)
    
    
def apagarL():
    print("LED apagado")
    led.write(1)
    
    
