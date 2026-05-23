import os
import csv
import flet as ft
import multiprocessing
import plotly.graph_objects as go

from gui.config import ConfigParams
from gui.loading import LoadingScreen
from gui.state import SimulationState
from gui.dashboard import Dashboard

class App:

    def __init__(self, page: ft.Page):
        self.page = page
        self.page.title = "World Simulator"
        self.page.window.width = 1200
        self.page.window.height = 700

        self.show_config()
        self.state = SimulationState()

    # pantalla de configuracion
    def show_config(self):

        self.page.clean()

        config = ConfigParams(
            on_start=self.show_loading
        )

        self.page.add(config)
        self.page.update()

    # pantalla de carga
    def show_loading(self, config_data):

        self.page.clean()

        loading = LoadingScreen(
            self.page,
            config_data=config_data,
            on_finish=self.show_results
        )

        self.page.add(loading)
        self.page.update()

        loading.start()

    # cargar y mostrar resultados
    def load_csv(self):
        continentes = ["asia", "europa", "america", "africa"]

        for c in continentes:
            path = f"datos/{c}.csv"

            if not os.path.exists(path):
                continue

            with open(path, newline="") as f:
                reader = csv.DictReader(f)

                for row in reader:
                    self.state.add_snapshot(
                        c,
                        int(row["anio"]),
                        {
                            "poblacion": int(row["poblacion"]),
                            "pib": float(row["pib"]),
                            "energia": float(row["energia"]),
                            "tension": float(row["tension"]),
                            "infectados": int(row["infectados"])
                        }
                    )

    def show_results(self, data):
        self.page.clean()

        self.load_csv()

        dashboard = Dashboard(self.state)

        self.page.add(dashboard)
        self.page.update()


def main(page: ft.Page):
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER
    page.vertical_alignment = ft.MainAxisAlignment.CENTER
    page.bgcolor = ft.Colors.GREY
    App(page)

if __name__ == "__main__":
    multiprocessing.set_start_method("spawn", force=True)
    ft.run(main)