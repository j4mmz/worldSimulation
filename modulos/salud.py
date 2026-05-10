import numpy as np

class Salud:
    def __init__(self):
        self.infectados = 0.0
        self.muertes = 0
        self.inmunes = 0.0 
        self.__capacidad_hospitalaria = 0.0
        self.__tasa_recuperacion = 0.20 

    @property
    def infectadosTotales(self): 
        return int(self.infectados)

    def importar(self, cantidad):
        self.infectados += cantidad

    def avanzar(self, poblacion, tecnologia):
        if poblacion <= 0:
            self.infectados, self.muertes, self.inmunes = 0, 0, 0
            return

        # calculo de susceptibles 
        susceptibles = max(0, poblacion - self.infectados - self.inmunes)
        
        # la tecnologia reduce la tasa de contagio base 
        tasa_contagio_base = 0.35 
        tasa_mitigada = tasa_contagio_base * np.exp(-0.2 * tecnologia)
        
        # nuevos infectados (modelo sir: depende de infectados Y susceptibles)
        probabilidad_encuentro = (self.infectados / poblacion) if poblacion > 0 else 0
        nuevos_infectados = susceptibles * probabilidad_encuentro * tasa_mitigada
        
        # mutacion local esporadica
        if self.infectados < 1 and np.random.random() < 0.02:
            nuevos_infectados = 5

        self.infectados += nuevos_infectados
        
        # resolucion de bajas y saturacion medica
        self.__capacidad_hospitalaria = poblacion * 0.08 * tecnologia
        sobrecarga = max(0, self.infectados - self.__capacidad_hospitalaria)
        
        muertes_normales = (self.infectados - sobrecarga) * 0.02
        muertes_crisis = sobrecarga * 0.15 # la saturacion es mas letal ahora
        self.muertes = int(muertes_normales + muertes_crisis)
        
        # recuperacion y perdida de inmunidad 
        recuperados = self.infectados * self.__tasa_recuperacion
        self.infectados = max(0, self.infectados - recuperados - self.muertes)
        
        # los recuperados pasan a ser inmunes
        self.inmunes += recuperados
        
        # la inmunidad no es eterna 
        perdida_inmunidad = self.inmunes * 0.05
        self.inmunes -= perdida_inmunidad