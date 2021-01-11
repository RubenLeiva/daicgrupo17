#!/usr/bin/env python
#
# This is the code for Grove - Ultrasonic Ranger
# (https://www.seeedstudio.com/Grove-Ultrasonic-Ranger-p-960.html)
# which is a non-contact distance measurement module which works with 40KHz sound wave. 
#
# This is the library for Grove Base Hat which used to connect grove sensors for raspberry pi.
#

'''
## License

The MIT License (MIT)

Grove Base Hat for the Raspberry Pi, used to connect grove sensors.
Copyright (C) 2018  Seeed Technology Co.,Ltd. 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
'''
import sys
import time
import motor
import led
import requests
import argparse
from grove.gpio import GPIO

URL = 'https://corlysis.com:8086/write'
READING_DATA_PERIOD_MS = 2000.0
SENDING_PERIOD = 2
MAX_LINES_HISTORY = 1000

usleep = lambda x: time.sleep(x / 1000000.0)

_TIMEOUT1 = 1000
_TIMEOUT2 = 10000

class GroveUltrasonicRanger(object):
    def __init__(self, pin):
        self.dio = GPIO(pin)

    def _get_distance(self):
        self.dio.dir(GPIO.OUT)
        self.dio.write(0)
        usleep(2)
        self.dio.write(1)
        usleep(10)
        self.dio.write(0)

        self.dio.dir(GPIO.IN)

        t0 = time.time()
        count = 0
        while count < _TIMEOUT1:
            if self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT1:
            return None

        t1 = time.time()
        count = 0
        while count < _TIMEOUT2:
            if not self.dio.read():
                break
            count += 1
        if count >= _TIMEOUT2:
            return None

        t2 = time.time()

        dt = int((t1 - t0) * 1000000)
        if dt > 530:
            return None

        distance = ((t2 - t1) * 1000000 / 29 / 2)    # cm

        return distance

    def get_distance(self):
        while True:
            dist = self._get_distance()
            if dist:
                return dist


Grove = GroveUltrasonicRanger


def main():
    from grove.helper import SlotHelper
    sh = SlotHelper(SlotHelper.GPIO)
    pin = 5
    contador = 0
    sonar = GroveUltrasonicRanger(pin)
    parser = argparse.ArgumentParser()
    parser.add_argument("db", help="database name")
    parser.add_argument("token", help="secret token")
    args = parser.parse_args()
    
    corlysis_params = {"db": args.db, "u": "token", "p": args.token, "precision": "ms"}
    
    payload = ""
    counter = 1
    problem_counter = 0        


    print('Detecting distance...')
    while True:
        unix_time_ms = int(time.time()*1000)
        line = "Distance,dist=" + str(sonar.get_distance())+ " hora="  + str(unix_time_ms) + "\n"
        print(line)
        payload += line
        
        if counter % SENDING_PERIOD == 0 or counter % SENDING_PERIOD != 0:
            try:
                r = requests.post(URL, params=corlysis_params, data = payload)
                if r.status_code == 204:
                    print("writing")
                else:
                    #print(r.content)
                    raise Exception("data not written")
                payload = ""
            except Eception as e:
                #print(e)
                problem_counter += 1
                #print(sys.exc_info()[0])
                print('cannot write')
                if problem_counter == MAX_LINES_HISTORY:
                    problem_counter = 0
                    payload = ""
        counter += 1
        time_diff_ms = int(time.time()*1000) - unix_time_ms           
        print(time_diff_ms)
        if time_diff_ms < READING_DATA_PERIOD_MS:
           time.sleep((READING_DATA_PERIOD_MS - time_diff_ms)/1000.0)
        
        print('{} cm'.format(sonar.get_distance()))
        time.sleep(1)
        if sonar.get_distance() > 100:
            contador = 0
            led.encenderL()
            motor.apagarM()
            time.sleep(1)
        else:
            contador += 1
            print (contador)
            led.apagarL()
            time.sleep(1)
            if contador > 3:
                motor.encenderM()
            

if __name__ == '__main__':
    main()

