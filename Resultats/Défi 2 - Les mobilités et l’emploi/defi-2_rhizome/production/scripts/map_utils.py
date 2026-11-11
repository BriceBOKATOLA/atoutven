from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "datasets" / "src"
CLEAN = Path(__file__).resolve().parent.parent / "datasets" / "clean" / "shared"

# Charte graphique commune de l'atlas (identique à la carte interactive)
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib import font_manager as fm
import matplotlib.patheffects as pe
import geopandas as gpd, pandas as pd, numpy as np, textwrap, re, json

for f in fm.findSystemFonts(fontpaths=["/root/.fonts"]):
    fm.fontManager.addfont(f)
BODY, COND = "Barlow", "Barlow Condensed"
plt.rcParams["font.family"] = [BODY, "DejaVu Sans"]
plt.rcParams["axes.unicode_minus"] = True

def fr(v, d=1, sign=True):
    """Nombre au format français : virgule décimale, vrai signe moins, espace des milliers."""
    v = round(float(v), d)
    txt = f"{abs(v):,.{d}f}".replace(",", "\u202f").replace(".", ",")
    return ("+" if v > 0 and sign else "\u2212" if v < 0 else "") + txt

BG = "#F3F4F2"; SHEET = "#FFFFFF"; LAND = "#E4E6E2"; LAND2 = "#D9DCD6"; EDGE = "#F7F8F6"
INK = "#0E1B2C"; INK2 = "#3A4656"; MUTED = "#6B7480"; RULE = "#D3D7D2"; OLD = "#A3A9A3"
POS = "#1F6FB2"; NEG = "#C2412F"; DEP = MUTED; WATER = "#BFD3E0"

PERIODS = [(2015, 2018, "2015 – 2018", "#D99A00"),
           (2019, 2021, "2019 – 2021", "#DD5A1A"),
           (2022, 2023, "2022 – 2023", "#B0175C"),
           (2024, 2025, "2024 – 2025", "#4A1A7A")]

def period_color(y):
    for a, b, _, c in PERIODS:
        if a <= y <= b: return c
    return OLD

def text_on(hexcol):
    """Couleur de texte lisible (contraste WCAG) sur un fond donné."""
    h = hexcol.lstrip("#"); r, g, b = [int(h[i:i+2], 16) / 255 for i in (0, 2, 4)]
    lum = lambda c: c / 12.92 if c <= 0.03928 else ((c + 0.055) / 1.055) ** 2.4
    L = 0.2126 * lum(r) + 0.7152 * lum(g) + 0.0722 * lum(b)
    return "#FFFFFF" if (1.05) / (L + 0.05) >= (L + 0.05) / (0.0141 + 0.05) else INK

def clean(s):
    return re.sub(r"[​‌‍﻿]", "", str(s)).replace("’", "'").strip()

def load():
    com = gpd.read_file((CLEAN / "hackathon_emploi.gpkg")).to_crs(2154)
    dep = gpd.read_file((BASE / "dep_idf.geojson")).to_crs(2154)
    riv = gpd.read_file((BASE / "rivieres_idf.geojson")).to_crs(2154)
    fer = gpd.read_file((BASE / "reseau_ferre_idf.geojson")).to_crs(2154)
    gar = gpd.read_file((BASE / "gares_idf.geojson")).to_crs(2154)
    fer["an"] = pd.to_datetime(fer.date_mes, errors="coerce").dt.year
    gar["an"] = pd.to_datetime(gar.date_mise, errors="coerce").dt.year
    gar["nom_gares"] = gar.nom_gares.map(clean)
    off = json.load(open((BASE / "noms_officiels.json")))
    com["nom"] = com.code.map(off).fillna(com.nom).map(clean)
    return com, dep, riv, fer, gar

def short(res):
    return (res.replace("METRO ", "M").replace("TRAM ", "T").replace("CABLE ", "Câble C")
               .replace("TER GRAND-EST", "TER"))

