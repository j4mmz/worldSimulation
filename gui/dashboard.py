import os
import flet as ft
import plotly.graph_objects as go
from plotly.subplots import make_subplots

class Dashboard(ft.Container):

    def __init__(self, state):
        super().__init__()
        self.state = state

        self.continent_checks = {
            "asia": ft.Checkbox(label="Asia", value=True),
            "europa": ft.Checkbox(label="Europa", value=False),
            "america": ft.Checkbox(label="America", value=False),
            "africa": ft.Checkbox(label="Africa", value=False),
        }

        self.variable_checks = {
            "poblacion": ft.Checkbox(label="Poblacion", value=True),
            "pib": ft.Checkbox(label="PIB"),
            "energia": ft.Checkbox(label="Energia"),
            "tension": ft.Checkbox(label="Tension"),
            "infectados": ft.Checkbox(label="Infectados"),
            "contaminacion": ft.Checkbox(label="Contaminacion"),
        }

        self.btn = ft.ElevatedButton(
            "Graficar",
            on_click=self.generar_grafica
        )

        self.chart_container = ft.Container(
            height=700,
            expand=True
        )

        self.content = ft.Column(
            alignment=ft.MainAxisAlignment.CENTER,
            horizontal_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Text("Dashboard de Civilizaciones", size=30),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Column([
                            ft.Text("Continentes"),
                            *self.continent_checks.values()
                        ]),

                        ft.Column([
                            ft.Text("Variables"),
                            *self.variable_checks.values()
                        ]),

                        self.btn
                    ]
                ),

                self.chart_container
            ]
        )

    def generar_grafica(self, e):
        continentes = [k for k, v in self.continent_checks.items() if v.value]
        variables = [k for k, v in self.variable_checks.items() if v.value]

        if not continentes or not variables:
            self.chart_container.content = ft.Text(
                "Selecciona al menos un continente y una variable"
            )

            self.update()
            return

        # crea un subplot por variable
        fig = make_subplots(
            rows=len(variables),
            cols=1,
            shared_xaxes=True,
            subplot_titles=[
                variable.title()
                for variable in variables
            ],
            vertical_spacing=0.08
        )

        for fila, variable in enumerate(variables, start=1):
            for continente in continentes:
                data = self.state.data.get(continente, [])

                if not data:
                    continue

                x = [d["year"] for d in data]
                y = [d.get(variable, 0) for d in data]

                fig.add_trace(go.Scatter(x=x, y=y, mode="lines", name=continente.title()), row=fila, col=1)

            fig.update_yaxes(
                title_text=variable.title(),
                row=fila,
                col=1
            )

        fig.update_layout(
            title="Analisis de la Simulacion",
            xaxis_title="",
            height=300 * len(variables),
            showlegend=True
        )

        graph_path = "grafica.html"
        fig.write_html(graph_path)
        fig.show()
        self.update()