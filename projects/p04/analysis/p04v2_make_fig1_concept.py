#!/usr/bin/env python3
"""
P04 v2 Fig 1: Conceptual schematic + Antarctic map with study regions

Panel a: Feedback loop diagram (competing mechanisms)
Panel b: Antarctic map showing MIZ, ice shelves, study regions
"""

import numpy as np
import matplotlib; matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch
import matplotlib.patheffects as pe

FIG = '/Users/zhulin/aitest/OpenSCI-Ocean/projects/p04/manuscript_v2/figures'

fig = plt.figure(figsize=(16, 7))

# ---- Panel A: Feedback loop conceptual diagram ----
ax = fig.add_axes([0.02, 0.05, 0.48, 0.90])
ax.set_xlim(0, 10); ax.set_ylim(0, 8)
ax.axis('off')

boxes = {
    'SIC':    (1.5, 6.5, 'Sea Ice\nConcentration', '#87CEEB'),
    'Fetch':  (5.0, 6.5, 'Fetch\n(Open Water)', '#FFD700'),
    'SWH':    (8.5, 6.5, 'Wave Height\n(SWH)', '#FF6347'),
    'Edge':   (8.5, 3.0, 'Ice Edge\nRetreat', '#90EE90'),
    'Wind':   (5.0, 3.0, 'Wind\n(SAM/Westerlies)', '#DDA0DD'),
    'Swell':  (1.5, 3.0, 'Swell\nAttenuation', '#FFA07A'),
}

for key, (x, y, label, color) in boxes.items():
    box = FancyBboxPatch((x-0.9, y-0.5), 1.8, 1.0, boxstyle="round,pad=0.1",
                          facecolor=color, edgecolor='k', lw=1.5, alpha=0.85)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', fontsize=9, fontweight='bold')

def draw_arrow(ax, x1, y1, x2, y2, color='k', lw=2, style='->', label='', ls='-'):
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle=style, color=color, lw=lw, ls=ls))
    if label:
        mx, my = (x1+x2)/2, (y1+y2)/2
        ax.text(mx, my+0.25, label, ha='center', fontsize=7, color=color,
                bbox=dict(facecolor='white', edgecolor='none', alpha=0.8))

# Supported links (solid green)
draw_arrow(ax, 2.4, 6.5, 4.1, 6.5, 'green', 2.5, '->', 'p<0.001***')
draw_arrow(ax, 9.4, 6.0, 9.4, 3.5, 'green', 2, '->', 'p=0.034*')
draw_arrow(ax, 5.0, 3.5, 5.0, 6.0, 'green', 2, '->', 'p=0.018*')

# Failed link (red dashed)
draw_arrow(ax, 5.9, 6.5, 7.6, 6.5, 'red', 2.5, '->', 'p=0.74 FAILS', ls='--')

# Direct SIC→SWH via swell attenuation (blue, the key finding)
ax.annotate('', xy=(2.4, 3.0), xytext=(1.5, 6.0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2.5))
ax.text(0.5, 4.7, 'SIC reduces\nattenuation', fontsize=7, color='blue', rotation=70)
ax.annotate('', xy=(7.6, 6.5), xytext=(2.4, 3.0),
            arrowprops=dict(arrowstyle='->', color='blue', lw=2.5, ls='-'))
ax.text(4.5, 4.5, 'More swell\nreaches edge', fontsize=7, color='blue',
        bbox=dict(facecolor='lightyellow', edgecolor='blue', alpha=0.7))

# Feedback arrow
draw_arrow(ax, 7.6, 3.0, 2.4, 6.0, '#666', 1.5, '->', 'p=0.049*')

# Legend
ax.text(0.3, 1.2, 'Hypothesis A (fetch): SIC↓ → Fetch↑ → SWH↑', fontsize=8,
        color='red', fontstyle='italic')
ax.text(0.3, 0.7, 'Hypothesis B (swell attenuation): SIC↓ → less attenuation → SWH↑',
        fontsize=8, color='blue', fontweight='bold')
ax.text(0.3, 0.2, 'Green = supported | Red dashed = fails | Blue = key mechanism',
        fontsize=7, color='gray')
