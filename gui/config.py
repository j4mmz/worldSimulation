import json
import flet as ft


class ConfigParams(ft.Container):

    def __init__(self, on_start):
        super().__init__()

        self.on_start = on_start
        self.width = 1150
        self.padding = 20
        self.border_radius = 15
        self.bgcolor = ft.Colors.GREY

        self.inputs = {}

        self.default = {
             "asia": {
                "poblacion": 4700,
                "capital": 45000,
                "tierra": 14000,
                "energia": 9000
            },

            "europa": {
                "poblacion": 1450,
                "capital": 40000,
                "tierra": 7000,
                "energia": 6000
            },

            "america": {
                "poblacion": 1050,
                "capital": 55000,
                "tierra": 18000,
                "energia": 10000
            },

            "africa": {
                "poblacion": 1450,
                "capital": 12000,
                "tierra": 22000,
                "energia": 3000
            }
        }

        self.content = ft.Column(
            spacing=20,
            controls=[

                ft.Row(
                    spacing=20,
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Column(
                            spacing=20,
                            controls=[
                                self.crear_continente("asia", ft.Colors.AMBER_700),
                                self.crear_continente("america", ft.Colors.TEAL_700),
                            ]
                        ),
                        ft.Column(
                            spacing=20,
                            controls=[
                                self.crear_continente("europa", ft.Colors.BLUE_GREY_700),
                                self.crear_continente("africa", ft.Colors.DEEP_ORANGE_800),
                            ]
                        ),
                    ]
                ),

                ft.Row(
                    alignment=ft.MainAxisAlignment.CENTER,
                    controls=[
                        ft.Button(
                            "Iniciar Simulacion",
                            icon=ft.Icons.PLAY_ARROW,
                            on_click=self.ejecutar_sim,
                        )
                    ]
                )
            ]
        )

    # crea un container para un continente
    def crear_continente(self, nombre, color):
        poblacion = ft.TextField(
            label="Poblacion Inicial",
            hint_text=str(self.default[nombre]["poblacion"]).title(),
            width=245,
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.ORANGE_100,
        )

        capital = ft.TextField(
            label="Capital Inicial",
            hint_text=str(self.default[nombre]["capital"]),
            width=245,
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.ORANGE_100,
        )

        tierra = ft.TextField(
            label="Tierra Inicial",
            hint_text=str(self.default[nombre]["tierra"]),
            width=245,
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.ORANGE_100,
        )

        energia = ft.TextField(
            label="Energia Inicial",
            hint_text=str(self.default[nombre]["energia"]),
            width=245,
            keyboard_type=ft.KeyboardType.NUMBER,
            filled=True,
            bgcolor=ft.Colors.ORANGE_100,
        )

        self.inputs[nombre] = {
            "poblacion": poblacion,
            "capital": capital,
            "tierra": tierra,
            "energia": energia,
        }

        return ft.Container(
            bgcolor=color,
            border_radius=15,
            padding=20,
            content=ft.Column(
                spacing=20,
                controls=[
                    ft.Text(nombre.title(), size=34, weight=ft.FontWeight.BOLD),
                    ft.Row([poblacion, capital]),
                    ft.Row([tierra, energia]),
                ]
            )
        )

    # mete los datos en un diccionario
    def obtener_datos(self):
        datos = {}

        for continente, parametros in self.inputs.items():
            datos[continente.lower()] = {}

            for parametro, textfield in parametros.items():
                valor = textfield.value

                if valor is None or valor == "":
                    valor = self.default[continente.lower()][parametro]
                else:
                    try:
                        valor = int(valor)
                    except:
                        valor = self.default[continente.lower()][parametro]

                datos[continente.lower()][parametro] = valor

        return datos

    # guarda los datos en un archivo JSON
    def guardar_datos(self, datos):
        with open("config.json", "w", encoding="utf-8") as archivo:
            json.dump(datos, archivo, indent=4, ensure_ascii=False)

    def ejecutar_sim(self, e):
        datos = self.obtener_datos()
        self.guardar_datos(datos)
        self.on_start(datos)