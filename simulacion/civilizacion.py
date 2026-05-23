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

        # almacena las ventas pendientes de cobro de la civilizacion {id_mensaje: precio_cobro}
        self.ventas_pendientes = {}

        # para la gestion de pandemias
        self.cache_comercio = {}
        self.capacidad_cache = 2


    def _enviarMensaje(self, msg: Mensaje) -> None:
        """ centraliza el envio de mensajes, con una probabilidad de perdida para un poco
        de caos
        """
        # protejemos con el lock ya que accedemos a self.directorio que puede ser modificado por el correo
        if random.random() > 0.15:
            try:
                if msg.destino in self.directorio:
                    self.directorio[msg.destino].put(msg)
            except Exception:
                pass  # el mensaje se pierde en la red (caos distribuido)


    def _actualizarCache(self, socio):
        """ actualiza la cache de contactos comerciales utilizando el algoritmo Second Chance (Clock) """
        with self.lock:
            # el socio ya esta en la cache, gana una segunda oportunidad
            if socio in self.cache_comercio:
                self.cache_comercio[socio] = 1
                return
            
            # el socio no esta en la cache pero hay espacio libre
            if len(self.cache_comercio) < self.capacidad_cache:
                self.cache_comercio[socio] = 1
                return
            
            # la cache esta llena, aplicamos el algoritmo Clock
            candidatos = list(self.cache_comercio.keys())
            
            # buscamos si hay alguno con bit 0
            for c in candidatos:
                if self.cache_comercio.get(c, 0) == 0:
                    del self.cache_comercio[c]
                    self.cache_comercio[socio] = 1
                    return
            
            # si todos tenian el bit 1, el primero de la lista es expulsado
            primer_candidato = candidatos[0]
            del self.cache_comercio[primer_candidato]
            self.cache_comercio[socio] = 1
            
            # el resto de elementos pierden su oportunidad
            for resto in self.cache_comercio:
                if resto != socio:
                    self.cache_comercio[resto] = 0


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
                try:
                    msg = self.buzon.get()
                except (OSError, TypeError, AttributeError):
                    break

                # señal de finalizacion del hilo
                if msg is None:
                    break

                with self.lock:
                    if msg.tipo == "comercio":
                        recurso = msg.payload["recurso"]
                        self.economia.recibir(recurso, msg.payload["cantidad"])
                        
                        # actualizamos la cache con el emisor del recurso
                        self._actualizarCache(msg.origen)

                        # enviamos el ack para confirmar la recepcion
                        ack = Mensaje(
                            origen=self.nombre,
                            destino=msg.origen,
                            tipo="ack_comercio",
                            payload={"id_referencia": msg.id}
                        )
                        self._enviarMensaje(ack)

                    elif msg.tipo == "ack_comercio":
                        id_trans = msg.payload["id_referencia"]
                        if id_trans in self.ventas_pendientes:
                            pago = self.ventas_pendientes.pop(id_trans)
                            self.economia.transaccion(pago) 

                    elif msg.tipo == "defuncion":
                        if msg.origen in self.directorio:
                            del self.directorio[msg.origen]

                    elif msg.tipo == "pandemia":
                        self.salud.importar(
                            msg.payload["cantidad"]
                        )

            except Empty:
                continue
            except Exception as e:
                print(f"[{self.nombre.upper()}-correo] Error inesperado: {e}")
                break


    def _enviarPandemia(self):
        """ propaga la infeccion a los contactos de la cache si se supera el umbral """

        with self.lock:
            if self.salud.infectados < 10 and random.random() < 0.05:
                self.salud.importar(50)
            
            if self.salud.infectados < 100:
                return

        with self.lock:
            # obtenemos los contactos comerciales actuales guardados en la cache de segunda oportunidad
            contactos_actuales = list(self.cache_comercio.keys())
        
        for destino in contactos_actuales:
            if random.random() < 0.75:
                msg = Mensaje(
                    origen=self.nombre,
                    destino=destino,
                    tipo="pandemia",
                    payload={"cantidad": int(self.salud.infectados * 0.10)}
                )
                self._enviarMensaje(msg)


    def _comercio(self):
        """ gestiona el comercio priorizando materiales como flujo constante"""

        with self.lock:
            pob = self.demografia.poblacionTotal
            precio_contrato = 2000.0
            
            puede_exportar_materiales = (self.economia.materiales > 2000)
            sobra_comida = (self.economia.alimentos > (pob * 500.0))
            necesita_energia = (self.economia.energia < 10000)
            
            recurso_a_enviar = None
            cantidad = 0

            if puede_exportar_materiales:
                recurso_a_enviar = "materiales"
                cantidad = 1500
            elif sobra_comida:
                recurso_a_enviar = "comida"
                cantidad = 5000
            elif necesita_energia and self.economia.pib > precio_contrato:
                recurso_a_enviar = "pago_por_energia"
                cantidad = 5000

            if recurso_a_enviar and self.economia.pib > precio_contrato:
                destinos = [x for x in self.directorio.keys() if x != self.nombre]

                if destinos:
                    destino = random.choice(destinos)
                    self._actualizarCache(destino)
                    if destino not in self.socios_ciclo:
                        self.socios_ciclo.append(destino)

                    # el emisor siempre paga el coste de logistica por adelantado
                    self.economia.transaccion(-precio_contrato)

                    # creamos el mensaje de comercio
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

                    # guardamos la venta en el mapa de transacciones en vuelo
                    self.ventas_pendientes[msg.id] = precio_contrato
                    self._enviarMensaje(msg)


    def _motor(self):
        """ nucleo del motor matematico que coordina todos los modulos """

        with self.lock:
            poblacion = self.demografia.poblacionTotal

            # condicion de parada
            if poblacion <= 0:
                self.colapso = True
                poblacion = 0

            fuerza_laboral = self.demografia.fuerzaLaboral          
            agricultores = int(fuerza_laboral * 0.45)
            mineros = int(fuerza_laboral * 0.15)
            energeticos = int(fuerza_laboral * 0.10)
            industria = max(0, fuerza_laboral - agricultores - mineros - energeticos)

            # extraccion de materiales y energia (la energia se trata como un recurso extraible)
            self.economia.extraerEnergia(energeticos)
            self.economia.extraerMinerales(mineros)
            
            # produccion de comida 
            comida = self.agricultura.producir(
                trabajadores=agricultores,
                tecnologia=self.economia.tecnologia,
                energia=self.economia.energia,
                fertilizantes=self.economia.materiales
            )
            self.economia.agregarComida(comida)

            # resolucion de salud y aplicar muertes por enfermedad y tal
            self.salud.avanzar(poblacion, self.economia.tecnologia)
            self.demografia.aplicarMuertes(self.salud.muertes)

            self.demografia.avanzar(
                self.economia.alimentos,
                self.sociopolitica.tension,
                self.economia.tecnologia
            )

            # calculo de la economia
            self.economia.avanzar(
                trabajadores=industria,
                poblacion=poblacion,
                corrupcion=self.sociopolitica.corrupcion,
                capital_humano=self.demografia.capitalHumano,
                contaminacion=self.agricultura.contaminacion
            )

            self.agricultura.actualizar(poblacion, self.economia.pib)

            # avanzamos en sociopolitca, y vemos si ha habido revuelta
            hubo_revuelta = self.sociopolitica.avanzar(
                pib=self.economia.pib,
                poblacion=poblacion,
                desigualdad=self.economia.gini,
                racionamiento=self.economia.racionamiento
            )

            if hubo_revuelta:
                self.sociopolitica.ejecutarRevolucion(poblacion)

                bajas_conflicto = int(poblacion * random.uniform(0.1, 0.3))
                self.demografia.aplicarMuertes(bajas_conflicto, "revolucion")
                
        # interacciones internacionales fuera del lock
        self._enviarPandemia()
        self._comercio()

        self.progress_queue.put({
            "tipo": "progreso",
            "civilizacion": self.nombre,
            "anio": self.anio
        })


    def run(self):
        """ bucle principal del proceso de civilizacion """

        # indicamos aqui para que no de problemas
        self.lock = threading.RLock()

        # iniciamos el hilo de escucha de mensajes
        hilo = Thread(target=self._correo, daemon=True)
        hilo.start()
        try:
            while self.anio < 100:
                self._motor()

                # persistencia datos del buffer
                self._registrar()

                # sincronizacion                
                self.barrera.wait()
                self.anio += 1
        except Exception as e:
            print(f"[{self.nombre}] error o interrupcion: {e}")

            # evitamos que el resto de procesos se queden colgados esperando
            # a una civilizacion muerta
            self.barrera.abort()
            
        finally:
            self.colapso = True

            msg_muerte = Mensaje(
                origen=self.nombre,
                destino="broadcast",
                tipo="defuncion",
                payload={}
            )

            with self.lock:
                destinos_finales = list(self.directorio.keys())

            for destino in destinos_finales:
                if destino != self.nombre:
                    msg_muerte.destino = destino
                    self._enviarMensaje(msg_muerte)

            self.buzon.put(None)

            # volcado final
            with self.lock:
                if self.buffer:
                    with open(self.archivo, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerows(self.buffer)

            self.progress_queue.put({
                "tipo": "fin",
                "civilizacion": self.nombre
            })
            
          