ax.set_title('(a) Competing wave-ice feedback mechanisms', fontsize=12, fontweight='bold')

# ---- Panel B: Antarctic map (simplified) ----
ax2 = fig.add_axes([0.52, 0.05, 0.46, 0.90])

theta = np.linspace(0, 2*np.pi, 360)
# Simplified Antarctic coastline (circle at ~70S)
coast_r = 2.0
ax2.plot(coast_r * np.cos(theta), coast_r * np.sin(theta), 'k-', lw=2)
ax2.fill(coast_r * np.cos(theta), coast_r * np.sin(theta), color='#E8E8E8', alpha=0.5)

# MIZ band (between ~60S and ~65S)
miz_inner = 2.5; miz_outer = 3.5
ax2.fill_between(miz_outer*np.cos(theta), miz_outer*np.sin(theta),
                  miz_inner*np.cos(theta), miz_inner*np.sin(theta),
                  color='#87CEEB', alpha=0.3, label='MIZ (55-65°S)')

# Ice edge
ax2.plot(miz_inner*np.cos(theta), miz_inner*np.sin(theta), 'b--', lw=1.5, label='Ice edge (~65°S)')

# Open ocean
ax2.fill_between(5*np.cos(theta), 5*np.sin(theta),
                  miz_outer*np.cos(theta), miz_outer*np.sin(theta),
                  color='#4169E1', alpha=0.15, label='Open Southern Ocean')

# Latitude labels
for r, lat in [(2.0, '70°S'), (2.5, '65°S'), (3.5, '55°S'), (5.0, '40°S')]:
    ax2.plot(r*np.cos(theta), r*np.sin(theta), ':', color='gray', lw=0.5, alpha=0.5)
    ax2.text(r*0.7, r*0.7, lat, fontsize=7, color='gray')

# Ice shelves (approximate positions)
shelves = [
    ('Ross', 180, 2.1), ('F-R', 310, 2.1), ('Amery', 70, 2.3),
    ('Larsen C', 295, 2.3), ('Totten', 115, 2.3),
]
for name, angle_deg, r in shelves:
    angle = np.radians(angle_deg)
    ax2.plot(r*np.cos(angle), r*np.sin(angle), 'r^', ms=10, zorder=5)
    ax2.text(r*np.cos(angle)+0.15, r*np.sin(angle)+0.15, name, fontsize=7,
             fontweight='bold', color='red')

# Swell arrows (from open ocean toward ice)
for angle_deg in range(0, 360, 45):
    angle = np.radians(angle_deg)
    x1 = 4.5 * np.cos(angle); y1 = 4.5 * np.sin(angle)
    x2 = 3.2 * np.cos(angle); y2 = 3.2 * np.sin(angle)
    ax2.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='->', color='#FF6347', lw=1.5, alpha=0.6))

ax2.text(4.2, 0, 'Swell', fontsize=9, color='#FF6347', fontstyle='italic', alpha=0.7)

# Wind arrows (circumpolar westerlies)
for angle_deg in range(0, 360, 60):
    angle = np.radians(angle_deg)
    r = 4.0
    dx = -0.8 * np.sin(angle); dy = 0.8 * np.cos(angle)
    ax2.annotate('', xy=(r*np.cos(angle)+dx, r*np.sin(angle)+dy),
                xytext=(r*np.cos(angle), r*np.sin(angle)),
                arrowprops=dict(arrowstyle='->', color='purple', lw=1.5, alpha=0.5))

ax2.text(-0.5, 4.5, 'Westerlies', fontsize=8, color='purple', fontstyle='italic', rotation=15)

ax2.set_xlim(-5.5, 5.5); ax2.set_ylim(-5.5, 5.5)
ax2.set_aspect('equal')
ax2.axis('off')
ax2.legend(loc='lower left', fontsize=7, framealpha=0.8)
ax2.set_title('(b) Southern Ocean study domain', fontsize=12, fontweight='bold')

plt.savefig(f'{FIG}/fig1_concept.png', bbox_inches='tight', dpi=300)
plt.close()
print(f'-> {FIG}/fig1_concept.png')
