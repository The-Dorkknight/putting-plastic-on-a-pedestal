"""Draw every figure in the paper from the data in ../data (and a few real Cura screenshots).

    python3 tools/figures.py            # writes docs/images/fig*.png

Schematic figures say so in their titles; everything else is drawn from real G-code layers
(data/layers_*.json, made by tools/extract_layers.py), the benchmark table (data/benchmark.json)
or the tether sag simulation (data/tethersim_results.json).

Copyright Matthew Armstrong (https://github.com/The-Dorkknight). PolyForm Noncommercial 1.0.0. No warranty.
"""
import json
import math
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt                      # noqa: E402
import numpy as np                                   # noqa: E402
from matplotlib.collections import LineCollection    # noqa: E402
from matplotlib.patches import FancyBboxPatch, Polygon, Rectangle   # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
DATA = os.path.join(ROOT, "data")
OUT = os.path.join(ROOT, "docs", "images")

# one bright palette for the whole paper
PART = "#8E9AB3"      # the thing you actually wanted to print
PART_E = "#5C6782"
TOWER = "#FF7A1A"     # Hybrid pedestals
CAP = "#2D6CDF"       # interface cap
TETHER = "#0FB5A4"    # tethers
CURA = "#B04FCF"      # Cura normal support
TREE = "#2BB34A"      # Cura tree support
WARN = "#FFB000"
BAD = "#E5384B"
INK = "#1F2433"
BG = "#FFFFFF"

plt.rcParams.update({
    "font.family": ["Inter", "DejaVu Sans"], "font.size": 10, "axes.edgecolor": "#C9CEDA",
    "axes.labelcolor": INK, "xtick.color": "#5A6072", "ytick.color": "#5A6072", "text.color": INK,
    "axes.titleweight": "bold", "axes.titlesize": 11, "figure.facecolor": BG, "axes.facecolor": BG,
    "savefig.facecolor": BG, "axes.spines.top": False, "axes.spines.right": False,
})
TITLE_FONT = {"fontfamily": "Poppins", "fontweight": "bold"}


def save(fig, name):
    p = os.path.join(OUT, name)
    fig.savefig(p, dpi=150, bbox_inches="tight", pad_inches=0.15)
    plt.close(fig)
    print("wrote", p)


def load(name):
    return json.load(open(os.path.join(DATA, name)))


def segs(ax, rec, kinds, colors, lw=0.7, box=None):
    for kind in kinds:
        a = np.array(rec.get(kind, []), float)
        if not len(a):
            continue
        if box is not None:
            x0, x1, y0, y1 = box
            m = ((a[:, 0] >= x0) & (a[:, 0] <= x1) & (a[:, 1] >= y0) & (a[:, 1] <= y1)) | \
                ((a[:, 2] >= x0) & (a[:, 2] <= x1) & (a[:, 3] >= y0) & (a[:, 3] <= y1))
            a = a[m]
        ax.add_collection(LineCollection(a.reshape(-1, 2, 2), colors=colors[kind], linewidths=lw, capstyle="round"))


def clean(ax, box):
    ax.set_xlim(box[0], box[1])
    ax.set_ylim(box[2], box[3])
    ax.set_aspect("equal")
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(True)
        s.set_color("#DDE1EA")


