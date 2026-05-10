import numpy as np

class Agricultura:
    def __init__(self, tierra_inicial):
        self.__tierra_max = tierra_inicial
        self.__tierra_arable = tierra_inicial
        self.__fertilidad = 1.0
        self.__contaminacion = 0.0

    @property
    def contaminacion(self): return self.__contaminacion

    def producir(self, trabajadores, tecnologia, energia, fertilizantes):
        """ calcula la produccion de alimentos segun el modelo world3 """

        if self.__tierra_arable <= 0: return 0.0
        
        # el capital (fertilizantes/energia) multiplica la capacidad del suelo
        intensidad = 1.0 + (min(energia, fertilizantes) / 1000)
        freno_toxico = np.exp(-0.0001 * self.__contaminacion)
        
        rendimiento = 15.0 * self.__fertilidad * tecnologia * intensidad * freno_toxico
        capacidad_mano_obra = trabajadores * 30.0
        
        produccion = min(capacidad_mano_obra, self.__tierra_arable * rendimiento)
        return produccion

    def actualizar(self, poblacion, pib):
        """ simula la degradacion y recuperacion del ecosistema """

        degradacion = (poblacion * 0.00001) 
        self.__fertilidad = max(0.3, self.__fertilidad - degradacion)
        
        # la contaminacion industrial tambien afecta la fertilidad
        #self.__contaminacion = (self.__contaminacion + (pib * 0.05)) * 0.92
        self.__contaminacion = (self.__contaminacion + (pib * 0.05)) * 0.99