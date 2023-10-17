import sys
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIntValidator
import pandas as pd
import random
import itertools

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Optimal turistical route")
        self.setGeometry(100, 100, 400, 300)

        self.distances = pd.read_csv('data/odleglosci.csv')
        self.distances.set_index('city', inplace=True)
        self.wagi_miast = pd.read_csv('data/wagi_miast.csv')
        self.city_weights = pd.Series(self.wagi_miast['srednia_waga'].values, index=self.wagi_miast['Nazwa'])

        self.threshold_distance = 1500
        self.num_cities = 5
        self.num_iterations = 1000
        self.num_solutions = 5

        self.threshold_distance_label = QLabel("Threshold Distance:", self)
        self.threshold_distance_input = QLineEdit(str(self.threshold_distance), self)
        self.threshold_distance_input.setValidator(QIntValidator(1, 9999999, self))

        self.num_cities_label = QLabel("Number of Cities:", self)
        self.num_cities_input = QLineEdit(str(self.num_cities), self)
        self.num_cities_input.setValidator(QIntValidator(1, 9999999, self))

        self.num_iterations_label = QLabel("Number of Iterations:", self)
        self.num_iterations_input = QLineEdit(str(self.num_iterations), self)
        self.num_iterations_input.setValidator(QIntValidator(1, 9999999, self))

        self.num_solutions_label = QLabel("Number of Solutions:", self)
        self.num_solutions_input = QLineEdit(str(self.num_solutions), self)
        self.num_solutions_input.setValidator(QIntValidator(1, 9999999, self))

        self.start_city_label = QLabel("Start City:", self)
        self.start_city_combo = QComboBox(self)
        self.start_city_combo.addItems(self.distances.columns.tolist())

        self.run_button = QPushButton("Run", self)
        self.run_button.clicked.connect(self.run_algorithm)

        self.solution_labels = []

        layout = QVBoxLayout()
        layout.addWidget(self.threshold_distance_label)
        layout.addWidget(self.threshold_distance_input)
        layout.addWidget(self.num_cities_label)
        layout.addWidget(self.num_cities_input)
        layout.addWidget(self.num_iterations_label)
        layout.addWidget(self.num_iterations_input)
        layout.addWidget(self.num_solutions_label)
        layout.addWidget(self.num_solutions_input)
        layout.addWidget(self.start_city_label)
        layout.addWidget(self.start_city_combo)
        layout.addWidget(self.run_button)

        self.solution_widget = QWidget(self)
        self.solution_layout = QVBoxLayout(self.solution_widget)

        central_widget = QWidget(self)
        central_layout = QVBoxLayout(central_widget)
        central_layout.addLayout(layout)
        central_layout.addWidget(self.solution_widget)
        self.setCentralWidget(central_widget)

    def run_algorithm(self):
        self.threshold_distance = int(self.threshold_distance_input.text())
        self.num_cities = int(self.num_cities_input.text())
        self.num_iterations = int(self.num_iterations_input.text())
        self.num_solutions = int(self.num_solutions_input.text())
        self.start_city = self.start_city_combo.currentText()

        optimal_routes = []
        max_city_weight = float('-inf')

        for _ in range(self.num_iterations):
            cities = random.sample(self.distances.columns.tolist(), self.num_cities - 1)
            permutations = list(itertools.permutations(cities))
            permutations = [[self.start_city] + list(permutation) + [self.start_city] for permutation in permutations]

            for route in permutations:
                total_distance = sum(self.distances.loc[route[i], route[i + 1]] for i in range(len(route) - 1))
                total_weight = self.city_weights[route].sum()

                if total_distance < self.threshold_distance and total_weight > max_city_weight:
                    optimal_routes.append(route)
                    max_city_weight = total_weight
                elif total_distance < self.threshold_distance and total_weight == max_city_weight:
                    optimal_routes.append(route)

        optimal_routes.sort(key=lambda r: self.city_weights[r].sum() /
                                          sum(self.distances.loc[r[j], r[j + 1]] for j in range(len(r) - 1)))
        optimal_routes = optimal_routes[:self.num_solutions]

        for label in self.solution_labels:
            label.deleteLater()

        self.solution_labels = []
        optimal_routes.reverse()

        for i, optimal_route in enumerate(optimal_routes):
            solution_label = QLabel(self.solution_widget)
            solution_label.setText(f"Solution {i + 1}\n"
                                   f"Optimal Route: {optimal_route}\n"
                                   f"Sum of Distances: {sum(self.distances.loc[optimal_route[j], optimal_route[j + 1]] for j in range(len(optimal_route) - 1))}\n"
                                   f"Maximum City Weight: {self.city_weights[optimal_route].sum()}")
            self.solution_labels.append(solution_label)
            self.solution_layout.addWidget(solution_label)

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())