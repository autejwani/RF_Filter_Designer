# simulation/abcd.py
# Simulates the frequency response of an LC ladder filter using
# ABCD transmission matrices

# Steps:
# 1. Build a 2x2 ABCD matrix for each component
# 2. Multiply all matrices together (cascade)
# 3. Convert the result to S21 (transmission coefficient)
# 4. Convert S21 to dB for plotting

# S21 in dB is what you see on a spectrum analyser or VNA.
# 0 dB = signal passes through unchanged
# -3 dB = cutoff frequency (half power point)
# -40 dB = signal reduced to 1% of its original voltage

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.ticker as ticker

def abcd_series_inductor(L, omega):
    # ABCD matrix for a series inductor.
    # Impedance of inductor: Z = j * omega * L
    # Series element matrix: [[1, Z], [0, 1]]

    Z = 1j * omega * L
    return np.array([[1, Z], [0, 1]], dtype=complex)

def abcd_shunt_capacitor(C, omega):
    # ABCD matrix for a shunt capacitor (connected to ground).
    # Admittance of capacitor: Y = j * omega * C
    # Shunt element matrix: [[1, 0], [Y, 1]]

    Y = 1j * omega * C
    return np.array([[1, 0], [Y, 1]], dtype=complex)

def abcd_series_capacitor(C, omega):
    # ABCD matrix for a series capacitor.
    # Impedance of capacitor: Z = 1 / (j * omega * C)

    Z = 1 / (1j * omega * C)
    return np.array([[1, Z], [0, 1]], dtype=complex)

def abcd_shunt_inductor(L, omega):
    # ABCD matrix for a shunt inductor (connected to ground).
    # Admittance of inductor: Y = 1 / (j * omega * L)

    Y = 1 / (1j * omega * L)
    return np.array([[1, 0], [Y, 1]], dtype=complex)

def abcd_to_s21(M, Z0=50):
    # Converts a total ABCD matrix to S21
    # The formula assumes equal source and load impedance Z0.
    A = M[0, 0]
    B = M[0, 1]
    C = M[1, 0]
    D = M[1, 1]
    S21 = 2 / (A + B / Z0 + C * Z0 + D)
    return S21

def simulate(components, f_start, f_stop, Z0=50, num_points=500):
    # Simulates the frequency response of a filter across a frequency range.
    # For each frequency point it builds and cascades the ABCD matrices
    # for all components, then converts to S21 in dB.

    frequencies = np.logspace(np.log10(f_start), np.log10(f_stop), num_points)
    s21_db = np.zeros(num_points)
    for idx, f in enumerate(frequencies):
        omega = 2 * np.pi * f
        # Identity matrix
        M_total = np.eye(2, dtype=complex)

        # Cascade each component matrix in order
        for comp in components:
            value = comp['standard']
            if comp['type'] == 'L' and comp['position'] == 'series':
                M = abcd_series_inductor(value, omega)

            elif comp['type'] == 'C' and comp['position'] == 'shunt':
                M = abcd_shunt_capacitor(value, omega)

            elif comp['type'] == 'C' and comp['position'] == 'series':
                M = abcd_series_capacitor(value, omega)

            elif comp['type'] == 'L' and comp['position'] == 'shunt':
                M = abcd_shunt_inductor(value, omega)

            M_total = M_total @ M
        s21 = abcd_to_s21(M_total, Z0)

        # Convert to dB: dB = 20 * log10(|S21|)
        s21_db[idx] = 20 * np.log10(np.abs(s21))
    return frequencies, s21_db

def plot_response(ax, components, f_start, f_stop, Z0=50, num_points=500, label=None, color='#00aaff'):
    # Plots the S21 frequency response
    # Parameters:
    # ax          (matplotlib.axes.Axes): The axes to draw on.
    # In the GUI this will be a canvas inside the window.
    # components  (list):  Component dicts from lowpass/highpass/bandpass
    # f_start     (float): Start frequency in Hz
    # f_stop      (float): Stop frequency in Hz
    # Z0          (float): System impedance in ohms
    # num_points  (int):   Number of simulation points
    # label       (str):   Legend label for this trace. Optional.
    # color       (str):   Line color. Defaults to blue.
    freqs, s21_db = simulate(components, f_start, f_stop, Z0, num_points)
    ax.plot(freqs / 1e6, s21_db, color=color, linewidth=2, label=label)
    ax.set_xscale('log')  # log frequency axis is standard in RF
    ax.set_xlabel('Frequency (MHz)', fontsize=11)
    ax.set_ylabel('S21 (dB)', fontsize=11)
    ax.set_ylim(-100, 5)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5, alpha=0.7)

    ax.set_title('Filter Frequency Response', fontsize=12)
    return freqs, s21_db

if __name__ == '__main__':
    from filters.lowpass import design_lowpass

    # --- Test 1: print numerical results (same as before)
    components = design_lowpass('butterworth', 3, fc=915e6, Z0=50)
    freqs, s21 = simulate(components, f_start=100e6, f_stop=10e9, Z0=50)

    print("Frequency Response - Butterworth LP n=3 fc=915MHz")
    print(f"{'Frequency':<25} {'S21 (dB)':<10}")
    print("-" * 35)

    check_freqs = [100e6, 500e6, 915e6, 1830e6, 2745e6]
    labels      = ["100 MHz", "500 MHz", "915 MHz (fc)",
                   "1830 MHz (2nd harmonic)", "2745 MHz (3rd harmonic)"]

    for cf, label in zip(check_freqs, labels):
        idx = np.argmin(np.abs(freqs - cf))
        print(f"{label:<25} {s21[idx]:.2f} dB")

    # --- Test 2: plot three filters on the same axes for comparison
    fig, ax = plt.subplots(figsize=(10, 6))

    # Dark background styling
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    ax.tick_params(colors='white')
    ax.xaxis.label.set_color('white')
    ax.yaxis.label.set_color('white')
    ax.title.set_color('white')
    ax.spines[:].set_color('#444444')

    # Design three filters to compare on the same plot
    comp_bw3 = design_lowpass('butterworth', 3, fc=915e6, Z0=50)
    comp_bw5 = design_lowpass('butterworth', 5, fc=915e6, Z0=50)
    comp_ch5 = design_lowpass('chebyshev',   5, fc=915e6, Z0=50)

    # Plot all three traces onto the same ax
    plot_response(ax, comp_bw3, 100e6, 5e9, label='Butterworth n=3', color='#00aaff')
    plot_response(ax, comp_bw5, 100e6, 5e9, label='Butterworth n=5', color='#00ff99')
    plot_response(ax, comp_ch5, 100e6, 5e9, label='Chebyshev n=5',   color='#ff6644')

    # Add legend with dark styling
    legend = ax.legend(fontsize=9)
    legend.get_frame().set_facecolor('#2e2e2e')
    legend.get_frame().set_edgecolor('#444444')
    for text in legend.get_texts():
        text.set_color('white')

    # Add annotation marking the 915 MHz cutoff on the x axis
    ax.axvline(x=915, color='yellow', linestyle=':', linewidth=1, alpha=0.6)
    ax.axhline(y=-3, color='red', linestyle='--', linewidth=1, alpha=0.8, label='-3 dB reference')
    ax.text(915, -75, '915 MHz', color='yellow', fontsize=8,
            ha='center', va='bottom')

    plt.tight_layout()
    plt.show()