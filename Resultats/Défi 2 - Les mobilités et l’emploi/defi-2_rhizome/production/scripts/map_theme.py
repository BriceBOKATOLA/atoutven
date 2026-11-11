# Charte graphique de l’atlas
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.patches import FancyBboxPatch, Rectangle
from matplotlib.colors import LinearSegmentedColormap
import numpy as np, pandas as pd, geopandas as gpd, textwrap, json
from scipy.ndimage import gaussian_filter
from map_utils import load, short, clean, fr, COND, BODY

plt.rcParams.update({"font.family": [BODY, "DejaVu Sans"], "pdf.fonttype": 42, "axes.unicode_minus": True})

NIGHT = "#F6F4EF"; PANEL = "#FFFFFF"; COMM = "#E9E6DF"; COMM_EDGE = "#FBFAF7"; PARIS = "#DCD8CF"
FRAME = "#2E6BFF"; PINK = "#FF2E88"; YEL = "#C28E00"; WHITE = "#0E1B2C"; MUTE = "#6B7280"; OLDNET = "#B5B0A5"; LABEL = "#FFD400"
GAIN = "#F2B800"; LOSS = "#FF2E88"

def lbl(res):
    s = short(res)
    if s.startswith("M"): return "Métro " + s[1:]
    if s.startswith("T"): return "Tram " + s
    return s

def lighten(hexcol, t):
    h = hexcol.lstrip("#"); c = [int(h[i:i+2], 16) for i in (0, 2, 4)]
    return "#" + "".join(f"{int(v + (255 - v) * t):02x}" for v in c)

def lum(hexcol):
    h = hexcol.lstrip("#"); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    return .2126 * r + .7152 * g + .0722 * b

def glow_line(ax, gdf, color, core=2.0, z=5):
    halo = lighten(color, .45) if lum(color) < .35 else color
    for w, a in ((10, .10), (5.5, .30)):
        gdf.plot(ax=ax, color=halo, linewidth=w, alpha=a, zorder=z, capstyle="round")
    gdf.plot(ax=ax, color=color, linewidth=core, zorder=z + 1, capstyle="round")
    gdf.plot(ax=ax, color="white", linewidth=core * .35, alpha=.55, zorder=z + 2)

def yl(ax, x, y, txt, size=7.4, color=YEL, ha="left", z=20, weight="semibold"):
    size = min(size, 7.6)
    box = LABEL if color == YEL else color; fg = WHITE if color == YEL else "#FFFFFF"
    t = ax.text(x, y, txt, fontsize=size, color=fg, fontfamily=COND, fontweight=weight, ha=ha, va="center", zorder=z,
                bbox=dict(boxstyle="square,pad=0.12", fc=box, ec="none", alpha=.93))
    return t

def night_lights(ax, com, weight, extent, sigma=3.6, res=700, cmap=None, alpha=.85, z=1):
    pts = com.geometry.representative_point()
    x0, x1, y0, y1 = extent
    H, xe, ye = np.histogram2d(pts.y, pts.x, bins=[int(res * (y1 - y0) / (x1 - x0)), res], range=[[y0, y1], [x0, x1]], weights=weight)
    H = gaussian_filter(H, sigma); H = np.log1p(H); H = H / H.max()
    cmap = cmap or LinearSegmentedColormap.from_list("nl", [(0, (0, 0, 0, 0)), (.22, (.45, .42, .38, 0)), (.5, (.45, .42, .38, .10)), (.8, (.38, .35, .32, .22)), (1, (.3, .28, .26, .32))])
    ax.imshow(H, extent=(x0, x1, y0, y1), origin="lower", cmap=cmap, alpha=alpha, zorder=z, interpolation="bilinear")

def basemap(ax, com, dep, fill=None):
    com.plot(ax=ax, color=fill if fill is not None else COMM, edgecolor=COMM_EDGE, linewidth=0.3, zorder=0)
    p = com[com.code == "75056"]
    if fill is None: p.plot(ax=ax, color=PARIS, edgecolor=COMM_EDGE, linewidth=0.3, zorder=0.5)
    b = dep.boundary
    b.plot(ax=ax, color="#D9739F", linewidth=.7, alpha=.8, zorder=2.1)

