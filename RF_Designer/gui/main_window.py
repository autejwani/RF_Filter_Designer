# gui/main_window.py
# Main application window. Built with PyQt6.
# The window is split into two panels:
# Left  — controls (filter type, response, frequency, order, impedance)
# Right — matplotlib plot showing the S21 frequency response

# When the user clicks "Design Filter", the app:
# 1. Reads all parameters from the controls
# 2. Calls the appropriate design function (lowpass/highpass/bandpass)
# 3. Runs the ABCD simulation
# 4. Updates the plot
# 5. Populates the component table
import os
import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget,
    QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QComboBox, QSpinBox, QDoubleSpinBox,
    QPushButton, QTableWidget, QTableWidgetItem,
    QGroupBox, QSplitter, QHeaderView
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QColor

# Matplotlib imports for embedding the plot inside PyQt6
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

# Our filter design and simulation modules
from filters.lowpass   import design_lowpass
from filters.highpass  import design_highpass
from filters.bandpass  import design_bandpass
from simulation.abcd   import simulate, plot_response

class PlotCanvas(FigureCanvas):
    def __init__(self, parent=None):
        self.fig = Figure(figsize=(8, 5), facecolor='#1e1e1e')
        self.ax = self.fig.add_subplot(111, facecolor='#1e1e1e')

        super().__init__(self.fig)
        self.setParent(parent)

        self._style_axes()

    def _style_axes(self):
        self.ax.tick_params(colors='white')
        self.ax.xaxis.label.set_color('white')
        self.ax.yaxis.label.set_color('white')
        self.ax.title.set_color('white')
        for spine in self.ax.spines.values():
            spine.set_color('#444444')

    def clear(self):
        self.ax.cla()
        self._style_axes()
        self.draw()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('RF Filter Designer')
        self.setMinimumSize(1100, 650)

        self.current_components = []
        self._build_ui()

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)

        top_layout = QHBoxLayout(central)
        top_layout.setSpacing(10)
        top_layout.setContentsMargins(10, 10, 10, 10)

        # Left panel
        left_panel = QWidget()
        left_panel.setFixedWidth(280)
        left_layout = QVBoxLayout(left_panel)
        left_layout.setSpacing(8)

        title = QLabel('RF Filter Designer')
        title.setFont(QFont('Arial', 14, QFont.Weight.Bold))
        title.setStyleSheet('color: #00aaff;')
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        left_layout.addWidget(title)

        # Filter type group
        type_group = QGroupBox('Filter Type')
        type_group.setStyleSheet('QGroupBox { color: white; }')
        type_layout = QGridLayout(type_group)

        type_layout.addWidget(QLabel('Topology:'), 0, 0)
        self.combo_topology = QComboBox()
        self.combo_topology.addItems(['Low-Pass', 'High-Pass', 'Band-Pass'])
        self.combo_topology.currentTextChanged.connect(self._on_topology_changed)
        type_layout.addWidget(self.combo_topology, 0, 1)

        type_layout.addWidget(QLabel('Response:'), 1, 0)
        self.combo_response = QComboBox()
        self.combo_response.addItems(['Butterworth', 'Chebyshev', 'Bessel'])
        type_layout.addWidget(self.combo_response, 1, 1)

        type_layout.addWidget(QLabel('Order:'), 2, 0)
        self.spin_order = QSpinBox()
        self.spin_order.setRange(1, 9)
        self.spin_order.setValue(3)
        type_layout.addWidget(self.spin_order, 2, 1)
        left_layout.addWidget(type_group)

        # Frequency group
        freq_group = QGroupBox('Frequency')
        freq_group.setStyleSheet('QGroupBox { color: white; }')
        freq_layout = QGridLayout(freq_group)

        self.label_fc = QLabel('Cutoff (MHz):')
        freq_layout.addWidget(self.label_fc, 0, 0)
        self.spin_fc = QDoubleSpinBox()
        self.spin_fc.setRange(0.1, 100000)
        self.spin_fc.setValue(915)
        self.spin_fc.setDecimals(1)
        freq_layout.addWidget(self.spin_fc, 0, 1)

        self.label_bw = QLabel('Bandwidth (MHz):')
        freq_layout.addWidget(self.label_bw, 1, 0)
        self.spin_bw = QDoubleSpinBox()
        self.spin_bw.setRange(0.1, 10000)
        self.spin_bw.setValue(50)
        self.spin_bw.setDecimals(1)
        freq_layout.addWidget(self.spin_bw, 1, 1)
        left_layout.addWidget(freq_group)

        # Impedance group
        imp_group = QGroupBox('Impedance')
        imp_group.setStyleSheet('QGroupBox { color: white; }')
        imp_layout = QGridLayout(imp_group)

        imp_layout.addWidget(QLabel('Z0 (ohm):'), 0, 0)
        self.spin_z0 = QDoubleSpinBox()
        self.spin_z0.setRange(1, 1000)
        self.spin_z0.setValue(50)
        self.spin_z0.setDecimals(1)
        imp_layout.addWidget(self.spin_z0, 0, 1)
        left_layout.addWidget(imp_group)

        # Design button
        self.btn_design = QPushButton('Design Filter')
        self.btn_design.setFixedHeight(40)
        self.btn_design.setStyleSheet('''
            QPushButton { background-color: #00aaff; color: black; font-weight: bold; font-size: 13px; border-radius: 5px; }
            QPushButton:hover { background-color: #33bbff; }
            QPushButton:pressed { background-color: #0088cc; }
        ''')
        self.btn_design.clicked.connect(self._on_design_clicked)
        left_layout.addWidget(self.btn_design)

        # Component values table
        table_label = QLabel('Component Values')
        table_label.setStyleSheet('color: white; font-weight: bold;')
        left_layout.addWidget(table_label)

        self.table = QTableWidget()
        self.table.setColumnCount(3)
        self.table.setHorizontalHeaderLabels(['Label', 'Ideal', 'Standard'])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet('''
            QTableWidget { background-color: #2a2a2a; color: white; gridline-color: #444444; }
            QHeaderView::section { background-color: #333333; color: white; padding: 4px; }
        ''')
        self.table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        left_layout.addWidget(self.table)

        # Export netlist button
        self.btn_export = QPushButton('Download LTspice Netlist')
        self.btn_export.setFixedHeight(35)
        self.btn_export.setStyleSheet('''
            QPushButton { background-color: #2a2a2a; color: #00ff99; font-weight: bold; border: 1px solid #00ff99; border-radius: 5px; }
            QPushButton:hover { background-color: #003322; }
            QPushButton:disabled { color: #555555; border-color: #555555; }
        ''')
        self.btn_export.setEnabled(False)
        self.btn_export.clicked.connect(self._on_export_clicked)
        left_layout.addWidget(self.btn_export)

        # Schematic button
        self.btn_schematic = QPushButton('Show Schematic')
        self.btn_schematic.setFixedHeight(35)
        self.btn_schematic.setStyleSheet('''
            QPushButton { background-color: #2a2a2a; color: #ffaa00; font-weight: bold; border: 1px solid #ffaa00; border-radius: 5px; }
            QPushButton:hover { background-color: #332200; }
            QPushButton:disabled { color: #555555; border-color: #555555; }
        ''')
        self.btn_schematic.setEnabled(False)
        self.btn_schematic.clicked.connect(self._on_schematic_clicked)
        left_layout.addWidget(self.btn_schematic)

        left_layout.addStretch()

        # Right panel with the S21 plot
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        right_layout.setContentsMargins(0, 0, 0, 0)
        self.canvas = PlotCanvas(self)
        right_layout.addWidget(self.canvas)

        top_layout.addWidget(left_panel)
        top_layout.addWidget(right_panel)

        self._on_topology_changed('Low-Pass')

    def _on_topology_changed(self, topology):
        is_bandpass = (topology == 'Band-Pass')
        self.label_bw.setVisible(is_bandpass)
        self.spin_bw.setVisible(is_bandpass)

        if is_bandpass:
            self.label_fc.setText('Center (MHz):')
        else:
            self.label_fc.setText('Cutoff (MHz):')

    def _on_design_clicked(self):
        # Read parameters from controls
        topology = self.combo_topology.currentText()
        response_type = self.combo_response.currentText().lower()
        order = self.spin_order.value()
        fc = self.spin_fc.value() * 1e6  # convert MHz to Hz
        bw = self.spin_bw.value() * 1e6
        Z0 = self.spin_z0.value()

        # Run the appropriate design function
        try:
            if topology == 'Low-Pass':
                components = design_lowpass(response_type, order, fc, Z0)
            elif topology == 'High-Pass':
                components = design_highpass(response_type, order, fc, Z0)
            elif topology == 'Band-Pass':
                components = design_bandpass(response_type, order, fc, bw, Z0)
        except ValueError as e:
            self.table.setRowCount(1)
            self.table.setItem(0, 0, QTableWidgetItem(str(e)))
            return

        self.current_components = components
        self.canvas.clear()

        # Set simulation range: 1 decade below to 1 decade above cutoff
        f_start = fc / 20
        f_stop = fc * 20

        plot_response(self.canvas.ax, components,
                      f_start, f_stop, Z0,
                      label=f'{topology} {response_type.capitalize()} n={order}',
                      color='#00aaff')

        self.canvas.ax.axhline(y=-3, color='red', linestyle='--', linewidth=1, alpha=0.8, label='-3 dB')
        self.canvas.ax.axvline(x=fc / 1e6, color='yellow', linestyle=':', linewidth=1, alpha=0.8)
        self.canvas.ax.text(fc / 1e6, -75, f'{fc / 1e6:.1f} MHz', color='yellow', fontsize=8, ha='center', va='bottom')

        # Add legend
        legend = self.canvas.ax.legend(fontsize=9)
        legend.get_frame().set_facecolor('#2e2e2e')
        legend.get_frame().set_edgecolor('#444444')
        for text in legend.get_texts():
            text.set_color('white')

        self.canvas.draw()

        # --- Populate the component table
        self._update_table(components)

        # --- Enable the export button now that we have a design
        self.btn_export.setEnabled(True)
        self.btn_schematic.setEnabled(True)

    def _on_schematic_clicked(self):
        from schematic.draw import draw_schematic
        topology = self.combo_topology.currentText()
        response_type = self.combo_response.currentText()
        order = self.spin_order.value()
        fc = self.spin_fc.value()
        title = f'{topology} {response_type} n={order} @ {fc:.1f} MHz'
        draw_schematic(self.current_components, title)

    def _update_table(self, components):
        self.table.setRowCount(len(components))

        for row, comp in enumerate(components):
            # Format value with appropriate unit
            if comp['type'] == 'L':
                ideal_str = f"{comp['ideal'] * 1e9:.3f} nH"
                standard_str = f"{comp['standard'] * 1e9:.3f} nH"
            else:
                ideal_str = f"{comp['ideal'] * 1e12:.3f} pF"
                standard_str = f"{comp['standard'] * 1e12:.3f} pF"

            self.table.setItem(row, 0, QTableWidgetItem(comp['label']))
            self.table.setItem(row, 1, QTableWidgetItem(ideal_str))
            self.table.setItem(row, 2, QTableWidgetItem(standard_str))

            # Colour inductors and capacitors differently for readability
            color = QColor('#1a3a5c') if comp['type'] == 'L' else QColor('#1a3a2a')
            for col in range(3):
                self.table.item(row, col).setBackground(color)

    def _on_export_clicked(self):
        from PyQt6.QtWidgets import QFileDialog, QMessageBox
        from export.ltspice import save_netlist
        import os

        if not self.current_components:
            return

        topology      = self.combo_topology.currentText()
        response_type = self.combo_response.currentText()
        order         = self.spin_order.value()
        fc            = self.spin_fc.value()
        Z0            = self.spin_z0.value()

        # Build descriptive default filename from filter parameters
        topology_short = {'Low-Pass': 'LP', 'High-Pass': 'HP', 'Band-Pass': 'BP'}
        default_name   = (f"{topology_short[topology]}_"
                          f"{response_type}_"
                          f"{order}_"
                          f"{fc:.0f}MHz.net")

        # Open in last used directory, or home folder on first use
        start_dir    = getattr(self, '_last_save_dir', os.path.expanduser('~'))
        default_path = os.path.join(start_dir, default_name)

        filename, _ = QFileDialog.getSaveFileName(
            self,
            'Save LTspice Netlist',
            default_path,
            'LTspice Netlist (*.net);;All Files (*)'
        )

        if not filename:
            return

        # Remember this folder for next time
        self._last_save_dir = os.path.dirname(filename)

        try:
            # ltspice.py handles all netlist generation
            save_netlist(filename, self.current_components,
                         topology, response_type, order, fc, Z0)

            QMessageBox.information(
                self,
                'Export Successful',
                f'Netlist saved to:\n{filename}\n\n'
                f'Open in LTspice and run the .ac simulation\n'
                f'to verify the frequency response.'
            )

        except Exception as e:
            QMessageBox.critical(self, 'Export Failed',
                                 f'Could not save file:\n{str(e)}')

def run():
    app = QApplication(sys.argv)

    # Dark theme for the whole application
    app.setStyleSheet('''
        QWidget {
            background-color: #1e1e1e;
            color: white;
        }
        QGroupBox {
            border: 1px solid #444444;
            border-radius: 4px;
            margin-top: 8px;
            padding-top: 8px;
        }
        QGroupBox::title {
            subcontrol-origin: margin;
            left: 8px;
        }
        QComboBox, QSpinBox, QDoubleSpinBox {
            background-color: #2a2a2a;
            color: white;
            border: 1px solid #444444;
            padding: 3px;
            border-radius: 3px;
        }
        QLabel {
            color: #cccccc;
        }
    ''')

    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    run()