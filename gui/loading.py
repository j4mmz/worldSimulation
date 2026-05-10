import time
import threading
import flet as ft
import multiprocessing
from queue import Empty

from simulacion.motorPrincipal import runSim


class LoadingScreen(ft.Container):

    def __init__(self, page, config_data, on_finish):
        super().__init__()

        self._page = page
        self.config_data = config_data
        self.on_finish = on_finish
        self.queue = multiprocessing.Queue()
        #self.bgcolor = "#111"
        self.expand = True
        self.loading_text = ft.Text("Iniciando Simulación...", color="white", size=20)
        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            expand=True,
            controls=[
                ft.ProgressRing(color="white", width=50, height=50),
                self.loading_text,
                ft.Text("Esto puede tardar unos segundos", color="white54", size=12, italic=True)
            ]
        )

    def start(self):
        threading.Thread(target=self._run_sim, daemon=True).start()
        threading.Thread(target=self._listen, daemon=True).start()

    def _run_sim(self):
        try:
            runSim(self.queue)
        except Exception as e:
            print(f"Error en motor simulación: {e}")

    def _listen(self):
        while True:
            try:
                msg = self.queue.get(timeout=0.2)
                
                if msg.get("tipo") == "fin_global":
                    break
                
                # creo que no sirve de nada, pero por si acaso...
                if msg.get("tipo") == "progreso":
                    anio = msg.get("anio")
                    cont = msg.get("civilizacion").title()
                    self.loading_text.value = f"Simulando: {cont} (Año {anio})"
                    self._page.update()

            except Empty:
                continue

        self.loading_text.value = "Generando reportes..."
        self._page.update()
        time.sleep(0.5) 
        self.on_finish({"ok": True})