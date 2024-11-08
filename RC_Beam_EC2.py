import math

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

# Secant Modulus of Elasticity of Concrete (Table 3.1 in EC2)
def calculate_e_cm(f_ck):
    return 22 * (f_ck / 10)**0.3 * 1e3  # in kN/mm²

def get_material_details():
    print("Choose the Concrete Strength Class:")
    for num, class_name in CONCRETE_CLASSES.items():
        print(f"{num}. {class_name}")
    while True:
        try:
            concrete_choice = input("Enter the number for the desired concrete class: ")
            if concrete_choice == '':
                raise ValueError("This concrete strength class is required for the calculation. Please enter a value.")
            concrete_choice = int(concrete_choice)
            if concrete_choice not in CONCRETE_CLASSES:
                raise ValueError("Invalid choice. Please choose a valid concrete class.")
            break
        except ValueError as e:
            print(f"Error: {e}")
    f_ck = CONCRETE_STRENGTHS[CONCRETE_CLASSES[concrete_choice]]

    while True:
        try:
            f_yk_main = input("Enter Main Reinforcement Strength (N/mm²) [Default = 500]: ")
            if f_yk_main == '':
                f_yk_main = 500
            else:
                f_yk_main = float(f_yk_main)
            if f_yk_main <= 0:
                raise ValueError("Reinforcement strength must be positive.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Main Reinforcement Strength in numerical type..!")

    while True:
        try:
            f_yk_shear = input("Enter Shear Reinforcement Strength (N/mm²) [Default = 500]: ")
            if f_yk_shear == '':
                f_yk_shear = 500
            else:
                f_yk_shear = float(f_yk_shear)
            if f_yk_shear <= 0:
                raise ValueError("Shear reinforcement strength must be positive.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Shear Reinforcement Strength in numerical type..!")

    while True:
        try:
            gamma_c = input("Enter Partial Factor for Concrete γ_c [Default = 1.5]: ")
            if gamma_c == '':
                gamma_c = 1.5
            else:
                gamma_c = float(gamma_c)
            if gamma_c <= 0:
                raise ValueError("Partial factor for concrete must be positive.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Partial Factor for Concrete in numerical type..!")

    while True:
        try:
            alpha_cc = input("Enter Compressive Strength Coefficient α_cc [Default = 0.85]: ")
            if alpha_cc == '':
                alpha_cc = 0.85
            else:
                alpha_cc = float(alpha_cc)
            if alpha_cc <= 0 or alpha_cc > 1:
                raise ValueError("Compressive strength coefficient must be between 0 and 1.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Compressive Strength Coefficient in numerical type between 0 and 1..!")

    while True:
        try:
            gamma_s = input("Enter Partial Factor for Steel γ_s [Default = 1.15]: ")
            if gamma_s == '':
                gamma_s = 1.15
            else:
                gamma_s = float(gamma_s)
            if gamma_s <= 0:
                raise ValueError("Partial factor for steel must be positive.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Partial Factor for Steel in numerical type..!")

    return f_ck, f_yk_main, f_yk_shear, gamma_c, alpha_cc, gamma_s