# ---------------------------------------------------------------- 1. support 101 (schematic)
def fig_support101():
    fig, axs = plt.subplots(1, 4, figsize=(13, 3.6))
    titles = ["Overhang", "Bridge", "Support", "Interface"]
    subs = ["past ~45 to 50 degrees the\nlayers have nothing below", "a span between two\nanchors: sags if too long",
            "a sacrificial structure\nbuilt to be thrown away", "the dense top layers that\nthe part actually sits on"]
    for ax, t, s in zip(axs, titles, subs):
        ax.set_xlim(0, 10)
        ax.set_ylim(-1.6, 8)
        ax.axis("off")
        ax.set_title(t, fontsize=13, color=INK, **TITLE_FONT)
        ax.text(5, -1.2, s, ha="center", va="center", fontsize=9, color="#5A6072")
        ax.add_patch(Rectangle((0, 0), 10, 0.35, color="#D7DCE6"))
    # overhang: stair of layers leaning out
    ax = axs[0]
    for i in range(14):
        x0 = 2 + max(0, i - 4) * 0.45
        ax.add_patch(Rectangle((x0, 0.35 + i * 0.45), 3, 0.42, color=PART if i < 9 else BAD, ec="white", lw=0.5))
    ax.annotate("droops", (7.6, 6.3), (8.2, 7.6), fontsize=9, color=BAD, arrowprops=dict(arrowstyle="->", color=BAD))
    # bridge
    ax = axs[1]
    ax.add_patch(Rectangle((0.5, 0.35), 1.6, 5, color=PART))
    ax.add_patch(Rectangle((7.9, 0.35), 1.6, 5, color=PART))
    xs = np.linspace(2.1, 7.9, 50)
    ax.plot(xs, 5.15 - 0.9 * np.sin(np.pi * (xs - 2.1) / 5.8), color=TETHER, lw=4, solid_capstyle="round")
    ax.annotate("sag", (5, 4.3), (5, 2.4), ha="center", fontsize=9, color=TETHER, arrowprops=dict(arrowstyle="->", color=TETHER))
    # support
    ax = axs[2]
    ax.add_patch(Rectangle((1, 5.6), 8, 1.2, color=PART))
    ax.add_patch(Rectangle((1.2, 0.35), 7.6, 5.0, color=CURA, alpha=0.25))
    for x in np.arange(1.4, 8.8, 0.55):
        ax.plot([x, x], [0.35, 5.35], color=CURA, lw=1.4)
    ax.text(5, 2.8, "zig-zag\nfill", ha="center", fontsize=10, color=CURA, fontweight="bold")
    # interface
    ax = axs[3]
    ax.add_patch(Rectangle((1, 6.3), 8, 1.2, color=PART))
    for i, (c, a) in enumerate([(CAP, 0.35), (CAP, 0.55), (CAP, 0.8), (CAP, 1.0)]):
        ax.add_patch(Rectangle((1.3, 4.3 + i * 0.45), 7.4, 0.38, color=c, alpha=a))
    for x in np.arange(1.6, 8.6, 1.4):
        ax.plot([x, x], [0.35, 4.3], color=TOWER, lw=2)
    ax.annotate("0.2 mm gap", (8.7, 6.15), (7.4, 7.9), fontsize=8, ha="center", arrowprops=dict(arrowstyle="->", color=INK))
    fig.suptitle("Figure 1. Four words you need for the rest of this paper (schematic)", x=0.01, y=1.04, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig01_support101.png")


# ---------------------------------------------------------------- 2. three ways to hold up a roof (schematic)
def fig_three_ways():
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.4))
    names = [("Block support", CURA, "Cura 'normal': fill the\nwhole space under the roof"),
             ("Tree support", TREE, "branches that merge\ninto trunks"),
             ("A pedestal (this paper)", TOWER, "hollow towers, wide hollow\nlobes, a thin interface cap")]
    for ax, (t, c, s) in zip(axs, names):
        ax.set_xlim(0, 20)
        ax.set_ylim(-3, 16)
        ax.axis("off")
        ax.set_title(t, color=c, fontsize=13, **TITLE_FONT)
        ax.text(10, -2.1, s, ha="center", fontsize=9.5, color="#4A5064")
        ax.add_patch(Rectangle((0, -0.4), 20, 0.4, color="#D7DCE6"))
        ax.add_patch(Rectangle((0.5, 0), 1.2, 14, color=PART))
        ax.add_patch(Rectangle((18.3, 0), 1.2, 14, color=PART))
        ax.add_patch(Rectangle((0.5, 14), 19, 1.3, color=PART))
    ax = axs[0]
    ax.add_patch(Rectangle((2.1, 0), 15.8, 13.6, color=CURA, alpha=0.18))
    for x in np.arange(2.4, 17.8, 0.6):
        ax.plot([x, x], [0, 13.6], color=CURA, lw=1)
    ax = axs[1]
    rng = np.random.default_rng(3)
    for root in (6.0, 14.0):
        for tip in np.linspace(root - 4, root + 3.5, 5):
            ys = np.linspace(0, 13.6, 30)
            xs = root + (tip - root) * np.clip((ys - 5) / 8.6, 0, 1) ** 1.6
            ax.plot(xs, ys, color=TREE, lw=2.6 - 0.25 * abs(tip - root), alpha=0.95)
        ax.plot([root, root], [0, 5], color=TREE, lw=5)
    ax = axs[2]
    for cx in (6.0, 14.0):
        ax.add_patch(Rectangle((cx - 0.9, 0), 1.8, 7, fc="white", ec=TOWER, lw=2.4))
        ax.add_patch(Polygon([[cx - 0.9, 7], [cx - 4.4, 12.6], [cx + 4.4, 12.6], [cx + 0.9, 7]], closed=True, fc="white", ec=TOWER, lw=2.4))
        ax.add_patch(Polygon([[cx - 2.6, 0], [cx - 0.9, 0], [cx - 0.9, 1.8]], fc=TOWER, ec=TOWER))
        ax.add_patch(Polygon([[cx + 2.6, 0], [cx + 0.9, 0], [cx + 0.9, 1.8]], fc=TOWER, ec=TOWER))
    ax.add_patch(Rectangle((1.8, 12.6), 16.4, 1.2, color=CAP))
    ax.annotate("interface cap", (16.5, 12.6), (16.0, 8.0), ha="center", color=CAP, fontsize=9.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=CAP))
    ax.annotate("hollow", (6, 3.5), (10, 3.8), ha="center", color=TOWER, fontsize=9.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=TOWER))
    fig.suptitle("Figure 2. Three ways to hold up a roof (schematic, side view)", x=0.01, y=1.04, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig02_three_ways.png")


# ---------------------------------------------------------------- 3. anatomy of a pedestal (schematic)
def fig_anatomy():
    fig, ax = plt.subplots(figsize=(9, 7.6))
    ax.set_xlim(-16, 16)
    ax.set_ylim(-2, 27)
    ax.axis("off")
    ax.add_patch(Rectangle((-16, -0.6), 32, 0.6, color="#D7DCE6"))
    ax.text(15.6, -1.5, "bed", ha="right", fontsize=9, color="#5A6072")
    ax.add_patch(Rectangle((-15, 23.4), 30, 2.4, color=PART))
    ax.text(0, 24.6, "YOUR PART", ha="center", va="center", color="white", fontsize=13, **TITLE_FONT)
    # cap layers
    cols = [(0.45, "lattice (slow, 20 mm/s)"), (0.6, "lattice, crossing"), (0.8, "50 % rings"), (1.0, "100 % top")]
    for i, (a, lab) in enumerate(cols):
        ax.add_patch(Rectangle((-12.5, 21.6 + i * 0.4), 25, 0.34, color=CAP, alpha=a))
    ax.text(13.2, 22.4, "interface cap\n4 layers = 0.8 mm\n(+0.2 mm air gap)", fontsize=9, color=CAP, va="center", fontweight="bold")
    # head (lobes flaring)
    ax.add_patch(Polygon([[-1.6, 12], [-12.5, 21.6], [12.5, 21.6], [1.6, 12]], fc="#FFF1E6", ec=TOWER, lw=2.4))
    ax.add_patch(Polygon([[-1.0, 12.4], [-11.4, 21.6], [11.4, 21.6], [1.0, 12.4]], fc="white", ec=TOWER, lw=1.2, ls="--"))
    ax.text(0, 18.2, "head: wide hollow lobes\nflaring at 45 degrees", ha="center", fontsize=10, color=TOWER, fontweight="bold")
    # trunk
    ax.add_patch(Rectangle((-1.6, 1.0), 3.2, 11, fc="#FFF1E6", ec=TOWER, lw=2.4))
    ax.add_patch(Rectangle((-1.0, 1.0), 2.0, 11, fc="white", ec=TOWER, lw=1.2, ls="--"))
    ax.annotate("trunk: a hollow tube,\n2 walls, nothing inside", (1.7, 7), (6.5, 8), fontsize=10, color=TOWER, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=TOWER))
    # gussets and foot
    for sgn in (-1, 1):
        ax.add_patch(Polygon([[sgn * 1.6, 1.0], [sgn * 6.6, 0], [sgn * 1.6, 6]], fc=TOWER, ec=TOWER, alpha=0.85))
    ax.add_patch(Rectangle((-7.5, 0), 15, 1.0, color=TOWER, alpha=0.35))
    ax.annotate("gussets + foot\nso it doesn't fall over", (-5, 1.3), (-14.5, 6.5), fontsize=10, color=TOWER, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=TOWER))
    ax.annotate("support blocker: stops Cura\nadding its own support here", (-9, 22.2), (-15.5, 15.2), fontsize=9, color="#5A6072",
                arrowprops=dict(arrowstyle="->", color="#5A6072"))
    ax.set_title("Figure 3. Anatomy of a pedestal (schematic, side cut)", loc="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig03_anatomy.png")


