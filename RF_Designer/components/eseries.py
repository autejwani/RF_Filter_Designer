# components/eseries.py
# Real components are manufactured in specific values defined by the E-series standard (IEC 60063)
# The series names (E12, E24, E96) tells you how many values there are per decade
# values taken from https://www.electronics-notes.com/articles/electronic_components/resistors/standard-resistor-values-e-series-e3-e6-e12-e24-e48-e96.php#google_vignette
import math

E12 = [1.0, 1.2, 1.5, 1.8, 2.2, 2.7,
       3.3, 3.9, 4.7, 5.6, 6.8, 8.2]

E24 = [1.0, 1.1, 1.2, 1.3, 1.5, 1.6,
       1.8, 2.0, 2.2, 2.4, 2.7, 3.0,
       3.3, 3.6, 3.9, 4.3, 4.7, 5.1,
       5.6, 6.2, 6.8, 7.5, 8.2, 9.1]

E96 = [1.00, 1.02, 1.05, 1.07, 1.10, 1.13, 1.15, 1.18,
       1.21, 1.24, 1.27, 1.30, 1.33, 1.37, 1.40, 1.43,
       1.47, 1.50, 1.54, 1.58, 1.62, 1.65, 1.69, 1.74,
       1.78, 1.82, 1.87, 1.91, 1.96, 2.00, 2.05, 2.10,
       2.15, 2.21, 2.26, 2.32, 2.37, 2.43, 2.49, 2.55,
       2.61, 2.67, 2.74, 2.80, 2.87, 2.94, 3.01, 3.09,
       3.16, 3.24, 3.32, 3.40, 3.48, 3.57, 3.65, 3.74,
       3.83, 3.92, 4.02, 4.12, 4.22, 4.32, 4.42, 4.53,
       4.64, 4.75, 4.87, 4.99, 5.11, 5.23, 5.36, 5.49,
       5.62, 5.76, 5.90, 6.04, 6.19, 6.34, 6.49, 6.65,
       6.81, 6.98, 7.15, 7.32, 7.50, 7.68, 7.87, 8.06,
       8.25, 8.45, 8.66, 8.87, 9.09, 9.31, 9.53, 9.76]

def nearest_standard(value, series=E24):
    # Finds component value closest to nearest value in an E-series
    # How it works:
    #   1. Find which power of 10 the value sits in
    #       e.g. 47.3e-9 sits in the 1e-8 decade (10nH to 99nH)
    #   2. Divide the value by the decade to normalize it to between 1.0 and 9.99
    #       e.g. 47.3e-9 / 1e-8 = 4.73
    #   3. Find the closest number in the E-series table to 4.73
    #       e.g. closest E24 value to 4.73 is 4.7
    #   4. Multiply back by the decade to restore the original scale
    #       e.g. 4.7 * 1e-8 = 47e-9 = 47 nH

    decade = 10 ** round(math.floor(math.log10(value)))
    normalized = value / decade
    closest_value = min(series, key=lambda x: abs(x - normalized))
    return closest_value * decade

if __name__ == "__main__":

    test_values = [
        (8.70e-9,  "H",  "nH", 1e9,  "ideal L at 915MHz n=3 Butterworth"),
        (6.95e-12, "F",  "pF", 1e12, "ideal C at 915MHz n=3 Butterworth"),
        (3.21e-9,  "H",  "nH", 1e9,  "small inductor"),
        (18.5e-12, "F",  "pF", 1e12, "mid range capacitor"),
        (100.3e-9, "H",  "nH", 1e9,  "larger inductor"),
    ]

    print(f"{'Ideal Value':<15} {'E24 Snap':<15} {'Description'}")
    print("-" * 60)

    for value, unit, display_unit, scale, description in test_values:
        snapped = nearest_standard(value, series=E24)
        print(f"{value*scale:<10.2f} {display_unit:<4} "
              f"{snapped*scale:<10.2f} {display_unit:<4}  {description}")