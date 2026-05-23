import numpy as np

class Economia:
    def __init__(self, capital_inicial, energia_inicial):
        self.__pib = 0.0
        self.__capital_fisico = capital_inicial
        self.__tecno = 1.0
        self.__gini = 0.35
        self.__deuda = 0.0
        self.__racionamiento = 0.0
        
        # almacen de recursos base
        self.__recursos = {
            "alimentos": 50000.0,
            "energia": energia_inicial,
            "materiales": 10000.0
        }

    @property
    def pib(self): return self.__pib
    @pib.setter
    def pib(self, i): self.__pib +=  i

    @property
    def tecnologia(self): return self.__tecno

    @property
    def alimentos(self): return self.__recursos["alimentos"]

    @property
    def energia(self): return self.__recursos["energia"]

    @property
    def materiales(self): return self.__recursos["materiales"]

    @property
    def gini(self): return self.__gini

    @property
    def deuda(self): return self.__deuda

    @property
    def racionamiento(self): return self.__racionamiento


    def transaccion(self, precio):
        self.__pib = max(0, self.__pib + precio)

    def recibir(self, recurso, cantidad):
        """ gestiona la entrada de mercancias por comercio """
        
        self.__recursos[recurso] += cantidad

    def agregarComida(self, cantidad):
        self.__recursos["alimentos"] += cantidad

    def extraerEnergia(self, trabajadores):
        """ genera energia basandose en la fuerza laboral y tecnologia """

        extraccion = trabajadores * 50.0 * self.__tecno
        self.__recursos["energia"] += extraccion

    def extraerMinerales(self, trabajadores):
        """ genera materiales base para el mantenimiento del capital """

        extraccion = trabajadores * 20.0 * self.__tecno
        self.__recursos["materiales"] += extraccion

    def _cobbDouglas(self, trabajadores, contaminacion):
        """ funcion de produccion con penalizaciones por falta de energia y contaminacion """

        alpha = 0.33
        
        # el capital minimo evita el bloqueo total de la economia
        cap_efectivo = max(1.0, self.__capital_fisico)
        
        # factor de eficiencia energetica
        demanda_e = cap_efectivo * 0.05
        eficiencia_e = 1.0
        if demanda_e > 0 and self.__recursos["energia"] < demanda_e:
            eficiencia_e = max(0.1, self.__recursos["energia"] / demanda_e)
            
        freno_toxico = np.exp(-0.00005 * contaminacion)
        
        prod_base = self.__tecno * eficiencia_e * freno_toxico * (cap_efectivo**alpha) * (trabajadores**(1-alpha))
        return max(100.0, prod_base)
    
    def avanzar(self, trabajadores, poblacion, corrupcion, capital_humano, contaminacion):
        """ actualiza el ciclo economico anual """
        self.__pib = self._cobbDouglas(trabajadores, contaminacion)
        
        # logica de racionamiento
        demanda_alimento = poblacion * 1.2
        if self.__recursos["alimentos"] < demanda_alimento:
            self.__racionamiento = 1.0 - (self.__recursos["alimentos"] / demanda_alimento)
            self.__recursos["alimentos"] = 0
        else:
            self.__recursos["alimentos"] -= demanda_alimento
            self.__racionamiento = 0.0

        # inversion y depreciacion vinculada a materiales
        inversion = self.__pib * 0.15
        materiales_usados = min(inversion, self.__recursos["materiales"])
        self.__recursos["materiales"] -= materiales_usados
        
        # si faltan materiales para reparar, el capital se degrada mas rapido
        tasa_depreciacion = 0.05 if materiales_usados >= inversion else 0.15
        self.__capital_fisico = (self.__capital_fisico * (1 - tasa_depreciacion)) + materiales_usados
        
        # actualizacion tecnologica basada en pib per capita
        if poblacion > 0 and (self.__pib / poblacion) > 0.5:
            self.__tecno += 0.01 * capital_humano if (self.__pib / poblacion) < 0.7 else  0.05 * capital_humano