# ---------------------------------------------------------------- 4. real layers: Cura vs Hybrid at the same heights
def fig_slices_u150():
    sets = [("Cura normal", "layers_u150_cura.json", CURA), ("Cura tree", "layers_u150_tree.json", TREE),
            ("Hybrid lobes", "layers_u150_lobes.json", TOWER), ("Hybrid cone", "layers_u150_cone.json", TOWER),
            ("Hybrid branch", "layers_u150_branch.json", TOWER)]
    zs = ["60.0", "120.0"]
    fig, axs = plt.subplots(2, 5, figsize=(15, 6.4))
    a = np.array(load("layers_u150_cura.json")["60.0"]["part"], float)
    box = (a[:, [0, 2]].min() - 4, a[:, [0, 2]].max() + 4, a[:, [1, 3]].min() - 4, a[:, [1, 3]].max() + 4)
    for j, (name, f, c) in enumerate(sets):
        d = load(f)
        for i, z in enumerate(zs):
            ax = axs[i, j]
            rec = d[z]
            segs(ax, rec, ["part", "support", "tower", "cap"], {"part": PART_E, "support": c, "tower": c, "cap": CAP}, lw=0.6)
            clean(ax, box)
            if i == 0:
                ax.set_title(name, color=c, fontsize=12, **TITLE_FONT)
            if j == 0:
                ax.set_ylabel(f"z = {float(z):.0f} mm", fontsize=11)
    fig.suptitle("Figure 6. The same two layers of the 200 x 200 mm U (stem 150 mm), straight out of Cura's G-code, seen from above",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    fig.text(0.01, 0.005, "Grey: the U's legs. Every line drawn is a line the nozzle would print. Cura 5.13, Elegoo Neptune 4 profile, 0.2 mm layers.",
             fontsize=9, color="#5A6072")
    save(fig, "fig06_slices_u150.png")


# ---------------------------------------------------------------- 5. the lobe star (the outline formula, drawn)
def star_outline(angles, w, L, fillet, K=360):
    th = np.linspace(0, 2 * np.pi, K, endpoint=False)
    rad = None
    for a in angles:
        d = (th - a + np.pi) % (2 * np.pi) - np.pi
        r = np.zeros(K)
        # distance from the centre to the edge of a capsule (half-width w, length L) along each direction
        for k, dd in enumerate(d):
            ux, uy = math.cos(dd), math.sin(dd)
            ts = np.linspace(0, L + w, 600)
            px, py = ts * ux, ts * uy
            qx = np.clip(px, 0, L)
            inside = np.hypot(px - qx, py) <= w
            r[k] = ts[inside].max() if inside.any() else 0
        if rad is None:
            rad = r
        else:
            if fillet > 0:
                h = np.maximum(fillet - np.abs(rad - r), 0) / fillet
                rad = np.maximum(rad, r) + h * h * fillet / 4
            else:
                rad = np.maximum(rad, r)
    return th, rad


def fig_lobes():
    fig, axs = plt.subplots(1, 3, figsize=(13, 4.6))
    ax = axs[0]
    for k in range(6):                                # 0.6.1: thin 2-line webs from one centre
        a = k * np.pi / 3
        u = np.array([math.cos(a), math.sin(a)])
        n = np.array([-u[1], u[0]])
        pts = np.array([n * 0.4, n * 0.4 + u * 18, -n * 0.4 + u * 18, -n * 0.4])
        ax.add_patch(Polygon(pts, fc="#FFE3CF", ec=TOWER, lw=1.6))
    ax.add_patch(plt.Circle((0, 0), 1.3, fc="none", ec=BAD, lw=2.5))
    ax.annotate("sharp notches:\nstress concentrators", (1.0, 0.5), (8, 4), color=BAD, fontsize=9.5, fontweight="bold",
                arrowprops=dict(arrowstyle="->", color=BAD))
    ax.set_title("0.6.1: six thin webs", color=INK, fontsize=12, **TITLE_FONT)
    ax.text(0, -21.5, "0.8 mm thick: floppy across", ha="center", fontsize=9.5, color="#5A6072")
    for ax, (n, title) in zip(axs[1:], [(4, "0.6.2+: four rounded lobes"), (3, "three lobes, same rules")]):
        angs = [np.pi / 4 + 2 * np.pi * i / n for i in range(n)]
        th, r = star_outline(angs, 4.0, 15.0, 3.0)
        x, y = r * np.cos(th), r * np.sin(th)
        ax.fill(x, y, fc="#FFE3CF", ec=TOWER, lw=2.2)
        th2, r2 = star_outline(angs, 4.0 - 0.8, 15.0, 3.0)
        ax.plot(np.r_[r2 * np.cos(th2), r2[0]], np.r_[r2 * np.sin(th2), 0], color=TOWER, lw=1.2, ls="--")
        ax.set_title(title, color=INK, fontsize=12, **TITLE_FONT)
        ax.text(0, -21.5, "8 mm wide, 2 walls, 3 mm fillets", ha="center", fontsize=9.5, color="#5A6072")
    for ax in axs:
        ax.set_xlim(-21, 21)
        ax.set_ylim(-23, 21)
        ax.set_aspect("equal")
        ax.axis("off")
    axs[1].annotate("smooth join", (5.0, 0.0), (10.5, -0.6), color=TOWER, fontsize=9.5, fontweight="bold",
                    arrowprops=dict(arrowstyle="->", color=TOWER))
    fig.suptitle("Figure 5. The head seen from above: why the lobes got fat (outlines from the plug-in's formula)",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig05_lobes.png")


# ---------------------------------------------------------------- 6. the interface cap, real layers
def fig_cap_layers():
    d = load("layers_u150_lobes.json")
    zs = ["149.0", "149.2", "149.4", "149.6", "149.8"]
    labels = ["last tower layer", "cap 1: lattice\n(20 mm/s)", "cap 2: lattice\nacross", "cap 3: 50 % rings", "cap 4: 100 % top"]
    fig, axs = plt.subplots(1, 5, figsize=(15, 3.9))
    a = np.array(d["60.0"]["part"], float)
    box = (a[:, [0, 2]].min() - 3, a[:, [0, 2]].max() + 3, a[:, [1, 3]].min() - 3, a[:, [1, 3]].max() + 3)
    for ax, z, lab in zip(axs, zs, labels):
        segs(ax, d[z], ["part", "tower", "cap"], {"part": PART_E, "tower": TOWER, "cap": CAP}, lw=0.45)
        clean(ax, box)
        ax.set_title(lab, fontsize=10.5, color=CAP if "cap" in lab else TOWER, **TITLE_FONT)
    fig.suptitle("Figure 7. The interface cap, layer by layer (real G-code, the whole 200 x 200 mm roof of the U, from above)",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig07_cap_layers.png")


# ---------------------------------------------------------------- 7. tethers on the test plate, real layers
def fig_tethers_plate():
    d = load("layers_plate.json")
    zs = ["5.9", "10.1", "14.3", "14.5", "14.7", "14.9"]
    labels = ["strips, z 5.9", "strips, z 10.1", "cap 1: lattice", "cap 2: lattice", "cap 3: rings", "cap 4: top"]
    fig, axs = plt.subplots(1, 6, figsize=(15.5, 3.4))
    box = (93, 142, 52, 98)
    for ax, z, lab in zip(axs, zs, labels):
        c = TETHER if "strips" in lab else CAP
        segs(ax, d[z], ["part", "support", "cap"], {"part": PART_E, "support": c, "cap": CAP}, lw=0.8, box=box)
        clean(ax, box)
        ax.set_title(lab, fontsize=10.5, color=TETHER if "strips" in lab else CAP, **TITLE_FONT)
    fig.suptitle("Figure 9. Tethers on the 40 mm test channel: wall-to-wall strips, then the cap (real G-code, seen from above)",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig09_tethers_plate.png")


# ---------------------------------------------------------------- 8. tethers: when they work (schematic)
def fig_tethers_where():
    fig, axs = plt.subplots(1, 3, figsize=(14, 4.4), gridspec_kw={"width_ratios": [1, 2.2, 2.2]})

    def setup(ax, W, title, sub, col):
        ax.set_xlim(-W * 0.04, W * 1.04)
        ax.set_ylim(-14, 92)
        ax.axis("off")
        ax.set_title(title, loc="left", fontsize=12, color=INK, **TITLE_FONT)
        ax.text(0, 0.99, sub, transform=ax.transAxes, fontsize=9.5, color=col, va="top", fontweight="bold")

    ax = axs[0]
    setup(ax, 48, "A. 40 mm test channel", "Tethers build", TETHER)
    ax.set_ylim(-6, 34)
    ax.add_patch(Rectangle((0, 0), 3.5, 18, color=PART))
    ax.add_patch(Rectangle((44.5, 0), 3.5, 18, color=PART))
    ax.add_patch(Rectangle((0, 18), 48, 3.5, color=PART))
    for i in range(3):
        ax.plot([3.5, 44.5], [7 + i * 0.6, 7 + i * 0.6], color=TETHER, lw=2.4)
    ax.add_patch(Rectangle((3.5, 17), 41, 0.8, color=CAP))
    ax.annotate("", (3.5, 3), (44.5, 3), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(24, -2.5, "41 mm: easy", ha="center", fontsize=9)
    ax = axs[1]
    setup(ax, 200, "B. 200 mm U, stem 150 mm", "Refused: 180 mm between the legs is past\nthe 110 mm hard limit, so it uses lobes", BAD)
    ax.add_patch(Rectangle((0, 0), 10, 60, color=PART))
    ax.add_patch(Rectangle((190, 0), 10, 60, color=PART))
    ax.add_patch(Rectangle((0, 60), 200, 6, color=PART))
    ax.plot([10, 190], [45, 45], color=BAD, lw=2.4, ls=(0, (5, 3)))
    ax.annotate("", (10, 22), (190, 22), arrowprops=dict(arrowstyle="<->", color=INK))
    ax.text(100, 25, "180 mm of fresh air", ha="center", fontsize=9, color=BAD)
    ax.text(100, 6, "(side view, squashed: the real stem is 150 mm tall)", ha="center", fontsize=8, color="#5A6072")
    ax = axs[2]
    setup(ax, 200, "C. 200 mm table top on one stem", "Refused: no walls near the roof to\ntie a strip to, so it uses lobes", BAD)
    ax.add_patch(Rectangle((85, 0), 30, 60, color=PART))
    ax.add_patch(Rectangle((0, 60), 200, 6, color=PART))
    ax.text(42, 40, "nothing to\ntie to", ha="center", fontsize=9.5, color=BAD)
    ax.text(158, 40, "nor here", ha="center", fontsize=9.5, color=BAD)
    fig.suptitle("Figure 10. Tethers need two facing walls, not too far apart (schematic, side view)",
                 x=0.01, y=1.06, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig10_tethers_where.png")


# ---------------------------------------------------------------- 9. span tiers on the sag simulation
def fig_span_tiers():
    sim = load("tethersim_results.json")["results"]["speed"]
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.axvspan(0, 90, color=TETHER, alpha=0.10)
    ax.axvspan(90, 110, color=WARN, alpha=0.20)
    ax.axvspan(110, 160, color=BAD, alpha=0.10)
    ax.text(45, 2.72, "builds", ha="center", color=TETHER, fontsize=11, **TITLE_FONT)
    ax.text(100, 2.72, "builds,\nwith a warning", ha="center", va="center", color="#B07A00", fontsize=10, **TITLE_FONT)
    ax.text(135, 2.72, "refused:\nuses lobes", ha="center", va="center", color=BAD, fontsize=10, **TITLE_FONT)
    styles = {"Neptune 4": ("-", [("20", "#7A3FE0"), ("40", "#2D6CDF")]), "Ender 3": ("--", [("10", "#FF7A1A"), ("20", "#E5384B")])}
    for printer, (ls, speeds) in styles.items():
        for sp, c in speeds:
            rows = sim[printer][sp]
            xs = [r["span"] for r in rows]
            ys = [r["final"] for r in rows]
            ax.plot(xs, ys, ls, color=c, lw=2.2, marker="o", ms=3.5, label=f"{printer}, {sp} mm/s")
    ax.axhline(0.45, color=INK, lw=1, ls=":")
    ax.text(3, 0.5, "0.45 mm: about what 5 layers can catch up (sim)", fontsize=8.5, color=INK)
    ax.set_xlim(0, 160)
    ax.set_ylim(0, 3.0)
    ax.set_xlabel("wall-to-wall span (mm)")
    ax.set_ylabel("predicted mid-span sag of the first strand (mm)")
    ax.legend(frameon=False, loc="upper left", bbox_to_anchor=(0.0, 0.88))
    ax.set_title("Figure 11. The tether span rules over the sag simulation\n(PLA, 0.4 mm nozzle, 0.2 mm layers; a model, not a measurement)",
                 loc="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig11_span_tiers.png")


# ---------------------------------------------------------------- 10-11. the benchmark
BENCH_PARTS = ["U 200x200\nstem 50 mm", "U 200x200\nstem 150 mm", "Table top 200x200\nstem 150 mm"]


def fig_bench():
    b = load("benchmark.json")
    names = ["Cura normal", "Cura tree", "Hybrid lobes", "Hybrid cone", "Hybrid branch", "Hybrid tethers"]
    cols = [CURA, TREE, TOWER, "#FFB36B", "#C9A27A", TETHER]
    for key, fname, ylabel, title in [
        ("filament_m", "fig12_bench_filament.png", "support filament (metres of 1.75 mm PLA)",
         "Figure 12. Plastic spent on support (Cura 5.13, Neptune 4, sliced, not printed)"),
        ("job_min", "fig13_bench_time.png", "whole print, hours (distance / feed-rate model)",
         "Figure 13. Time for the whole job, part included (same slices)")]:
        fig, ax = plt.subplots(figsize=(11, 5))
        w = 0.14
        for i, (n, c) in enumerate(zip(names, cols)):
            src = "Hybrid lobes" if n == "Hybrid tethers" else n       # tethers refused all three parts: lobes were built
            vals = [b[p][src][key] / (60 if key == "job_min" else 1) for p in ("U50", "U150", "TABLE150")]
            if n == "Hybrid tethers":
                bars = ax.bar(np.arange(3) + (i - 2.5) * w, vals, w, label="Hybrid tethers (refused: fell back to lobes)",
                              color="white", edgecolor=c, hatch="////", linewidth=1.2)
            else:
                bars = ax.bar(np.arange(3) + (i - 2.5) * w, vals, w, label=n, color=c, edgecolor="white", linewidth=0.6)
            ax.bar_label(bars, fmt="%.0f" if key == "filament_m" else "%.1f", fontsize=7, padding=1.5)
        if key == "job_min":
            for k, p in enumerate(("U50", "U150", "TABLE150")):
                bare = b[p]["bare_min"] / 60
                ax.plot([k - 0.45, k + 0.45], [bare, bare], color=INK, lw=1.4, ls="--")
                ax.text(k + 0.47, bare, "part alone", fontsize=7.5, va="center")
        ax.set_xticks(range(3))
        ax.set_xticklabels(BENCH_PARTS)
        ax.set_ylabel(ylabel)
        ax.legend(frameon=False, ncol=3, loc="upper center", bbox_to_anchor=(0.5, -0.17))
        ax.set_title(title, loc="left", fontsize=12, **TITLE_FONT)
        save(fig, fname)


def fig_channel():
    d = load("benchmark_channel100.json")
    names = ["Cura tree", "Cura sparse (5 %, no roof)", "Hybrid cone", "Hybrid branch", "Hybrid lobes", "Hybrid tethers"]
    cols = [TREE, CURA, "#FFB36B", "#C9A27A", TOWER, TETHER]
    fig, axs = plt.subplots(1, 2, figsize=(12, 4.4))
    for ax, h in zip(axs, ("100", "150")):
        vals = [d[h][n][1] for n in names]
        bars = ax.barh(range(len(names)), vals, color=cols, edgecolor="white")
        ax.bar_label(bars, fmt="%.1f m", fontsize=9, padding=3)
        ax.set_yticks(range(len(names)))
        ax.set_yticklabels(names if h == "100" else [""] * len(names))
        ax.set_xlim(0, 48)
        ax.set_xlabel("support filament (m)")
        ax.set_title(f"roof {h} mm up", fontsize=11, **TITLE_FONT)
    fig.suptitle("Figure 15. Where tethers can work: a 100 x 100 mm channel roof between two walls (Cura 5.13, sliced before the cap stack existed)",
                 x=0.01, y=1.03, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig15_channel_tethers.png")


def fig_height():
    b = load("benchmark.json")
    fig, ax = plt.subplots(figsize=(9, 4.6))
    for n, c in [("Cura normal", CURA), ("Cura tree", TREE), ("Hybrid lobes", TOWER)]:
        ys = [b["U50"][n]["filament_m"], b["U150"][n]["filament_m"]]
        ax.plot([50, 150], ys, "-o", color=c, lw=3, ms=8, label=n)
        ax.text(153, ys[1], f"{ys[1]:.0f} m", va="center", color=c, fontsize=10, fontweight="bold")
        off = {"Cura tree": -9, "Hybrid lobes": 9}.get(n, 0)
        ax.text(45, ys[0] + off, f"{ys[0]:.0f} m", va="center", ha="right", color=c, fontsize=10, fontweight="bold")
    ax.set_xlim(25, 175)
    ax.set_xticks([50, 150])
    ax.set_xticklabels(["stem 50 mm", "stem 150 mm"])
    ax.set_ylabel("support filament (m)")
    ax.legend(frameon=False)
    ax.set_title("Figure 14. Tripling the height: who pays for the extra 100 mm (200 mm U)", loc="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig14_height.png")


# ---------------------------------------------------------------- 12. real Cura screenshots, cropped
def fig_cura_shots(shots_dir):
    from PIL import Image
    crops = [("U200_h150/lobes/02_generated.png", (430, 118, 935, 495), "Lobes: the plug-in's towers in Cura"),
             ("U200_h150/lobes/03_preview.png", (400, 118, 945, 495), "The same, sliced (Cura's layer view)")]
    fig, axs = plt.subplots(1, 2, figsize=(13, 5))
    for ax, (p, box, t) in zip(axs, crops):
        im = Image.open(os.path.join(shots_dir, p)).convert("RGB").crop(box)
        ax.imshow(im)
        ax.axis("off")
        ax.set_title(t, fontsize=11, **TITLE_FONT)
    fig.suptitle("Figure 4. The 200 x 200 mm U, stem 150 mm, with Hybrid lobes (Cura 5.13 screenshots; red = walls)",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig04_cura_u150.png")
    heads = [("mushroom200_h150/lobes/02_generated.png", "Lobes"), ("mushroom200_h150/cone/02_generated.png", "Cone"),
             ("mushroom200_h150/branch/02_generated.png", "Branch")]
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.6))
    for ax, (p, t) in zip(axs, heads):
        im = Image.open(os.path.join(shots_dir, p)).convert("RGB").crop((452, 118, 935, 495))
        ax.imshow(im)
        ax.axis("off")
        ax.set_title(t, fontsize=12, color=TOWER, **TITLE_FONT)
    fig.suptitle("Figure 8. Three heads under the 200 mm table top on a 30 mm stem (Cura 5.13 screenshots)",
                 x=0.01, ha="left", fontsize=12, **TITLE_FONT)
    save(fig, "fig08_heads_table.png")


if __name__ == "__main__":
    import sys
    os.makedirs(OUT, exist_ok=True)
    fig_support101()
    fig_three_ways()
    fig_anatomy()
    fig_lobes()
    fig_slices_u150()
    fig_cap_layers()
    fig_tethers_plate()
    fig_tethers_where()
    fig_span_tiers()
    fig_bench()
    fig_height()
    fig_channel()
    shots = sys.argv[1] if len(sys.argv) > 1 else os.path.join(DATA, "shots")
    if os.path.isdir(shots):
        fig_cura_shots(shots)
