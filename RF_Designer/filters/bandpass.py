# filters/bandpass.py
# A band-pass filter is derived from the low-pass prototype using the
# low-pass to band-pass frequency transformation.

# Every low-pass element splits into two band-pass elements:
#
#   LP series inductor  ->  series LC pair  (L and C in series)
#   LP shunt capacitor  ->  shunt LC pair   (L and C in parallel)
#
# This means an nth order prototype produces a 2n component filter.
# We need to know two things:
# f_center = center frequency of the passband
# bandwidth = width of the passband
# Q = f_center / bandwidth  (higher Q = narrower band)

import math
from filters.prototypes import get_prototype
from components.eseries import nearest_standard, E24

def design_bandpass(response_type, order, f_center, bandwidth, Z0=50):
    # Designs a band-pass LC ladder filter and returns the component values.
    g = get_prototype(response_type, order)
    omega_0 = 2 * math.pi * f_center  # center frequency in rad/s
    Q = f_center / bandwidth  # Q factor (sharpness of the band)

    components = []
    group_count = 0  # tracks which LC pair we are on
    inductor_count = 0
    capacitor_count = 0

    for i, g_val in enumerate(g[1:-1]):
        group_count += 1
        if i % 2 == 0:
            # This g-value was a series inductor in the low-pass prototype.
            # It becomes a SERIES LC PAIR (L and C in series with each other).
            # At the center frequency these resonate and pass the signal.
            inductor_count += 1
            capacitor_count += 1

            L_ideal = (g_val * Z0 * Q) / omega_0
            C_ideal = 1 / (g_val * Z0 * Q * omega_0)

            components.append({
                'type': 'L',
                'ideal': L_ideal,
                'standard': nearest_standard(L_ideal, E24),
                'position': 'series',
                'group': group_count,
                'label': f'L{inductor_count}',
            })
            components.append({
                'type': 'C',
                'ideal': C_ideal,
                'standard': nearest_standard(C_ideal, E24),
                'position': 'series',
                'group': group_count,
                'label': f'C{capacitor_count}',
            })
        else:
            # This g-value was a shunt capacitor in the low-pass prototype.
            # It becomes a SHUNT LC PAIR (L and C in parallel to ground).
            # At the center frequency these resonate and block the signal
            # from leaking to ground.
            inductor_count += 1
            capacitor_count += 1

            C_ideal = (g_val * Q) / (Z0 * omega_0)
            L_ideal = Z0 / (g_val * Q * omega_0)

            components.append({
                'type': 'C',
                'ideal': C_ideal,
                'standard': nearest_standard(C_ideal, E24),
                'position': 'shunt',
                'group': group_count,
                'label': f'C{capacitor_count}',
            })
            components.append({
                'type': 'L',
                'ideal': L_ideal,
                'standard': nearest_standard(L_ideal, E24),
                'position': 'shunt',
                'group': group_count,
                'label': f'L{inductor_count}',
            })
    return components

def print_components(components, response_type, order, f_center, bandwidth, Z0):
    # Prints a formatted table of component values to the console.
    # Groups are printed together with a divider to show which components
    # form a resonant pair.

    Q = f_center / bandwidth
    print(f"\n{'=' * 50}")
    print(f"  Band-Pass Filter Design")
    print(f"  Response  : {response_type.capitalize()}")
    print(f"  Order     : {order} (prototype) → {order * 2} components")
    print(f"  Center    : {f_center / 1e6:.1f} MHz")
    print(f"  Bandwidth : {bandwidth / 1e6:.1f} MHz")
    print(f"  Q factor  : {Q:.2f}")
    print(f"  Impedance : {Z0} ohm")
    print(f"{'=' * 50}")
    print(f"  {'Label':<6} {'Position':<10} {'Group':<8} {'Ideal':>12}  {'Standard':>12}")
    print(f"  {'-' * 50}")

    current_group = None
    for comp in components:
        # Print a divider between groups so LC pairs are clear
        if comp['group'] != current_group:
            if current_group is not None:
                print(f"  {'-' * 54}")
            current_group = comp['group']

        if comp['type'] == 'L':
            ideal_str = f"{comp['ideal'] * 1e9:.3f} nH"
            standard_str = f"{comp['standard'] * 1e9:.3f} nH"
        else:
            ideal_str = f"{comp['ideal'] * 1e12:.3f} pF"
            standard_str = f"{comp['standard'] * 1e12:.3f} pF"

        print(f"  {comp['label']:<6} {comp['position']:<10} "
              f"{'pair ' + str(comp['group']):<8} "
              f"{ideal_str:>12}  {standard_str:>12}")

    print(f"{'=' * 60}\n")

if __name__ == "__main__":

    # Test 1: 3rd order Butterworth band-pass
    # Center 915 MHz, 50 MHz wide (covers the full 902-928 MHz US ISM band)
    components = design_bandpass('butterworth', 3,
                                 f_center=915e6,
                                 bandwidth=50e6,
                                 Z0=50)
    print_components(components, 'butterworth', 3,
                     f_center=915e6, bandwidth=50e6, Z0=50)

    # Test 2: 3rd order Chebyshev band-pass
    # Narrower band - 10 MHz wide, higher Q
    components = design_bandpass('chebyshev', 3,
                                 f_center=915e6,
                                 bandwidth=10e6,
                                 Z0=50)
    print_components(components, 'chebyshev', 3,
                     f_center=915e6, bandwidth=10e6, Z0=50)