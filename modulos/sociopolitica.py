import math
import random
import numpy as np


class Sociopolitica:
    def __init__(self):
        self.__tension = 10.0
        self.__corrupcion = 0.15
        self.__prob_revuelta = 0.0
        self.__cooldown = 0

    @property
    def tension(self): return self.__tension
    @property
    def corrupcion(self): return self.__corrupcion

    def avanzar(self, pib, poblacion, desigualdad, racionamiento):
        if self.__cooldown > 0:
            self.__cooldown -= 1

            # durante el cooldown la tension baja gradualmente, no a cero de golpe
            self.__tension *= 0.5
            return

        pib_pc = (pib / poblacion) if poblacion > 0 else 0
        
        # el pib_pc ayuda a calmar a las masas
        z = -4.0 + (5.0 * desigualdad) + (10.0 * racionamiento) - (2.0 * pib_pc)

        self.__prob_revuelta = 1.0 / (1.0 + math.exp(-z))
        self.__tension = self.__prob_revuelta * 100.0

        # solo estalla si la tension es realmente insoportable
        if self.__tension > 80 and np.random.random() < 0.1:
            return True 
        return False

    def ejecutarRevolucion(self, poblacion):
        """ ejecuta la revolucion, con reiniciando parametros y tal """
        self.__cooldown = 15
        self.__corrupcion = 0.10
        self.__tension = 20.0
        
        # retornamos las bajas por revolucion 
        # deberia depender de la corrupcion y la tension previa a la revolucion
        # pero de momento se queda asi simplificado
        return int(poblacion * random.uniform(0.1, 0.3))