def get_section_details():
    while True:
        try:
            min_cover = input("Enter Minimum Cover (mm): ")
            if min_cover == '':
                raise ValueError("This Minimum Cover is required for the calculation. Please enter a value.")
            min_cover = float(min_cover)
            if min_cover <= 0:
                raise ValueError("Minimum cover must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            cover_dev = input("Enter Cover Deviation (mm) [Default = 10]: ")
            if cover_dev == '':
                cover_dev = 10
            else:
                cover_dev = float(cover_dev)
            if cover_dev < 0:
                raise ValueError("Cover deviation cannot be negative.")
            break
        except ValueError:
            print("Input is in incorrect type and it not matching..! Please Input Cover Deviation in non-negative numerical type..!")

    c_nom = min_cover + cover_dev  # Nominal cover calculation in mm

    while True:
        try:
            h = input("Enter Section Depth (mm): ")
            if h == '':
                raise ValueError("This Section Depth is required for the calculation. Please enter a value.")
            h = float(h)
            if h <= 0:
                raise ValueError("Section depth must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            b = input("Enter Section Width (mm): ")
            if b == '':
                raise ValueError("This Section Width is required for the calculation. Please enter a value.")
            b = float(b)
            if b <= 0:
                raise ValueError("Section width must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    return c_nom,h, b

def get_reinforcement_details():
    reinforcement_layers = {'tension': [], 'compression': []}

    for layer in range(1, 7):
        # Input for tension reinforcement layers
        print(f"Enter details for Tension Reinforcement Layer {layer}:")
        try:
            d_s = input(f"Diameter of bars in Layer {layer} (mm) [leave blank to skip]: ")
            if d_s == '':
                break
            d_s = float(d_s)
            n_s = int(input(f"Number of bars in Layer {layer}: "))
            A_s = math.pi * (d_s**2) * 0.25 * n_s
            reinforcement_layers['tension'].append((d_s, A_s))
        except ValueError:
            print("Incorrect input. Please enter valid numerical values for diameter and number of bars.")

    for layer in range(1, 7):
        # Input for compression reinforcement layers
        print(f"Enter details for Compression Reinforcement Layer {layer}:")
        try:
            d_sc = input(f"Diameter of bars in Layer {layer} (mm) [leave blank to skip]: ")
            if d_sc == '':
                break
            d_sc = float(d_sc)
            n_sc = int(input(f"Number of bars in Layer {layer}: "))
            A_sc = math.pi * (d_sc**2) * 0.25 * n_sc
            reinforcement_layers['compression'].append((d_sc, A_sc))
        except ValueError:
            print("Incorrect input. Please enter valid numerical values for diameter and number of bars.")

    # Calculate total reinforcement areas for tension and compression
    A_s_pro = sum(A_s for _, A_s in reinforcement_layers['tension'])
    A_sc_pro = sum(A_sc for _, A_sc in reinforcement_layers['compression'])

    return reinforcement_layers, A_s_pro, A_sc_pro

def get_shear_reinforcement_details():
    while True:
        try:
            d_w = input("Enter Shear Reinforcement Diameter (mm): ")
            if d_w == '':
                raise ValueError("This Shear Reinforcement Diameter is required for the calculation. Please enter a value.")
            d_w = float(d_w)
            if d_w <= 0:
                raise ValueError("Shear reinforcement diameter must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            n_l = input("Enter Number of Legs of Shear Reinforcement: ")
            if n_l == '':
                raise ValueError("This Number of Legs is required for the calculation. Please enter a value.")
            n_l = int(n_l)
            if n_l <= 0:
                raise ValueError("Number of legs must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    while True:
        try:
            s = input("Enter Spacing of Shear Reinforcement (mm): ")
            if s == '':
                raise ValueError("This Spacing of Shear Reinforcement is required for the calculation. Please enter a value.")
            s = float(s)
            if s <= 0:
                raise ValueError("Spacing must be positive.")
            break
        except ValueError as e:
            print(f"Error: {e}")

    A_sw = math.pi * (d_w * 1000)**2 * 0.25 * n_l  # Area of shear reinforcement in mm²

    return d_w, n_l, s, A_sw

def perform_bending_design(f_ck, f_yk_main,f_yk_shear, gamma_s, h, b, c_nom, d_w, reinforcement_layers, A_s_pro, A_sc_pro, gamma_c):
    f_cd = 0.85 * f_ck / gamma_c
    f_yd_main = f_yk_main / gamma_s
    f_yd_shear = f_yk_shear / gamma_s

    # Effective depth calculations
    A_s1, d_s1 = reinforcement_layers['tension'][0]
    A_sc1, d_sc1 = reinforcement_layers['compression'][0]
    
    # Corrected Centroid Calculation for Tension Reinforcement Layers
    # Updated calculation for centroid depth `y_t` for tension reinforcement
    A_s_total = sum(A_s for _, A_s in reinforcement_layers['tension'])

    y_t = 0

    for i, (d_s, A_s) in enumerate(reinforcement_layers['tension']):
        if i == 0:
            # Depth to centroid for the first layer is half the bar diameter
            layer_depth = d_s * 0.5
        else:
            # Calculate the depth to the centroid of subsequent layers
            previous_layers_depth = sum(
                (reinforcement_layers['tension'][j][0] + max(25, reinforcement_layers['tension'][j][0]))
                for j in range(i)
            )
            layer_depth = previous_layers_depth + (d_s * 0.5)

        # Sum up contributions for centroid calculation
        y_t += A_s * layer_depth

    # Final calculation of centroid depth for tension reinforcement
    y_t /= A_s_total

    # Updated calculation for centroid depth `y_c` for compression reinforcement
    A_sc_total = sum(A_sc for _, A_sc in reinforcement_layers['compression'])

    y_c = 0

    for i, (d_sc, A_sc) in enumerate(reinforcement_layers['compression']):
        if i == 0:
            # Depth to centroid for the first layer is half the bar diameter
            layer_depth = d_sc * 0.5
        else:
            # Calculate the depth to the centroid of subsequent layers
            previous_layers_depth = sum(
                (reinforcement_layers['compression'][j][0] + max(25, reinforcement_layers['compression'][j][0]))
                for j in range(i)
            )
            layer_depth = previous_layers_depth + (d_sc * 0.5)

        # Sum up contributions for centroid calculation
        y_c += A_sc * layer_depth

    # Final calculation of centroid depth for compression reinforcement
    y_c /= A_sc_total


    d_eff = h - c_nom - d_w - y_t
    dc_eff = c_nom + d_w + y_c

    # Redistribution
    rdp = float(input("Enter Redistribution Percentage (default 15%): ") or 15)
    mr = 1 - (rdp / 100)

    # K calculations
    K_bal = 0.453 * (mr - 0.4) * (1 - 0.4 * (mr - 0.4))
    M_Ed = float(input("Enter Design Moment M_Ed (kNm): ")) * 1e3
    K = M_Ed / (b * d_eff**2 * f_ck)

    if K <= K_bal:
        # Singly reinforced
        z_m = min(((0.5 + (0.25 - 0.881 * K)**0.5) * d_eff), 0.95 * d_eff)
        A_s_min = 0.001572 * b * d_eff
        A_s_req = max(M_Ed / (z_m * f_yd_main), A_s_min)
        A_sc_req = A_s_min
    else:
        # Doubly reinforced
        z_m_bal = 0.82 * d_eff
        duc_check = dc_eff / d_eff

        if duc_check <= 0.171:
            A_sc_req = ((K - K_bal) * f_ck * b * d_eff**2) / (f_yd_main * (d_eff - dc_eff))
            A_s_req = ((K_bal * f_ck * b * d_eff**2) / (f_yd_main * z_m_bal)) + A_sc_req
        else:
            f_sc = ((0.45 * d_eff - dc_eff) * 0.0035 * E_s) / (0.45 * d_eff)
            A_sc_req = ((K - K_bal) * f_ck * b * d_eff**2) / (f_sc * (d_eff - dc_eff))
            A_s_req = ((K_bal * f_ck * b * d_eff**2) / (f_yd_main * z_m_bal)) + A_sc_req

    return A_s_req, A_sc_req, f_yd_main, f_yd_shear, y_t, y_c, d_eff, dc_eff



import sys
from PyQt5.QtWidgets import QApplication, QFileDialog, QWidget, QVBoxLayout, QPushButton, QTextEdit
from fpdf import FPDF

class PDFGeneratorApp(QWidget):
    def __init__(self, output_text):
        super().__init__()
        self.output_text = output_text
        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        # Text edit to show the output
        self.text_display = QTextEdit(self)
        self.text_display.setPlainText('\n'.join(self.output_text))
        self.text_display.setReadOnly(True)
        layout.addWidget(self.text_display)

        # Button to save the output to PDF
        self.save_pdf_button = QPushButton('Save PDF', self)
        self.save_pdf_button.clicked.connect(self.save_pdf)
        layout.addWidget(self.save_pdf_button)

        # Set layout and window properties
        self.setLayout(layout)
        self.setWindowTitle("RC Beam Design Output")
        self.setGeometry(100, 100, 600, 400)

    def save_pdf(self):
        # Prompt a browse window to choose the folder location
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.AnyFile)
        file_dialog.setNameFilter("PDF Files (*.pdf)")
        file_dialog.setDefaultSuffix("pdf")
        file_path, _ = file_dialog.getSaveFileName(self, "Save PDF", "output.pdf", "PDF Files (*.pdf);;All Files (*)")
        if file_path:
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            for line in self.output_text:
                pdf.cell(200, 10, txt=line, ln=True)
            pdf.output(file_path)

def main():
    # Run the RC beam design script
    # Get material and section details
    f_ck, f_yk_main, f_yk_shear, gamma_c, alpha_cc, gamma_s = get_material_details()
    c_nom, h, b = get_section_details()
    reinforcement_layers, A_s_pro, A_sc_pro = get_reinforcement_details()
    d_w, n_l, s, A_sw = get_shear_reinforcement_details()

    # Perform bending design and get the results
    A_s_req, A_sc_req, f_yd_main, f_yd_shear, y_t, y_c, d_eff, dc_eff = perform_bending_design(f_ck, f_yk_main, f_yk_shear, gamma_s, h, b, c_nom, d_w, reinforcement_layers, A_s_pro, A_sc_pro, gamma_c)

    # Store all the output lines
    output_text = [
        "\nMaterial and Section Details:",
        f"Concrete strength (f_ck): {f_ck} N/mm²",
        f"Main reinforcement strength (f_yk_main): {f_yk_main} N/mm²",
        f"Shear reinforcement strength (f_yk_shear): {f_yk_shear} N/mm²",
        f"Partial factor for concrete (gamma_c): {gamma_c}",
        f"Compressive strength coefficient (alpha_cc): {alpha_cc}",
        f"Partial factor for steel (gamma_s): {gamma_s}",

        "\nCalculated Design Strengths:",
        f"Design strength of main reinforcement (f_yd_main): {f_yd_main} N/mm²",
        f"Design strength of shear reinforcement (f_yd_shear): {f_yd_shear} N/mm²",

        "\nSection Details:",
        f"Nominal cover (c_nom): {c_nom} m",
        f"Section depth (h): {h} m",
        f"Section width (b): {b} m",

        "\nReinforcement Details:",
        f"Total area of tension reinforcement (A_s_pro): {A_s_pro} mm²",
        f"Total area of compression reinforcement (A_sc_pro): {A_sc_pro} mm²",

        "\nEffective Depth Values:",
        f"Distance from centroid to tension reinforcement layer (y_t): {y_t} mm",
        f"Distance from centroid to compression reinforcement layer (y_c): {y_c} mm",
        f"Effective Depth to tension reinforcement (d_eff): {d_eff} mm",
        f"Effective Depth to compression reinforcement (dc_eff): {dc_eff} mm",

        "\nShear Reinforcement Details:",
        f"Shear reinforcement area (A_sw): {A_sw} mm²",

        "\nBending Design Results:",
        f"Required Area of Tension Reinforcement (A_s_req): {A_s_req:.2f} mm²",
        f"Required Area of Compression Reinforcement (A_sc_req): {A_sc_req:.2f} mm²",
    ]

    # Launch the PyQt5 app to display output and save as PDF
    app = QApplication(sys.argv)
    pdf_app = PDFGeneratorApp(output_text)
    pdf_app.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()





