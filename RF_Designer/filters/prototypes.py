# filters/prototypes.py
# This file contains the normalized low-pass prototype g values for each filter response type.
# These describe the shape of the filter. The index of each list corresponds tro the order of the filter

# g[0] is always 1.0 because it is a normalized source resistance.
# g[1], g[2], ..., g[n] is the component values (inductors and capacitors)
# g[n+1] is the normalized load resistence (A value of 1.0 means matched load)

# BUTTERWORTH
# Maximally flat passband. There is no ripple.
# Slower rolloff compared to Chebyshev.
# values taken from https://www.rfcafe.com/references/electrical/butter-proto-values.htm

BUTTERWORTH_G = {
    1: [1.0, 2.0, 1.0],
    2: [1.0, 1.4142, 1.4142, 1.0],
    3: [1.0,  1.0000,  2.0000,  1.0000,  1.0],
    4: [1.0,  0.7654,  1.8478,  1.8478,  0.7654,  1.0],
    5: [1.0,  0.6180,  1.6180,  2.0000,  1.6180,  0.6180,  1.0],
    6: [1.0,  0.5176,  1.4142,  1.9319,  1.9319,  1.4142,  0.5176,  1.0],
    7: [1.0,  0.4450,  1.2470,  1.8019,  2.0000,  1.8019,  1.2470,  0.4450,  1.0]
}

# CHEBYSHEV (0.5 dB ripple)
# There are several dB options to choose from. I chose 0.5dB because it offers the sharpest stopband rolloff out of
# all of the available options. This leads to the best harmonic suppression. Note that for even ordered filters RLoad != 1.0
# This makes Chebyshev filters harder to use. For example, n=4, RLoad=0.5040, system Z0=50 ohm -> load = 50 * 0.5040 = 25.2 ohm
# values taken from https://www.rfcafe.com/references/electrical/cheby-proto-values.htm

CHEBYSHEV_G = {
    2: [1.0, 1.4029, 0.7071, 0.5040],
    3: [1.0, 1.5963, 1.0967, 1.5963, 1.0],
    4: [1.0, 1.6704, 1.1926, 2.3662, 0.8419, 0.5040],
    5: [1.0, 1.7058, 1.2296, 2.5409, 1.2296, 1.7058, 1.0],
    6: [1.0, 1.7254, 1.2478, 2.6064, 1.3136, 2.4759, 0.8696, 0.5040],
    7: [1.0, 1.7373, 1.2582, 2.6383, 1.3443, 2.6383, 1.2582, 1.7373, 1.0],
    8: [1.0, 1.7451, 1.2647, 2.6565, 1.3590, 2.6965, 1.3389, 2.5093, 0.8795, 0.5040],
    9: [1.0, 1.7505, 1.2690, 2.6678, 1.3673, 2.7240, 1.3673, 2.6678, 1.2690, 1.7505, 1.0]
}

# BESSEL
# The primary advantage of a Bessel filter is its linear phase response and nearly constant group delay across the
# passband, which preserves the shape of complex signals by ensuring all frequency components take the same time to pass through
# values taken from https://www.rfcafe.com/references/electrical/bessel-proto-values.htm
BESSEL_G = {
    1: [1.0,  2.0000,  1.0],
    2: [1.0,  1.5774,  0.4226,  1.0],
    3: [1.0,  1.2550,  0.5528,  0.1922,  1.0],
    4: [1.0,  1.0598,  0.5116,  0.3181,  0.1104,  1.0],
    5: [1.0,  0.9303,  0.4577,  0.3312,  0.2090,  0.0718,  1.0],
    6: [1.0,  0.8377,  0.4116,  0.3158,  0.2364,  0.1480,  0.0505,  1.0],
    7: [1.0,  0.7677,  0.3744,  0.2944,  0.2378,  0.1778,  0.1104,  0.0375,  1.0]
}

def get_prototype(response_type, order):
    # Returns the g values for a given response type and order

    tables = {
        'butterworth': BUTTERWORTH_G,
        'chebyshev': CHEBYSHEV_G,
        'bessel': BESSEL_G
    }

    if response_type.lower() not in tables:
        raise ValueError("Invalid response type '%s'" % response_type)

    table = tables[response_type.lower()]

    if order not in table:
        raise ValueError("Invalid order '%s'" % order)

    return table[order]

if __name__ == '__main__':
    print("--- Butterworth n=3 ---")
    g = get_prototype('butterworth', 3)
    print(f"g-values: {g}")

    print("\n--- Chebyshev n=3 (odd order - RLoad should be 1.0) ---")
    g = get_prototype('chebyshev', 3)
    print(f"g-values: {g}")
    print(f"RLoad = {g[-1]}  <-- should be 1.0")

    print("\n--- Chebyshev n=4 (even order - RLoad should be 0.5040) ---")
    g = get_prototype('chebyshev', 4)
    print(f"g-values: {g}")
    print(f"RLoad = {g[-1]}  <-- actual load = 50 * {g[-1]} = {50 * g[-1]:.1f} ohm")

    print("\n--- Bessel n=4 ---")
    g = get_prototype('bessel', 4)
    print(f"g-values: {g}")