import json
import multiprocessing

from simulacion.civilizacion import Civilizacion


def dividir_poblacion(total, continente):
    porcentajes = {
        "asia": (0.23, 0.67, 0.10),
        "europa": (0.15, 0.64, 0.21),
        "america": (0.20, 0.66, 0.14),
        "africa": (0.40, 0.56, 0.04)
    }

    jovenes_p, activos_p, ancianos_p = porcentajes[continente]
    jovenes = int(total * jovenes_p)
    activos = int(total * activos_p)
    ancianos = total - jovenes - activos

    return [jovenes, activos, ancianos]


def runSim(progress_queue):
    CONTINENTES = [
        "asia",
        "europa",
        "america",
        "africa"
    ]

    # lectura de configuracion
    with open("config.json", "r", encoding="utf-8") as f:
        datos = json.load(f)

    configuraciones = {}
    
    for continente in CONTINENTES:
        datos_continente = datos[continente.lower()]
        poblacion_total = datos_continente["poblacion"]
        configuraciones[continente] = {

            "poblacion": dividir_poblacion(
                poblacion_total,
                continente
            ),
            "capital": datos_continente["capital"],
            "tierra": datos_continente["tierra"],
            "energia": datos_continente["energia"]
        }

    # iniciamos las barreras
    barrera = multiprocessing.Barrier(
        len(CONTINENTES)
    )

    buzones = {
        nombre: multiprocessing.Queue()
        for nombre in CONTINENTES
    }

    procesos = []

    # creamos los procesos
    for nombre in CONTINENTES:

        p = Civilizacion(
            nombre=nombre,
            config=configuraciones[nombre],
            buzon=buzones[nombre],
            directorio=buzones,
            barrera=barrera,
            progress_queue=progress_queue
        )

        procesos.append(p)

    # inicio
    for p in procesos:
        p.start()

    # espera
    for p in procesos:
        p.join()
    
    progress_queue.put({"tipo": "fin_global"})
    print("FIN DE LA SIMULACION")


if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True
    )

    runSim(multiprocessing.Queue())