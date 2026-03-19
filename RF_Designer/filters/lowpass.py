# filters/lowpass.py
# This file takes normalized g-values from prototypes.py and scales them
# to real inductor and capacitor values for a low-pass filter at a given
# frequency and impedance.

# The formulas are
# Series inductor:   L = g * Z0 / omega
# Shunt capacitor:   C = g / (Z0 * omega)

# g = the normalized g-value from the prototype table
# Z0 = system impedance in ohms (usually 50)
# omega = cutoff frequency in radians/sec = 2 * pi * fc

import math
from filters.prototypes import get_prototype
from components.eseries import nearest_standard, E24

def design_lowpass(response_type, order, fc, Z0=50):
    # designs a low-pass LC filter and returns the component values

    g = get_prototype(response_type, order)
    omega = 2 * math.pi * fc

    components = []
    inductor_count = 0
    capacitor_count = 0

    for i, g_val in enumerate(g[1:-1]): #iterate through everything except g[0] and g[-1]
        if i % 2 == 0:
            inductor_count += 1
            ideal_value = g_val * Z0 / omega
            components.append({
                'type': 'L',
                'ideal': ideal_value,
                'standard': nearest_standard(ideal_value, E24),
                'position': 'series',
                'label': f'L{inductor_count}'
            })
        else:
            capacitor_count += 1
            ideal_value = g_val / (Z0 * omega)
            components.append({
                'type': 'C',
                'ideal': ideal_value,
                'standard': nearest_standard(ideal_value, E24),
                'position': 'shunt',
                'label': f'C{capacitor_count}'
            })
    return components

def print_components(components, response_type, order, fc, Z0=50):
    # Print a formatted table of the component values

    print(f"\n{'=' * 50}")
    print(f"  Low-Pass Filter Design")
    print(f"  Response           : {response_type.capitalize()}")
    print(f"  Order              : {order}")
    print(f"  Cutoff frequency   : {fc / 1e6:.1f} MHz")
    print(f"  Impedance          : {Z0} ohm")
    print(f"{'=' * 55}")
    print(f"  {'Label':<6} {'Type':<12} {'Ideal':>12}  {'Standard':>12}")
    print(f"  {'-' * 49}")

    for comp in components:
        if comp['type'] == 'L':
            # Display inductors in nH (1 H = 1e9 nH)
            ideal_str = f"{comp['ideal'] * 1e9:.3f} nH"
            standard_str = f"{comp['standard'] * 1e9:.3f} nH"
        else:
            # Display capacitors in pF (1 F = 1e12 pF)
            ideal_str = f"{comp['ideal'] * 1e12:.3f} pF"
            standard_str = f"{comp['standard'] * 1e12:.3f} pF"

        print(f"  {comp['label']:<6} {comp['position']:<12} "
              f"{ideal_str:>12}  {standard_str:>12}")

    print(f"{'=' * 55}\n")

if __name__ == "__main__":

    # Test 1: 3rd order Butterworth low-pass at 915 MHz, 50 ohm
    components = design_lowpass('butterworth', 3, fc=915e6, Z0=50)
    print_components(components, 'butterworth', 3, fc=915e6, Z0=50)

    # Test 2: 5th order Chebyshev low-pass at 915 MHz, 50 ohm
    components = design_lowpass('chebyshev', 5, fc=915e6, Z0=50)
    print_components(components, 'chebyshev', 5, fc=915e6, Z0=50)

    # Test 3: 3rd order Butterworth at 868 MHz (EU LoRa band)
    components = design_lowpass('butterworth', 3, fc=868e6, Z0=50)
    print_components(components, 'butterworth', 3, fc=868e6, Z0=50)