def frame(title, subtitle, figsize=(18, 11.5)):
    """Carte à gauche (70 %), colonne d'information à droite."""
    fig = plt.figure(figsize=figsize, facecolor=BG)
    ax = fig.add_axes([0.02, 0.085, 0.70, 0.78]); ax.set_facecolor(BG); ax.set_axis_off()
    fig.text(0.03, 0.965, title, fontsize=30, fontfamily=COND, fontweight="bold", color=INK, va="top")
    fig.text(0.03, 0.912, subtitle, fontsize=13, color=INK2, va="top")
    fig.add_artist(plt.Line2D([0.03, 0.97], [0.885, 0.885], color=INK, lw=1.6))
    fig.add_artist(plt.Line2D([0.745, 0.745], [0.10, 0.86], color=RULE, lw=0.8))
    fig.text(0.97, 0.965, "HACKATHON MOBILITÉS 2026 · ÉQUIPE 16", fontsize=9, color=MUTED, ha="right", va="top", fontfamily=COND, fontweight="semibold")
    return fig, ax

def side_title(fig, y, txt):
    fig.text(0.765, y, txt.upper(), fontsize=10, color=MUTED, fontfamily=COND, fontweight="semibold", va="top")

def side_text(fig, y, txt, size=10.5, color=None, weight="normal", family=None):
    fig.text(0.765, y, txt, fontsize=size, color=color or INK, va="top", fontweight=weight, linespacing=1.45, fontfamily=family or BODY)

def big(fig, x, y, num, label, color=None):
    fig.text(x, y, num, fontsize=30, fontfamily=COND, fontweight="bold", color=color or INK, va="top")
    fig.text(x, y - 0.052, label, fontsize=10, color=INK2, va="top", linespacing=1.35)

def footer(fig, txt):
    fig.add_artist(plt.Line2D([0.03, 0.97], [0.06, 0.06], color=RULE, lw=0.8))
    fig.text(0.03, 0.05, "\n".join(textwrap.wrap(txt, 235)), fontsize=8, color=MUTED, va="top", linespacing=1.45)

def halo(t, w=2.6, c=BG):
    t.set_path_effects([pe.withStroke(linewidth=w, foreground=c)])
    return t

def badge(ax, x, y, txt, col, size=9.5, z=12):
    return ax.text(x, y, txt, fontsize=size, fontfamily=COND, fontweight="bold", color=text_on(col), ha="center", va="center", zorder=z,
                   bbox=dict(boxstyle="round,pad=0.28,rounding_size=0.25", fc=col, ec="white", lw=1.1))

def scalebar(ax, x, y, km=5):
    ax.plot([x, x + km * 1000], [y, y], color=INK, lw=2.2, solid_capstyle="butt", zorder=20)
    for xx in (x, x + km * 1000): ax.plot([xx, xx], [y - 250, y + 250], color=INK, lw=1.2, zorder=20)
    ax.text(x + km * 500, y + 700, f"{km} km", ha="center", fontsize=9, color=INK, zorder=20)

def north(ax, x, y):
    ax.annotate("N", xy=(x, y + 2800), xytext=(x, y), ha="center", fontsize=10, color=INK, fontweight="bold", fontfamily=COND,
                arrowprops=dict(arrowstyle="-|>", color=INK, lw=1.1), zorder=20)

def basemap(ax, com, dep, fill=None, xlim=None, ylim=None):
    com.plot(ax=ax, color=fill if fill is not None else LAND, edgecolor=EDGE, linewidth=0.35)
    dep.boundary.plot(ax=ax, color=MUTED, linewidth=0.8, alpha=0.7)
    if xlim: ax.set_xlim(*xlim); ax.set_ylim(*ylim)

def dep_labels(ax, dep, X0, X1, Y0, Y1):
    for _, d in dep.iterrows():
        c = d.geometry.representative_point()
        if X0 + 4000 < c.x < X1 - 4000 and Y0 + 4000 < c.y < Y1 - 4000 and d.code != "75":
            halo(ax.text(c.x, c.y, d.nom.upper(), fontsize=9, color="#8E959C", ha="center", fontfamily=COND, fontweight="semibold"), 2.4)
    return halo(ax.text(652300, 6862300, "PARIS", fontsize=14, color=INK2, ha="center", fontfamily=COND, fontweight="bold", zorder=11), 3)
