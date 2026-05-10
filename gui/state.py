class SimulationState:

    def __init__(self):
        # datos estructurados
        self.data = {
            "asia": [],
            "europa": [],
            "america": [],
            "africa": []
        }

        self.current_year = 0
        self.max_year = 1000

        self.selected_variable = "poblacion"
        self.selected_continents = ["asia", "europa", "america", "africa"]

    def add_snapshot(self, continent, year, stats):
        self.data[continent].append({"year": year, **stats})