def dep_names(ax, dep, X0, X1, Y0, Y1):
    for _, d in dep.iterrows():
        c = d.geometry.representative_point()
        if X0 + 4000 < c.x < X1 - 4000 and Y0 + 4000 < c.y < Y1 - 4000 and d.code != "75":
            t = ax.text(c.x, c.y, d.nom.upper(), fontsize=8.5, color="#4B5563", alpha=.75, ha="center", fontfamily=COND, fontweight="semibold", zorder=3)
    t = ax.text(651800, 6862200, "PARIS", fontsize=13, color=WHITE, alpha=.85, ha="center", fontfamily=COND, fontweight="bold", zorder=19)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground=NIGHT)])
    return t

def compass(ax, x, y, r=2200):
    star = [(0, r), (r * .18, r * .18), (r, 0), (r * .18, -r * .18), (0, -r), (-r * .18, -r * .18), (-r, 0), (-r * .18, r * .18)]
    ax.add_patch(plt.Polygon([(x + a, y + b) for a, b in star], color=WHITE, zorder=25))
    ax.text(x, y + r * 1.45, "N", color=WHITE, fontsize=9, ha="center", fontfamily=COND, fontweight="bold", zorder=25)

def scalebar(ax, x, y):
    for i, c in enumerate([WHITE, MUTE]):
        ax.add_patch(Rectangle((x + i * 2500, y), 2500, 350, color=c, zorder=25))
    for v, xx in ((0, x), (2.5, x + 2500), (5, x + 5000)):
        ax.text(xx, y + 900, f"{fr(v, 1 if v == 2.5 else 0, sign=False)}", color=WHITE, fontsize=8, ha="center", zorder=25)
    ax.text(x + 5700, y + 175, "km", color=WHITE, fontsize=8, va="center", zorder=25)

def plate(num, title, claim, figsize=(18, 11.5)):
    fig = plt.figure(figsize=figsize, facecolor=NIGHT)
    ax = fig.add_axes([0.015, 0.075, 0.69, 0.77]); ax.set_facecolor(NIGHT); ax.set_axis_off()
    fig.text(0.03, 0.955, num, fontsize=12, color=YEL, fontfamily=COND, fontweight="bold", va="top")
    fig.text(0.055, 0.958, title, fontsize=30, color=WHITE, fontfamily=COND, fontweight="bold", va="top")
    fig.text(0.055, 0.905, claim, fontsize=13.5, color="#4B5563", va="top")
    # panneau de légende encadré, titre dans un cadre bleu (signature du portfolio)
    fig.patches.append(FancyBboxPatch((0.72, 0.075), 0.255, 0.77, boxstyle="square,pad=0", transform=fig.transFigure, fc=PANEL, ec=FRAME, lw=1.2, zorder=-5))
    return fig, ax

def panel_title(fig, y, txt):
    fig.patches.append(FancyBboxPatch((0.735, y - 0.032), 0.225, 0.038, boxstyle="square,pad=0", transform=fig.transFigure, fc="none", ec=FRAME, lw=1.2))
    fig.text(0.8475, y - 0.013, txt, fontsize=12, color=WHITE, fontfamily=COND, fontweight="bold", ha="center", va="center")

def ptitle(fig, y, txt):
    fig.text(0.735, y, txt.upper(), fontsize=9.5, color=MUTE, fontfamily=COND, fontweight="semibold", va="top")

def ptext(fig, y, txt, size=10.5, color=WHITE, x=0.735, **kw):
    fig.text(x, y, txt, fontsize=size, color=color, va="top", linespacing=1.45, **kw)

def big(fig, x, y, num, label, color=YEL):
    fig.text(x, y, num, fontsize=28, color=color, fontfamily=COND, fontweight="bold", va="top")
    fig.text(x, y - 0.047, label, fontsize=9.5, color="#4B5563", va="top", linespacing=1.3)

def footer(fig, txt):
    fig.text(0.03, 0.058, "\n".join(textwrap.wrap(txt, 235)), fontsize=8, color=MUTE, va="top", linespacing=1.45)

# 3 périodes, couleurs très distinctes (palette Okabe-Ito, lisible par les daltoniens)
PERIODS = [(2015, 2018, "#009E73", "2015 – 2018"), (2019, 2021, "#0072B2", "2019 – 2021"), (2022, 2025, "#D55E00", "2022 – 2025")]
def pcol(an):
    for a, b, c, _ in PERIODS:
        if a <= an <= b: return c

def cased(ax, gdf, color, w=2.2, z=5):
    gdf.plot(ax=ax, color="#FFFFFF", linewidth=w + 2.2, zorder=z, capstyle="round")
    gdf.plot(ax=ax, color=color, linewidth=w, zorder=z + 1, capstyle="round")
