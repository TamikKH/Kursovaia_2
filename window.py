from PyQt6.QtWidgets import (
    QWidget, QLabel, QPushButton,
    QVBoxLayout, QGridLayout,
    QComboBox, QSpinBox, QDoubleSpinBox
)

from Kursach import main


class MyWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Агросистема")
        self.setFixedSize(420, 550)

        self.fields = {
            'Region': ("Регион:", ["Europe", "Asia", "North America", "South America", "Australia"]),
            'Soil_Type': ("Тип почвы:", ["Sandy", "Clay", "Loam", "Peaty", "Silt", "Chalky"]),
            'Soil_pH': ("pH почвы:", float),
            'Organic_Matter_%': ("Орг. вещество (%):", float),
            'Rainfall_mm_per_year': ("Осадки:", int),
            'Temperature_C_avg': ("Температура:", float),
            'Climate_Zone': ("Климат:", ["Tropical", "Temperate", "Dry", "Continental", "Polar"]),
            'Irrigation_Level': ("Орошение:", ["Low", "Medium", "High"]),
            'Soil_Fertility': ("Плодородие:", ["Low", "Medium", "High"]),
            'Growing_Season_days': ("Дни:", int)
        }

        self.inputs = {}
        grid = QGridLayout()

        for i, (key, (label_text, field_type)) in enumerate(self.fields.items()):
            label = QLabel(label_text)

            if isinstance(field_type, list):
                widget = QComboBox()
                widget.addItems(field_type)
            elif field_type == int:
                widget = QSpinBox()
                widget.setRange(0, 100000)
            else:
                widget = QDoubleSpinBox()
                widget.setRange(0.0, 1000.0)
                widget.setDecimals(2)

                if key == 'Soil_pH':
                    widget.setRange(0.0, 14.0)

            self.inputs[key] = widget
            grid.addWidget(label, i, 0)
            grid.addWidget(widget, i, 1)

        self.button = QPushButton("Рассчитать")
        self.button.clicked.connect(self.process_data)

        self.result_label = QLabel("")
        self.result_label.setWordWrap(True)

        layout = QVBoxLayout()
        layout.addLayout(grid)
        layout.addWidget(self.button)
        layout.addWidget(self.result_label)

        self.setLayout(layout)

    def process_data(self):
        test = {}

        try:
            for key, (_, field_type) in self.fields.items():
                widget = self.inputs[key]

                if isinstance(field_type, list):
                    value = widget.currentText()
                else:
                    value = widget.value()

                test[key] = value

            yield_result, crop_result = main(test)

            self.result_label.setText(
                f"Урожайность: {yield_result:.2f} т/га\n"
                f"Культура: {crop_result}"
            )

        except Exception as e:
            self.result_label.setText(f"Ошибка: {str(e)}")