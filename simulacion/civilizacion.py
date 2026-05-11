import csv
import time
import random
import threading
import multiprocessing
from queue import Empty
from threading import Thread

from modulos.salud import Salud
from modulos.economia import Economia
from simulacion.mensajes import Mensaje
from modulos.demografia import Demografia
from modulos.agricultura import Agricultura
from modulos.sociopolitica import Sociopolitica


class Civilizacion(multiprocessing.Process):

    def __init__(self, nombre, config, buzon, directorio, barrera, progress_queue):
        super().__init__()

        self.nombre = nombre
        self.config = config

        # para la pantalla de carga
        self.progress_queue = progress_queue
        
        # infraestructura de comunicacion distribuida
        self.buzon = buzon
        self.directorio = directorio
        self.barrera = barrera
        self.colapso = False
        self.anio = 1
        self.ultima_pandemia = 0

        # lock para proteger el estado compartido
        self.lock = None

        # instanciacion de modulos con parametros iniciales
        self.demografia = Demografia(config["poblacion"])

        self.economia = Economia(
            capital_inicial=config["capital"],
            energia_inicial=config["energia"]
        )

        self.agricultura = Agricultura(
            tierra_inicial=config["tierra"]
        )

        self.salud = Salud()
        self.sociopolitica = Sociopolitica()

        self.buffer = []
        self.archivo = f"datos/{self.nombre.lower()}.csv"
        self._crearCSV()
        self.socios_ciclo = []


    def _crearCSV(self):
        """ crea el fichero de salida con las cabeceras correspondientes """

        headers = [
            "anio",
            "poblacion",
            "pib",
            "tecnologia",
            "energia",
            "comida",
            "tension",
            "infectados",
            "socios"
        ]

        with open(self.archivo, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(headers)


    def _registrar(self):
        """ guarda los datos incluyendo el balance migratorio """

        with self.lock:
            socios_str = (
                "-".join(self.socios_ciclo)
                if self.socios_ciclo
                else "ninguno"
            )
            
            fila = [
                self.anio,
                self.demografia.poblacionTotal,
                round(self.economia.pib, 2),
                round(self.economia.tecnologia, 4),
                int(self.economia.energia),
                int(self.economia.alimentos),
                round(self.sociopolitica.tension, 2),
                self.salud.infectadosTotales,
                socios_str,
            ]
            
            self.buffer.append(fila)
            self.socios_ciclo = []

            if len(self.buffer) >= 50:
                with open(self.archivo, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerows(self.buffer)

                self.buffer.clear()


    def _correo(self):
        """ procesa las ventas y entregas de suministros """

        while True:
            try:
                msg = self.buzon.get()

                # señal de finalizacion del hilo
                if msg is None:
                    break

                with self.lock:
                    if msg.tipo == "comercio":
                        recurso = msg.payload["recurso"]
                        pago_recibido = msg.payload["pago"]
                        cantidad_entregada = msg.payload["cantidad"]
                        
                        # el vendedor recibe el dinero
                        self.economia.pib += pago_recibido

                        self.economia.recibir(
                            recurso,
                            cantidad_entregada
                        )
                        
                    elif msg.tipo == "pandemia":
                        self.salud.importar(
                            msg.payload["cantidad"]
                        )

            except Empty:
                continue


    def _enviarPandemia(self):
        """ propaga la infeccion a un continente aleatorio si se supera el umbral """

        with self.lock:
            if self.salud.infectados < 100:
                return

        destinos = [
            x for x in self.directorio.keys()
            if x != self.nombre
        ]

        if not destinos:
            return
        
        destino = random.choice(destinos)
        msg = Mensaje(
            origen=self.nombre,
            destino=destino,
            tipo="pandemia",
            payload={"cantidad": 10}
        )

        # comprobamos que no haya habido otra pandemia antes para que no haya infinitas
        # de todas formas creo que sirve de poco pq no hay tipo de virus son solo infectados totales
        if self.ultima_pandemia > 0:
            self.directorio[destino].put(msg)
            self.ultima_pandemia = 30
        else:
            self.ultima_pandemia -= 1


    def _comercio(self):
        """ gestiona el comercio priorizando materiales como flujo constante """

        with self.lock:
            pob = self.demografia.poblacionTotal
            precio_contrato = 2000.0
            
            # comercio de materiales 
            # comerciamos materiales siempre que tengamos un minimo de reserva
            puede_exportar_materiales = (self.economia.materiales > 2000)
            
            # recursos secundarios 
            # sobra mucho: mas de 500 raciones por persona
            sobra_comida = (self.economia.alimentos > (pob * 500.0))

            # menos de 20 raciones por persona
            necesita_energia = (self.economia.energia < 10000)

            recurso_a_enviar = None
            cantidad = 0

            # logica de decision jerarquica
            if puede_exportar_materiales:
                recurso_a_enviar = "materiales"
                cantidad = 1500

            elif sobra_comida:
                recurso_a_enviar = "comida"
                cantidad = 5000

            elif necesita_energia and self.economia.pib > precio_contrato:

                # compramos energia
                recurso_a_enviar = "pago_por_energia"
                cantidad = 5000

            if recurso_a_enviar and self.economia.pib > precio_contrato:
                destinos = [
                    x for x in self.directorio.keys()
                    if x != self.nombre
                ]

                if destinos:
                    destino = random.choice(destinos)

                    if destino not in self.socios_ciclo:
                        self.socios_ciclo.append(destino)

                    # el emisor siempre paga el coste de logistica/transaccion
                    self.economia.transaccion(-precio_contrato)
                    msg = Mensaje(
                        origen=self.nombre,
                        destino=destino,
                        tipo="comercio",
                        payload={
                            "recurso": recurso_a_enviar,
                            "cantidad": cantidad,
                            "pago": precio_contrato
                        }
                    )

                    self.directorio[destino].put(msg)


    def _motor(self):
        """ nucleo del motor matematico que coordina todos los modulos """

        with self.lock:
            poblacion = self.demografia.poblacionTotal

            # condicion de parada
            if poblacion <= 0:
                self.colapso = True
                poblacion = 0

            fuerza_laboral = self.demografia.fuerzaLaboral
            
            # reparto estrategico de la fuerza laboral
            agricultores = int(fuerza_laboral * 0.45)
            mineros = int(fuerza_laboral * 0.15)
            energeticos = int(fuerza_laboral * 0.10)

            industria = max(0, fuerza_laboral - agricultores - mineros - energeticos)

            # extraccion de materias primas y energia
            self.economia.extraerEnergia(energeticos)
            self.economia.extraerMinerales(mineros)

            # produccion de comida condicionada por energia y materiales
            comida = self.agricultura.producir(
                trabajadores=agricultores,
                tecnologia=self.economia.tecnologia,
                energia=self.economia.energia,
                fertilizantes=self.economia.materiales
            )

            self.economia.agregarComida(comida)

            # resolucion de salud y aplicacion de bajas demograficas
            self.salud.avanzar(poblacion, self.economia.tecnologia)
            self.demografia.aplicarMuertes(self.salud.muertes)

            # avance temporal de la poblacion y la economia
            self.demografia.avanzar(
                self.economia.alimentos,
                self.sociopolitica.tension,
                self.economia.tecnologia
            )

            self.economia.avanzar(
                trabajadores=industria,
                poblacion=poblacion,
                corrupcion=self.sociopolitica.corrupcion,
                capital_humano=self.demografia.capitalHumano,
                contaminacion=self.agricultura.contaminacion
            )

            # degradacion del entorno y estabilidad social
            self.agricultura.actualizar(poblacion, self.economia.pib)

            hubo_revuelta = self.sociopolitica.avanzar(
                pib=self.economia.pib,
                poblacion=poblacion,
                desigualdad=self.economia.gini,
                racionamiento=self.economia.racionamiento
            )

            if hubo_revuelta:
                #print(f"[{self.nombre}] ({self.anio}) ¡estalla una revolucion!")
                self.sociopolitica.ejecutarRevolucion()

                # calculamos bajas
                bajas_conflicto = int(poblacion * random.uniform(0.1, 0.3))
                self.demografia.aplicarMuertes(bajas_conflicto, "revolucion")
                
        # interacciones internacionales fuera del lock
        self._enviarPandemia()
        self._comercio()


    def run(self):
        """ bucle principal del proceso de civilizacion """

        # inicamos aqui para que no de problemas
        self.lock = threading.Lock()

        # iniciamos el hilo de escucha de mensajes
        hilo = Thread(target=self._correo, daemon=True)
        hilo.start()
        try:

            # el bucle se ejecuta hasta el colapso o el limite de tiempo
            while self.anio < 100:

                # ejecucion de la logica interna y externa
                self._motor()
                
                # persistencia de datos en el buffer
                self._registrar()
                
                # sincronizacion
                self.barrera.wait()
                #print(f"[{self.nombre}]: finaliza ciclo {self.anio}")
                self.anio += 1

            #print(f"[{self.nombre}]: SIMULACION TERMINADA")

        except Exception as e:
            print(f"[{self.nombre}] error o interrupcion: {e}")

            # evitamos que los demas procesos se queden colgados
            self.barrera.abort()
            
        finally:
            self.colapso = True

            # desbloqueamos el hilo de correo
            self.buzon.put(None)

            # volcado final de seguridad
            with self.lock:
                if self.buffer:
                    with open(self.archivo, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(self.buffer)

            self.progress_queue.put({
                "tipo": "fin",
                "civilizacion": self.nombre
            })

            #hilo.join(timeout=1)
            #print(f"[{self.nombre}]: notificado fin")

