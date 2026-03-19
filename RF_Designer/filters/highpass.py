# filters/highpass.py
# A high-pass filter is derived from the low-pass prototype using a
# frequency transformation. The transformation replaces every element
# with its dual:
# Low-pass series inductor -> High-pass series capacitor
# Low-pass shunt capacitor -> High-pass shunt inductor
# The scaling formulas also invert compared to low pass
# Series capacitor: C = 1 / (g * Z0 * omega)
# Shunt inductor: L = Z0 / (g * omega)

import math
from filters.prototypes import get_prototype
from components.eseries import nearest_standard, E24

def design_highpass(response_type, order, fc, Z0=50):
    # Designs a high-pass LC ladder filter and returns the component values.
    g = get_prototype(response_type, order)
    omega = 2 * math.pi * fc

    components = []
    inductor_count = 0
    capacitor_count = 0

    for i, g_val in enumerate(g[1:-1]):  # slice off g[0] and g[-1]
        if i % 2 == 0:
            capacitor_count += 1
            ideal_value = 1 / (g_val * Z0 * omega)
            components.append({
                'type': 'C',
                'ideal': ideal_value,
                'standard': nearest_standard(ideal_value, E24),
                'position': 'series',
                'label': f'C{capacitor_count}',
            })
        else:
            inductor_count += 1
            ideal_value = Z0 / (g_val * omega)
            components.append({
                'type': 'L',
                'ideal': ideal_value,
                'standard': nearest_standard(ideal_value, E24),
                'position': 'shunt',
                'label': f'L{inductor_count}'
            })
    return components

def print_components(components, response_type, order, fc, Z0=50):
    # Prints a formatted table of component values to the console.

    print(f"\n{'=' * 50}")
    print(f"  High-Pass Filter Design")
    print(f"  Response  : {response_type.capitalize()}")
    print(f"  Order     : {order}")
    print(f"  Cutoff    : {fc / 1e6:.1f} MHz")
    print(f"  Impedance : {Z0} ohm")
    print(f"{'=' * 50}")
    print(f"  {'Label':<6} {'Position':<12} {'Ideal':>12}  {'Standard':>12}")
    print(f"  {'-' * 49}")

    for comp in components:
        if comp['type'] == 'L':
            ideal_str = f"{comp['ideal'] * 1e9:.3f} nH"
            standard_str = f"{comp['standard'] * 1e9:.3f} nH"
        else:
            ideal_str = f"{comp['ideal'] * 1e12:.3f} pF"
            standard_str = f"{comp['standard'] * 1e12:.3f} pF"

        print(f"  {comp['label']:<6} {comp['position']:<12} "
              f"{ideal_str:>12}  {standard_str:>12}")

    print(f"{'=' * 50}\n")

if __name__ == "__main__":

    # Test 1: 3rd order Butterworth high-pass at 915 MHz
    # Notice the component types are flipped vs lowpass:
    # series capacitors and shunt inductors instead of the reverse
    components = design_highpass('butterworth', 3, fc=915e6, Z0=50)
    print_components(components, 'butterworth', 3, fc=915e6, Z0=50)

    # Test 2: 5th order Chebyshev high-pass at 915 MHz
    components = design_highpass('chebyshev', 5, fc=915e6, Z0=50)
    print_components(components, 'chebyshev', 5, fc=915e6, Z0=50)