import numpy as np

class Demografia:
    def __init__(self, poblacion_ini):

        # poblacion dividida en [jovenes, activos, ancianos]
        self.__poblacion = np.array(poblacion_ini, dtype=float)

        # el capital humano (educacion) empieza bajo y frena la natalidad al subir
        self.__capital_humano = 0.5
        self.__req_calorico = 1.2

    @property
    def poblacionTotal(self): 
        return int(np.sum(self.__poblacion))
        
    @property
    def fuerzaLaboral(self): 
        return int(self.__poblacion[1])
        
    @property
    def capitalHumano(self): 
        return self.__capital_humano


    def aplicarMuertes(self, cantidad, tipo=None):
        """ resta muertes por pandemia/revolucion del conteo poblacional """
        pob_antes = self.poblacionTotal
        if pob_antes <= 0: return

        if tipo:
            if tipo == "revolucion":
                # pesos de mortalidad: 70% activos, 20% jovenes, 10% ancianos
                pesos = np.array([0.20, 0.70, 0.10])
                muertes_por_grupo = cantidad * pesos

                for i in range(3):
                    bajas = min(self.__poblacion[i], muertes_por_grupo[i])
                    self.__poblacion[i] -= bajas

        else:
            # las pandemias suelen afectar mas a ancianos 
            for i in [2, 1, 0]: 
                bajas = min(self.__poblacion[i], cantidad)
                self.__poblacion[i] -= bajas
                cantidad -= bajas


    def _leslie(self, salud, tension_social, seguridad_alm):
        """ construye la matriz de transicion de poblacion """
        
        # reduccion drastica de natalidad si no hay comida (seguridad_alm < 1.0)
        # usamos un crecimiento exponencial para que la falta de comida sea critica
        f_max = 0.25 
        freno_educ = np.exp(-0.7 * self.__capital_humano)
        freno_social = max(0.05, 1.0 - (tension_social / 100.0))
        
        # impacto de la desnutricion en la natalidad
        impacto_comida = np.power(seguridad_alm, 2) 
        f2 = f_max * freno_educ * freno_social * impacto_comida

        # la supervivencia cae si la salud es mala o no hay comida
        s_base = min(0.98, 0.90 + (salud / 1000.0)) * min(1.0, seguridad_alm)

        t1 = 1/15.0 
        t2 = 1/45.0 

        matriz = np.array([
            [(1-t1)*s_base, f2,            0],    
            [t1*s_base,     (1-t2)*s_base, 0],    
            [0,             t2*s_base,     0.85 * s_base] # ancianos mueren mas rapido sin comida
        ])
        
        return matriz

    def avanzar(self, comida_disp, tension_social, nivel_tec):
        necesidad_total = self.poblacionTotal * self.__req_calorico
        
        # si no hay poblacion, no hay nada que calcular
        if necesidad_total <= 0:
            return

        seg_alimentaria = comida_disp / necesidad_total
        
        # limitamos el beneficio del exceso de comida pero no el perjuicio de la falta
        seg_alimentaria_ajustada = min(1.1, seg_alimentaria)

        salud_base = 50.0 
        matriz = self._leslie(salud_base, tension_social, seg_alimentaria_ajustada)
        self.__poblacion = np.dot(matriz, self.__poblacion)
        self.__poblacion = np.maximum(0, self.__poblacion)

        if tension_social < 30:
            self.__capital_humano = min(1.0, self.__capital_humano + 0.002)