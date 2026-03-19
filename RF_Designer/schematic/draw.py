# schematic/draw.py
# Draws a ladder network schematic using matplotlib

import matplotlib.pyplot as plt
import matplotlib.patches as patches


def _draw_inductor(ax, x, y, label, width=0.7):
    # 4 arcs along the wire represent an inductor
    bump_r = width / 8
    for i in range(4):
        cx = x + bump_r + i * bump_r * 2
        ax.add_patch(patches.Arc((cx, y), bump_r * 2, bump_r * 1.8, angle=0, theta1=0, theta2=180, color='#00aaff', linewidth=2))
    ax.text(x + width / 2, y + 0.25, label, ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')


def _draw_series_capacitor(ax, x, y, label, width=0.7):
    # two vertical lines represent a series capacitor
    cx = x + width / 2
    ax.plot([x, cx - 0.06], [y, y], color='white', linewidth=1.5)
    ax.plot([cx - 0.06, cx - 0.06], [y - 0.14, y + 0.14], color='#00ff99', linewidth=4)
    ax.plot([cx + 0.06, cx + 0.06], [y - 0.14, y + 0.14], color='#00ff99', linewidth=4)
    ax.plot([cx + 0.06, x + width], [y, y], color='white', linewidth=1.5)
    ax.text(cx, y + 0.25, label, ha='center', va='bottom', color='white', fontsize=9, fontweight='bold')


def _draw_shunt_capacitor(ax, x, y, label):
    # two horizontal lines represent a shunt capacitor going to ground
    ax.plot([x, x], [y, y - 0.35], color='white', linewidth=1.5)
    ax.plot([x - 0.16, x + 0.16], [y - 0.35, y - 0.35], color='#00ff99', linewidth=4)
    ax.plot([x - 0.16, x + 0.16], [y - 0.45, y - 0.45], color='#00ff99', linewidth=4)
    ax.plot([x, x], [y - 0.45, y - 0.85], color='white', linewidth=1.5)
    for i, w in enumerate([0.28, 0.18, 0.09]):
        ax.plot([x - w/2, x + w/2], [y - 0.85 - i * 0.1, y - 0.85 - i * 0.1], color='white', linewidth=1.5)
    ax.text(x + 0.22, y - 0.45, label, ha='left', va='center', color='white', fontsize=9, fontweight='bold')


def _draw_shunt_inductor(ax, x, y, label):
    # arcs going downward represent a shunt inductor going to ground
    ax.plot([x, x], [y, y - 0.2], color='white', linewidth=1.5)
    for i in range(3):
        cy = y - 0.2 - 0.09 - i * 0.18
        ax.add_patch(patches.Arc((x, cy), 0.18, 0.16, angle=90, theta1=0, theta2=180, color='#00aaff', linewidth=2))
    bottom = y - 0.2 - 3 * 0.18
    ax.plot([x, x], [bottom, bottom - 0.2], color='white', linewidth=1.5)
    for i, w in enumerate([0.28, 0.18, 0.09]):
        ax.plot([x - w/2, x + w/2], [bottom - 0.2 - i * 0.1, bottom - 0.2 - i * 0.1], color='white', linewidth=1.5)
    ax.text(x + 0.22, y - 0.45, label, ha='left', va='center', color='white', fontsize=9, fontweight='bold')


def _draw_resistor(ax, x, y, label, value, vertical=False):
    rw, rh = (0.45, 0.22) if not vertical else (0.22, 0.45)
    ax.add_patch(patches.FancyBboxPatch((x - rw/2, y - rh/2), rw, rh, boxstyle='square,pad=0', edgecolor='#aaaaaa', facecolor='#333333', linewidth=1.5))
    ax.text(x, y, label, ha='center', va='center', color='white', fontsize=7, fontweight='bold')
    if vertical:
        # label to the right of the box so it never overlaps the wire
        ax.text(x + rw/2 + 0.08, y, value, ha='left', va='center', color='#ffaa00', fontsize=8, fontweight='bold')
    else:
        # label above the box so it never overlaps the horizontal wire
        ax.text(x, y + rh/2 + 0.08, value, ha='center', va='bottom', color='#ffaa00', fontsize=8, fontweight='bold')


def draw_schematic(components, title='Filter Schematic'):

    seg = 0.9
    pad = 0.8
    total_width = pad * 2 + len(components) * seg + 2.0

    fig, ax = plt.subplots(figsize=(max(12, total_width * 1.4), 5))
    fig.patch.set_facecolor('#1e1e1e')
    ax.set_facecolor('#1e1e1e')
    ax.set_aspect('equal')
    ax.axis('off')
    ax.set_title(title, color='white', fontsize=11, pad=12)

    y = 1.5

    # voltage source circle with + and - labels
    vs_cx = 0.55
    ax.add_patch(patches.Circle((vs_cx, y - 0.5), 0.25, fill=False, edgecolor='#ffaa00', linewidth=2))
    ax.text(vs_cx, y - 0.38, '+', ha='center', va='center', color='#ffaa00', fontsize=10, fontweight='bold')
    ax.text(vs_cx, y - 0.62, '−', ha='center', va='center', color='#ffaa00', fontsize=10, fontweight='bold')
    ax.text(vs_cx - 0.32, y - 0.5, 'V1\n1V AC', ha='right', va='center', color='#ffaa00', fontsize=8)

    # wires connecting voltage source to main line and to ground
    ax.plot([vs_cx, vs_cx], [y - 0.25, y], color='white', linewidth=1.5)
    ax.plot([vs_cx, vs_cx], [y - 0.75, y - 1.0], color='white', linewidth=1.5)
    for i, w in enumerate([0.28, 0.18, 0.09]):
        ax.plot([vs_cx - w/2, vs_cx + w/2], [y - 1.0 - i * 0.1, y - 1.0 - i * 0.1], color='white', linewidth=1.5)

    # RS resistor after the voltage source
    rs_x = vs_cx + 0.25
    ax.plot([vs_cx, rs_x], [y, y], color='white', linewidth=1.5)
    _draw_resistor(ax, rs_x + 0.225, y, 'RS', '50Ω')
    x = rs_x + 0.45 + 0.15
    ax.plot([rs_x + 0.45, x], [y, y], color='white', linewidth=1.5)

    # draw each filter component
    for comp in components:
        cx = x + seg / 2
        if comp['position'] == 'series':
            ax.plot([x, x + (seg - 0.7) / 2], [y, y], color='white', linewidth=1.5)
            if comp['type'] == 'L':
                _draw_inductor(ax, x + (seg - 0.7) / 2, y, comp['label'], width=0.7)
            else:
                _draw_series_capacitor(ax, x + (seg - 0.7) / 2, y, comp['label'], width=0.7)
            ax.plot([x + (seg - 0.7) / 2 + 0.7, x + seg], [y, y], color='white', linewidth=1.5)
        elif comp['position'] == 'shunt':
            ax.plot([x, x + seg], [y, y], color='white', linewidth=1.5)
            if comp['type'] == 'C':
                _draw_shunt_capacitor(ax, cx, y, comp['label'])
            else:
                _draw_shunt_inductor(ax, cx, y, comp['label'])
        x += seg

    # RL resistor at the output, connected vertically to ground
    rl_x = x + 0.3
    ax.plot([x, rl_x], [y, y], color='white', linewidth=1.5)
    ax.plot([rl_x, rl_x], [y, y - 0.15], color='white', linewidth=1.5)
    _draw_resistor(ax, rl_x, y - 0.15 - 0.225, 'RL', '50Ω', vertical=True)
    ax.plot([rl_x, rl_x], [y - 0.15 - 0.45, y - 1.0], color='white', linewidth=1.5)
    for i, w in enumerate([0.28, 0.18, 0.09]):
        ax.plot([rl_x - w/2, rl_x + w/2], [y - 1.0 - i * 0.1, y - 1.0 - i * 0.1], color='white', linewidth=1.5)

    ax.set_xlim(0, rl_x + 0.8)
    ax.set_ylim(-1.5, 2.2)
    plt.tight_layout()
    plt.show(block=False)


if __name__ == '__main__':
    from filters.lowpass import design_lowpass
    from filters.highpass import design_highpass

    components = design_lowpass('butterworth', 3, fc=915e6, Z0=50)
    draw_schematic(components, 'Butterworth Low-Pass n=3 @ 915 MHz')

    components = design_highpass('butterworth', 3, fc=915e6, Z0=50)
    draw_schematic(components, 'Butterworth High-Pass n=3 @ 915 MHz')