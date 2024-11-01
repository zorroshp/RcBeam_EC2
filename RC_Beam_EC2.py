import math


# Function to calculate the area of tensile reinforcement
def calculate_reinforcement(M, b, h, fck, fyk, d):
    # Constants for Eurocode 2
    gamma_c = 1.5  # Partial safety factor for concrete
    gamma_s = 1.15  # Partial safety factor for steel

    # Design strengths
    fcd = fck / gamma_c
    fyd = fyk / gamma_s

    # Lever arm factor (assumed 0.9 for simplicity; depends on design)
    z = 0.9 * d

    # Area of tensile reinforcement (As)
    As = M / (z * fyd)

    return As


# Main function to run the beam design
def main():
    # Input parameters
    M = float(input("Enter the design moment (kNm): ")) * 1e6  # Convert kNm to Nmm
    b = float(input("Enter the width of the beam (mm): "))
    h = float(input("Enter the total height of the beam (mm): "))
    d = float(input("Enter the effective depth (mm): "))
    fck = float(input("Enter the characteristic strength of concrete (MPa): "))
    fyk = float(input("Enter the yield strength of reinforcement (MPa): "))

    # Calculate the area of tensile reinforcement
    As = calculate_reinforcement(M, b, h, fck, fyk, d)

    # Output the result
    print(f"Required area of tensile reinforcement: {As:.2f} mm²")


# Uncomment the line below to run the main function
main()
