import sys
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout, QLineEdit, QLabel, QPushButton, QGroupBox, QGridLayout, QTextEdit, QFileDialog, QComboBox)
from fpdf import FPDF
import tempfile  # Added this import
import os  # Also add os if it isn't already imported for file removal
from PIL import Image  # Ensure this is imported for loading image dimensions

# Define concrete strength classes as per Eurocode 2
CONCRETE_CLASSES = {
    1: 'C12/15', 2: 'C16/20', 3: 'C20/25', 4: 'C25/30',
    5: 'C30/37', 6: 'C32/40', 7: 'C35/45', 8: 'C40/50',
    9: 'C45/55', 10: 'C50/60', 11: 'C55/67', 12: 'C60/75'
}
CONCRETE_STRENGTHS = {
    'C12/15': 12, 'C16/20': 16, 'C20/25': 20, 'C25/30': 25,
    'C30/37': 30, 'C32/40': 32, 'C35/45': 35, 'C40/50': 40,
    'C45/55': 45, 'C50/60': 50, 'C55/67': 55, 'C60/75': 60
}

# Modulus of Elasticity for Reinforcement (Default = 200 kN/mm²)
E_s = 200 * 1e3

class RCBeamDesignApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        main_layout = QVBoxLayout()

        # Top left: Diagram of the rectangular section
        top_layout = QHBoxLayout()
        self.section_figure = plt.figure(figsize=(4, 4))  # Adjusted figure size
        self.section_canvas = FigureCanvas(self.section_figure)
        self.section_canvas.setMinimumWidth(300)  # Add minimum width
        top_layout.addWidget(self.section_canvas)

        # Material and Section Details next to the diagram
        details_layout = QHBoxLayout()

        # Material Details
        material_group_box = QGroupBox("Material Details Input")
        material_form_layout = QFormLayout()
        self.concrete_class_input = QComboBox()
        self.concrete_class_input.addItems(list(CONCRETE_CLASSES.values()))
        self.concrete_class_input.setMaximumWidth(150)
        self.f_yk_main_input = QLineEdit('500')
        self.f_yk_shear_input = QLineEdit('500')
        self.gamma_c_input = QLineEdit('1.5')
        self.alpha_cc_input = QLineEdit('0.85')
        self.gamma_s_input = QLineEdit('1.15')
        material_form_layout.addRow(QLabel('Concrete Class:'), self.create_input_with_unit(self.concrete_class_input, ''))
        material_form_layout.addRow(QLabel('Main Reinforcement Strength:'), self.create_input_with_unit(self.f_yk_main_input, 'N/mm²'))
        material_form_layout.addRow(QLabel('Shear Reinforcement Strength:'), self.create_input_with_unit(self.f_yk_shear_input, 'N/mm²'))
        material_form_layout.addRow(QLabel('Partial Factor for Concrete (γ_c):'), self.create_input_with_unit(self.gamma_c_input, ''))
        material_form_layout.addRow(QLabel('Compressive Strength Coefficient (α_cc):'), self.create_input_with_unit(self.alpha_cc_input, ''))
        material_form_layout.addRow(QLabel('Partial Factor for Steel (γ_s):'), self.create_input_with_unit(self.gamma_s_input, ''))
        material_group_box.setLayout(material_form_layout)
        details_layout.addWidget(material_group_box)

        # Section Details
        section_group_box = QGroupBox("Section Details Input")
        section_form_layout = QFormLayout()
        self.min_cover_input = QLineEdit('30')
        self.cover_dev_input = QLineEdit('10')
        self.section_depth_input = QLineEdit('500')
        self.section_width_input = QLineEdit('300')
        self.rdp_input = QLineEdit('15')
        section_form_layout.addRow(QLabel('Minimum Cover:'), self.create_input_with_unit(self.min_cover_input, 'mm'))
        section_form_layout.addRow(QLabel('Cover Deviation:'), self.create_input_with_unit(self.cover_dev_input, 'mm'))
        section_form_layout.addRow(QLabel('Section Depth:'), self.create_input_with_unit(self.section_depth_input, 'mm'))
        section_form_layout.addRow(QLabel('Section Width:'), self.create_input_with_unit(self.section_width_input, 'mm'))
        section_form_layout.addRow(QLabel('Redistribution Percentage:'), self.create_input_with_unit(self.rdp_input, '%'))
        section_group_box.setLayout(section_form_layout)
        details_layout.addWidget(section_group_box)

        # Design Loading Details
        design_load_group_box = QGroupBox("Design Loading Input")
        design_load_form_layout = QFormLayout()
        self.sls_m_ed_input = QLineEdit('0')
        self.uls_m_ed_input = QLineEdit('500')
        self.v_ed_input = QLineEdit('0')
        self.v_ef_input = QLineEdit('0')
        self.t_ed_input = QLineEdit('0')
        self.t_ef_input = QLineEdit('0')
        design_load_form_layout.addRow(QLabel('SLS M_Ed:'), self.create_input_with_unit(self.sls_m_ed_input, 'kNm'))
        design_load_form_layout.addRow(QLabel('ULS M_Ed:'), self.create_input_with_unit(self.uls_m_ed_input, 'kNm'))
        design_load_form_layout.addRow(QLabel('V_Ed:'), self.create_input_with_unit(self.v_ed_input, 'kN'))
        design_load_form_layout.addRow(QLabel('V_Ef:'), self.create_input_with_unit(self.v_ef_input, 'kN'))
        design_load_form_layout.addRow(QLabel('T_Ed:'), self.create_input_with_unit(self.t_ed_input, 'kN'))
        design_load_form_layout.addRow(QLabel('T_Ef:'), self.create_input_with_unit(self.t_ef_input, 'kN'))
        design_load_group_box.setLayout(design_load_form_layout)
        details_layout.addWidget(design_load_group_box)

        top_layout.addLayout(details_layout)
        main_layout.addLayout(top_layout)

        # Row 3: Reinforcement and Shear Reinforcement Details
        reinforcement_layout = QHBoxLayout()

        # Tension Reinforcement Details
        tension_group_box = QGroupBox("Tension Reinforcement Details Input")
        tension_form_layout = QGridLayout()
        tension_form_layout.addWidget(QLabel("Layer"), 0, 0)
        tension_form_layout.addWidget(QLabel("Diameter"), 0, 1)
        tension_form_layout.addWidget(QLabel("Number of Bars"), 0, 2)

        self.tension_layers_input = []
        for i in range(1, 7):
            tension_form_layout.addWidget(QLabel(f"Layer {i}"), i, 0)
            tension_diameter_input = QComboBox()
            tension_diameter_input.addItems([""])
            tension_diameter_input.addItems(['10', '12', '13', '16', '20', '25', '32', '40', '55'])
            tension_diameter_input.setFixedWidth(60)  # Set width to match existing input field size
            tension_number_input = QLineEdit('')
            tension_number_input.setFixedWidth(60)  # Set width to match existing input field size
            tension_form_layout.addWidget(tension_diameter_input, i, 1)
            tension_form_layout.addWidget(tension_number_input, i, 2)
            self.tension_layers_input.append((tension_diameter_input, tension_number_input))

        tension_group_box.setLayout(tension_form_layout)
        reinforcement_layout.addWidget(tension_group_box)

        # Compression Reinforcement Details
        compression_group_box = QGroupBox("Compression Reinforcement Details Input")
        compression_form_layout = QGridLayout()
        compression_form_layout.addWidget(QLabel("Layer"), 0, 0)
        compression_form_layout.addWidget(QLabel("Diameter"), 0, 1)
        compression_form_layout.addWidget(QLabel("Number of Bars"), 0, 2)

        self.compression_layers_input = []
        for i in range(1, 7):
            compression_form_layout.addWidget(QLabel(f"Layer {i}"), i, 0)
            compression_diameter_input = QComboBox()
            compression_diameter_input.addItems([""])
            compression_diameter_input.addItems(['10', '12', '13', '16', '20', '25', '32', '40', '55'])
            compression_diameter_input.setFixedWidth(60)  # Set width to match existing input field size
            compression_number_input = QLineEdit('')
            compression_number_input.setFixedWidth(60)  # Set width to match existing input field size
            compression_form_layout.addWidget(compression_diameter_input, i, 1)
            compression_form_layout.addWidget(compression_number_input, i, 2)
            self.compression_layers_input.append((compression_diameter_input, compression_number_input))

        compression_group_box.setLayout(compression_form_layout)
        reinforcement_layout.addWidget(compression_group_box)

        # Shear Reinforcement Details
        shear_group_box = QGroupBox("Shear Reinforcement Details Input")
        shear_form_layout = QFormLayout()
        self.d_w_input = QComboBox()
        self.d_w_input.addItem("")  # Add an empty item as the default selection
        self.d_w_input.addItems(['6', '8', '10', '12', '13', '16', '20', '25'])
        self.d_w_input.setFixedWidth(60)  # Set width to match existing input field size
        self.n_l_input = QLineEdit('2')
        self.s_input = QLineEdit('150')

        shear_form_layout.addRow(QLabel('Shear Reinforcement Diameter:'), self.create_input_with_unit(self.d_w_input, 'mm'))
        shear_form_layout.addRow(QLabel('Number of Legs:'), self.create_input_with_unit(self.n_l_input, ''))
        shear_form_layout.addRow(QLabel('Spacing:'), self.create_input_with_unit(self.s_input, 'mm'))
        shear_group_box.setLayout(shear_form_layout)
        reinforcement_layout.addWidget(shear_group_box)

        main_layout.addLayout(reinforcement_layout)

        # Row 4: Calculate and Save PDF Buttons
        buttons_layout = QHBoxLayout()
        self.calculate_button = QPushButton('Calculate')
        self.calculate_button.clicked.connect(self.calculate)
        buttons_layout.addWidget(self.calculate_button)

        self.save_pdf_button = QPushButton('Save PDF')
        self.save_pdf_button.clicked.connect(self.save_pdf)
        buttons_layout.addWidget(self.save_pdf_button)
        main_layout.addLayout(buttons_layout)

        # Row 5: Output Screen
        self.result_display = QTextEdit()
        self.result_display.setReadOnly(True)
        main_layout.addWidget(self.result_display)

        self.setLayout(main_layout)
        self.setWindowTitle("RC Beam Design Input")
        self.setGeometry(100, 100, 1200, 800)

    def create_input_with_unit(self, input_field, unit):
        layout = QHBoxLayout()
        layout.addWidget(input_field)
        layout.addWidget(QLabel(unit))
        container = QWidget()
        container.setLayout(layout)
        return container


    def calculate(self):
        try:
            # Get input values from the UI
            f_ck = CONCRETE_STRENGTHS[self.concrete_class_input.currentText()]  # Get concrete class directly from ComboBox
            f_yk_main = float(self.f_yk_main_input.text())
            f_yk_shear = float(self.f_yk_shear_input.text())
            gamma_c = float(self.gamma_c_input.text())
            alpha_cc = float(self.alpha_cc_input.text())
            gamma_s = float(self.gamma_s_input.text())
            min_cover = float(self.min_cover_input.text())
            cover_dev = float(self.cover_dev_input.text())
            c_nom = min_cover + cover_dev
            h = float(self.section_depth_input.text())
            b = float(self.section_width_input.text())

            # Get shear reinforcement diameter from ComboBox (can be empty or zero)
            d_w = float(self.d_w_input.currentText()) if self.d_w_input.currentText() else 0

            # Validation for the first layer of tension reinforcement
            first_tension_diameter_input, first_tension_number_input = self.tension_layers_input[0]

            if not first_tension_diameter_input.currentText() or not first_tension_number_input.text():
                raise ValueError("Please provide tension reinforcement diameter & number of bars.")

            try:
                first_layer_diameter = float(first_tension_diameter_input.currentText())
                first_layer_number = int(first_tension_number_input.text())
            except ValueError:
                raise ValueError("Please provide valid numeric values for tension reinforcement diameter & number of bars.")

            # Continue processing other tension and compression layers
            reinforcement_layers = {'tension': [], 'compression': []}
            for diameter_input, number_input in self.tension_layers_input:
                if not diameter_input.currentText() or not number_input.text():
                    continue
                try:
                    d_s = float(diameter_input.currentText())  # Get diameter from ComboBox
                    n_s = int(number_input.text())
                    if d_s > 0 and n_s > 0:
                        A_s = math.pi * (d_s ** 2) * 0.25 * n_s
                        reinforcement_layers['tension'].append((d_s, A_s))
                except ValueError:
                    continue

            for diameter_input, number_input in self.compression_layers_input:
                if not diameter_input.currentText() or not number_input.text():
                    continue
                try:
                    d_sc = float(diameter_input.currentText())  # Get diameter from ComboBox
                    n_sc = int(number_input.text())
                    if d_sc > 0 and n_sc > 0:
                        A_sc = math.pi * (d_sc ** 2) * 0.25 * n_sc
                        reinforcement_layers['compression'].append((d_sc, A_sc))
                except ValueError:
                    continue

            # Total area of tension reinforcement
            A_s_total = sum(A_s for _, A_s in reinforcement_layers['tension'])
            if A_s_total == 0:
                raise ValueError("Total tension reinforcement area is zero. Please provide valid tension reinforcement data.")

            y_t = 0
            # Corrected Centroid Calculation for Tension Reinforcement Layers
            for i, (d_s, A_s) in enumerate(reinforcement_layers['tension']):
                if i == 0:
                    layer_depth = d_s * 0.5
                else:
                    previous_layers_depth = sum(
                        (reinforcement_layers['tension'][j][0] + max(25, reinforcement_layers['tension'][j][0]))
                        for j in range(i)
                    )
                    layer_depth = previous_layers_depth + (d_s * 0.5)
                y_t += A_s * layer_depth

            y_t /= A_s_total

            # Total area of compression reinforcement
            A_sc_total = sum(A_sc for _, A_sc in reinforcement_layers['compression'])
            y_c = 0
            if A_sc_total > 0:
                # Corrected Centroid Calculation for Compression Reinforcement Layers
                for i, (d_sc, A_sc) in enumerate(reinforcement_layers['compression']):
                    if i == 0:
                        layer_depth = d_sc * 0.5
                    else:
                        previous_layers_depth = sum(
                            (reinforcement_layers['compression'][j][0] + max(25, reinforcement_layers['compression'][j][0]))
                            for j in range(i)
                        )
                        layer_depth = previous_layers_depth + (d_sc * 0.5)
                    y_c += A_sc * layer_depth

                y_c /= A_sc_total

            d_eff = h - c_nom - d_w - y_t
            dc_eff = c_nom + d_w + y_c

            # Redistribution
            rdp = float(self.rdp_input.text())  # Get Redistribution Percentage from user input

            mr = 1 - (rdp / 100)

            # K calculations
            K_bal = 0.453 * (mr - 0.4) * (1 - 0.4 * (mr - 0.4))
            M_Ed = float(self.uls_m_ed_input.text()) * 1e6  # Get ULS M_Ed value from user input (converted to Nmm)

            K = M_Ed / (b * d_eff ** 2 * f_ck)

            if K <= K_bal:
                # Singly reinforced
                section_type = "Singly Reinforced Section"
                # Calculate lever arm 'z_m'
                if (0.25 - 0.881 * K) < 0:
                    # If the value inside the square root is negative, use 0.95 * d_eff
                    z_m = 0.95 * d_eff
                else:
                    z_m = min(((0.5 + (0.25 - 0.881 * K) ** 0.5) * d_eff), 0.95 * d_eff)
                A_s_min = 0.001572 * b * d_eff
                A_s_req = max(M_Ed / (z_m * (f_yk_main / gamma_s)), A_s_min)
                A_sc_req = 0  # No compression reinforcement required
                compression_utilisation_ratio = None  # No compression reinforcement needed
            else:
                # Doubly reinforced
                section_type = "Doubly Reinforced Section"
                z_m = d_eff * 0.82
                A_sc_req = ((K - K_bal) * f_ck * b * d_eff ** 2) / ((f_yk_main / gamma_s) * (d_eff - dc_eff))
                A_s_req = ((K_bal * f_ck * b * d_eff ** 2) / (z_m * (f_yk_main / gamma_s))) + A_sc_req
                compression_utilisation_ratio = A_sc_req / A_sc_total if A_sc_total > 0 else None

            # Minimum and Maximum Reinforcement Check
            A_s_min_check = 0.001572 * b * d_eff
            A_s_max = 0.04 * b * h

            A_s_req = max(A_s_req, A_s_min_check)
            A_s_req = min(A_s_req, A_s_max)

            # Design Summary
            output_text = [f"<b><u>Design Summary</u></b>\n"]
            output_text.append(f"Section Type = {section_type}\n")
            tension_utilisation_ratio = A_s_req / A_s_total if A_s_total > 0 else 0
            if tension_utilisation_ratio > 1:
                output_text.append(f"<span style='color:red;'>Tension Reinforcement Utilisation Ratio = {tension_utilisation_ratio:.3f} > 1 ; Fail</span>\n")
            else:
                output_text.append(f"<span style='color:green;'>Tension Reinforcement Utilisation Ratio = {tension_utilisation_ratio:.3f} < 1 ; Pass</span>\n")

            if section_type == "Doubly Reinforced Section":
                if A_sc_req > 0 and A_sc_total == 0:
                    output_text.append(f"<span style='color:red;'>Compression Reinforcement not provided ; Fail</span>")
                elif compression_utilisation_ratio is not None:
                    if compression_utilisation_ratio > 1:
                        output_text.append(f"<span style='color:red;'>Compression Reinforcement Utilisation Ratio = {compression_utilisation_ratio:.3f} > 1 ; Fail</span>")
                    else:
                        output_text.append(f"<span style='color:green;'>Compression Reinforcement Utilisation Ratio = {compression_utilisation_ratio:.3f} < 1 ; Pass</span>")

            # Add original details to output, each on a new line
            output_text += [
                "<br><b><u>Material and Section Details</u></b>\n",
                f"Concrete strength (f_ck) = {f_ck:.3f} N/mm²\n",
                f"Main reinforcement strength (f_yk_main) = {f_yk_main:.3f} N/mm²\n",
                f"Shear reinforcement strength (f_yk_shear) = {f_yk_shear:.3f} N/mm²\n",
                f"Partial factor for concrete (gamma_c) = {gamma_c:.3f}\n",
                f"Compressive strength coefficient (alpha_cc) = {alpha_cc:.3f}\n",
                f"Partial factor for steel (gamma_s) = {gamma_s:.3f}\n\n",

                "<br><b><u>Calculated Design Strengths</u></b>\n",
                f"Design strength of main reinforcement (f_yd_main) = {f_yk_main / gamma_s:.3f} N/mm²\n",
                f"Design strength of shear reinforcement (f_yd_shear) = {f_yk_shear / gamma_s:.3f} N/mm²\n",

                "<br><b><u>Section Details</u></b>\n",
                f"Nominal cover (c_nom) = {c_nom:.3f} mm\n",
                f"Section depth (h) = {h:.3f} mm\n",
                f"Section width (b) = {b:.3f} mm\n\n",

                "<br><b><u>Reinforcement Details</u></b>\n",
                f"Total area of tension reinforcement (A_s_pro) = {A_s_total:.2f} mm²\n",
                f"Total area of compression reinforcement (A_sc_pro) = {A_sc_total:.2f} mm²\n",

                "<br><b><u>Effective Depth Values</u></b>\n",
                f"Distance from centroid to tension reinforcement layer (y_t) = {y_t:.2f} mm\n",
                f"Distance from centroid to compression reinforcement layer (y_c) = {y_c:.2f} mm\n",
                f"Effective Depth to tension reinforcement (d_eff) = {d_eff:.2f} mm\n",
                f"Effective Depth to compression reinforcement (dc_eff) = {dc_eff:.2f} mm\n",
            ]

            # Bending Design Results
            output_text.append("<br><b><u>Bending Design Results</u></b>\n")
            output_text.append(f"Section Type = {section_type}\n")
            output_text.append(f"A_s_Pro = {A_s_total:.3f} mm²\n")
            output_text.append(f"A_s_req = {A_s_req:.3f} mm²\n")

            if tension_utilisation_ratio >= 1:
                output_text.append(f"<span style='color:red;'>A_s_req / A_s_Pro = {tension_utilisation_ratio:.3f} >= 1 ; Fail</span>\n")
            else:
                output_text.append(f"<span style='color:green;'>A_s_req / A_s_Pro = {tension_utilisation_ratio:.3f} < 1 ; Pass</span>\n")

            if section_type == "Doubly Reinforced Section":
                if A_sc_req > 0 and A_sc_total == 0:
                    output_text.append(f"<span style='color:red;'>Compression Reinforcement not provided ; Fail</span>\n")
                elif A_sc_req > 0:
                    output_text.append(f"A_sc_Pro = {A_sc_total:.3f} mm²\n")
                    output_text.append(f"A_sc_req = {A_sc_req:.3f} mm²\n")

                    if compression_utilisation_ratio is not None:
                        if compression_utilisation_ratio >= 1:
                            output_text.append(f"<span style='color:red;'>A_sc_req / A_sc_Pro = {compression_utilisation_ratio:.3f} >= 1 ; Fail</span>\n")
                        else:
                            output_text.append(f"<span style='color:green;'>A_sc_req / A_sc_Pro = {compression_utilisation_ratio:.3f} <= 1 ; Pass</span>\n")

            # Display calculation results in HTML format, with each line on a new line
            self.result_display.setHtml('<br>'.join(output_text))

            # Update the diagram
            self.plot_section_diagram(c_nom, b, h, reinforcement_layers, d_w)

        except Exception as e:
            self.result_display.setText(f"Error: {str(e)}")



        except Exception as e:
            self.result_display.setText(f"Unexpected error: {str(e)}")




    def plot_section_diagram(self, c_nom, b, h, reinforcement_layers, d_w):
        self.section_figure.clear()
        ax = self.section_figure.add_subplot(111)
        ax.add_patch(Rectangle((0, 0), b, h, fill=True, facecolor='lightblue', edgecolor='blue'))

        # Draw Shear Link (Rectangular shape with rounded corners)
        ax.add_patch(Rectangle((c_nom, c_nom), b - 2 * c_nom, h - 2 * c_nom,
                               fill=False, edgecolor='red', linewidth=d_w / 10))

        # Draw Tension Reinforcement
        y_offset_tension = c_nom + d_w  # Initial offset from bottom
        for i, (d_s, A_s) in enumerate(reinforcement_layers['tension']):
            if i > 0:
                # Add previous layer diameter and spacing
                previous_diameter = reinforcement_layers['tension'][i - 1][0]
                y_offset_tension += previous_diameter + max(25, previous_diameter)

            y_position = y_offset_tension + d_s * 0.5
            n_bars = int(A_s / (math.pi * (d_s ** 2) * 0.25))

            # Calculate spacing between bars
            spacing = (b - 2 * (c_nom + d_w + d_s * 0.5)) / (n_bars - 1) if n_bars > 1 else 0

            for j in range(n_bars):
                x_position = c_nom + d_w + d_s * 0.5 + j * spacing
                ax.add_patch(Circle((x_position, y_position), d_s * 0.5, color='black'))

        # Draw Compression Reinforcement
        y_offset_compression = c_nom + d_w  # Initial offset from top
        for i, (d_sc, A_sc) in enumerate(reinforcement_layers['compression']):
            if i > 0:
                # Add previous layer diameter and spacing
                previous_diameter = reinforcement_layers['compression'][i - 1][0]
                y_offset_compression += previous_diameter + max(25, previous_diameter)

            y_position = h - (y_offset_compression + d_sc * 0.5)
            n_bars = int(A_sc / (math.pi * (d_sc ** 2) * 0.25))

            # Calculate spacing between bars
            spacing = (b - 2 * (c_nom + d_w + d_sc * 0.5)) / (n_bars - 1) if n_bars > 1 else 0

            for j in range(n_bars):
                x_position = c_nom + d_w + d_sc * 0.5 + j * spacing
                ax.add_patch(Circle((x_position, y_position), d_sc * 0.5, color='black'))


        ax.set_xlim(-10, b + 10)
        ax.set_ylim(-10, h + 10)
        ax.set_aspect('equal')
        ax.axis('off')
        self.section_canvas.draw()


    def save_pdf(self):
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        file_dialog.setDefaultSuffix("pdf")
        file_path, _ = file_dialog.getSaveFileName(self, "Save PDF", "output.pdf", "PDF Files (*.pdf);;All Files (*)")

        if file_path:
            try:
                # Save the figure to a temporary file
                with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as temp_file:
                    temp_filename = temp_file.name
                    self.section_figure.savefig(temp_filename)

                # Create PDF and add figure and text content
                pdf = FPDF()
                pdf.add_page()
                pdf.set_font("Arial", size=12)

                # Add figure to the PDF before the output text
                pdf_height = pdf.h - 20  # Page height with padding
                max_img_height = pdf_height * 0.3  # Image height limited to 30% of the page height
                max_img_width = pdf.w - 20  # Allow padding on both sides

                # Get figure dimensions from matplotlib directly
                width, height = self.section_figure.get_size_inches() * self.section_figure.dpi

                # Calculate scaling factor to maintain aspect ratio
                scale_factor = min(max_img_height / height, max_img_width / width)
                img_width_scaled = width * scale_factor
                img_height_scaled = height * scale_factor

                # Calculate X coordinate to center the image
                x_position = (pdf.w - img_width_scaled) / 2

                # Insert the image into the PDF centered
                pdf.image(temp_filename, x=x_position, y=10, w=img_width_scaled, h=img_height_scaled)

                # Adjust text start position to avoid overlapping with image
                pdf.set_y(10 + img_height_scaled + 10)

                # Add calculation results text to the PDF
                for line in self.result_display.toPlainText().split('\n'):
                    pdf.multi_cell(0, 10, txt=line)

                # Output the final PDF
                pdf.output(file_path)

                # Remove the temporary file after saving the PDF
                os.unlink(temp_filename)

                # Show success message in the output window
                current_text = self.result_display.toPlainText()
                self.result_display.setText(f"{current_text}\n\nFile saved successfully at: {file_path}")

            except Exception as e:
                current_text = self.result_display.toPlainText()
                self.result_display.setText(f"{current_text}\n\nError saving PDF: {str(e)}")



if __name__ == "__main__":
    app = QApplication(sys.argv)
    rc_beam_app = RCBeamDesignApp()
    rc_beam_app.show()
    sys.exit(app.exec_())
