# daicgrupo17
<!-- TABLE OF CONTENTS -->
## Tabla de Contenidos

* [Sobre el proyecto](#sobre-el-proyecto)
* [Documentación](#documentación)
* [Contribuidores](#contribuidores)

<!-- ABOUT THE PROJECT -->
## Sobre el proyecto

Safe Seats es un sistema IoT para evitar aglomeraciones en bares y restaurantes y mantener constantemente la distancia de seguridad entre las sillas. Para esto las sillas llevan incorporado un dispositivo el cual cuando detecta una silla a un metro o menos distancia se apaga la luz incorporada en el dispositivo. En caso de no haber hecho caso a la luz y lleves más de 10 segundos a menos de un metro de distancia, el motor de vibración incorporado se activará por lo que la silla comenzará a vibrar para que el comensal se dé cuenta de que está inflingiendo las medidas de seguridad.


<!-- GETTING STARTED -->
## Documentación

### Base de datos
Para la base de Datos hemos utilizado Corlysis, necesitas añadir los argumentos db y token las declararemos en la cmd cuando ejecutemos el programa. Nuestra db es Safe Seats y el token es la secuencia de números y letras que te da Corlysis. Creamos una línea que va a ser nuestro Query que medimos la distancia que recoge el ultrasonido.

```parser = argparse.ArgumentParser()
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
        
```
### IoT

En cuanto al hardware, hemos utilizado una Raspberry Pi 3 junto con una Grove Base Hat que nos permite añadir varios componentes como dos LED que hemos utilizado para advertir al consumidor si está manteniendo la distancia de seguridad o no, dos ultrasonidos para medir contantemente la distancia y un motor de vibración y un buzzer para volver a avisar en caso de que no hayan hecho caso a la primera advertencia.

Para hacer uso de los componentes así como desarrollar sus funcionalidades, hemos creado la clase grove_ultrasonic_ranger.py en lenguaje python donde hemos desarrollado todo el código para poder hacer uso del hardware. 

Hemos importado el Led y el motor de vibración para esta Raspberry Pi.

```python
import motor
import led
```
Hemos asignado el LED al puerto 22 que es donde lo conectaremos en el HAT. Con el método Write() haremosque la luz se encienda o se apague.
Hemos hecho lo mismo para el motor.
```python
led =    GPIO(22, GPIO.OUT)

def encenderL():
    print("LED encendido")
    led.write(0)
    
    
def apagarL():
    print("LED apagado")
    led.write(1)
```    

El programa principal se basa en estar midiendo constantemente la distancia. El sensor calcula el tiempo que tarda las ondas en ir, rebotar con el objeto y volver el sensor calcula la distancia en base al tiempo que han tardado estas ondas en hacer el recorrido. Si tarda mucho tiempo el sensor omitirán los datos.

```  
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
```  

<!-- CONTRIBUTORS -->
## Contribuidores

* **Erik Saenz de Ugarte**	-	*erik.saenzdeugarte@opendeusto.es*
* **Ruben Leiva**	-	*ruben.leiva@opendeusto.es*	
