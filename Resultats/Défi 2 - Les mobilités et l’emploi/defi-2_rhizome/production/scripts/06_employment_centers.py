from export_paths import export_paths

PNG, PDF = export_paths("06_poles_emploi_2015_2025")

from map_theme import *
from map_utils import BASE
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, FancyBboxPatch

com, dep, riv, fer, gar = load()
com["km2"] = com.area / 1e6; com["pt"] = com.geometry.representative_point()
SEUIL = 10000
# Sources complémentaires (récupérées le 09/11/2026)
I = {}
for t in open((BASE / "insee_emploi_rp_2017_2023.txt")).read().strip().split(","):
    c, a, b, x, y = t.split(":"); I[c] = (int(a), int(b), int(x), int(y))
INSEE = {"2017": (5720649, 630178), "2023": (6029602, 712304)}          # emploi total au lieu de travail, dont non-salariés (RP)
AE = {"2015": (212191, 116115), "2025": (706791, 325509)}               # auto-entrepreneurs Urssaf, adm. actifs / éco. actifs, fin d'année
DEFM = (972835, 1015850)                                                # France Travail, cat. A B C, moyennes du 4e trimestre 2016 / 2024, sommes de valeurs communales arrondies

BINS = [(0, 100, "#F1EFEA", "Moins de 100"), (100, 500, "#DCE3EC", "100 à 500"), (500, 2000, "#B3C3D9", "500 à 2 000"), (2000, 1e9, "#7F9BC2", "Plus de 2 000")]
def dcol(v):
    for a, b, c, _ in BINS:
        if a <= v < b: return c
K = 0.011

fig = plt.figure(figsize=(18, 11.5), facecolor=NIGHT)
fig.text(0.03, 0.955, "06", fontsize=12, color=YEL, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.958, "Les pôles d'emploi en 2015 et en 2025", fontsize=30, color=WHITE, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.905, "Fond : densité d'emplois salariés privés par commune. Cercles : pôles d'au moins 10 000 emplois. En dix ans, 14 communes ont franchi ce seuil, surtout en grande couronne.", fontsize=13.5, color="#4B5563", va="top")
fig.patches.append(FancyBboxPatch((0.72, 0.075), 0.255, 0.77, boxstyle="square,pad=0", transform=fig.transFigure, fc=PANEL, ec=FRAME, lw=1.2, zorder=-5))

X0, X1, YC = 612000, 694000, 6857000
new_poles = set(com[(com.emploi_2025 >= SEUIL) & (com.emploi_2015 < SEUIL)].code)
for i, y in enumerate((2015, 2025)):
    ax = fig.add_axes([0.015 + i * 0.352, 0.075, 0.345, 0.77]); ax.set_facecolor(NIGHT); ax.set_axis_off()
    v = com[f"emploi_{y}"]
    com.plot(ax=ax, color=[dcol(d) for d in v / com.km2], edgecolor="#FFFFFF", linewidth=.25, zorder=0)
    dep.boundary.plot(ax=ax, color="#D9739F", linewidth=.7, alpha=.8, zorder=1)
    fer[(fer.an <= y) & (fer["mode"] != "TER")].plot(ax=ax, color="#9AA0A8", linewidth=.45, zorder=2)
    p = com[(v >= SEUIL)].copy(); p["v"] = p[f"emploi_{y}"]; p = p.sort_values("v", ascending=False)
    for _, r in p.iterrows():
        s = np.sqrt(r.v) * K * 60
        if r.code == "75056":
            ax.scatter(r.pt.x, r.pt.y, s=s, facecolor="none", edgecolor="#A86F00", linewidth=1.2, zorder=4)
        else:
            nw = y == 2025 and r.code in new_poles
            ax.scatter(r.pt.x, r.pt.y, s=s, color="#E69F00", alpha=.75, edgecolor="#D55E00" if nw else "#A86F00", linewidth=2 if nw else .6, zorder=5)
    h = (X1 - X0) * (0.77 * 11.5) / (0.345 * 18); ax.set_xlim(X0, X1); ax.set_ylim(YC - h / 2, YC + h / 2)
    top = p[p.code != "75056"].head(6)
    pr = com[com.code == "75056"].iloc[0]
    t = ax.text(pr.pt.x, pr.pt.y + 600, f"PARIS\n{fr(pr[f'emploi_{y}'] / 1e6, 2, sign=False)} million", fontsize=8.5, color=WHITE, ha="center", va="center", fontfamily=COND, fontweight="bold", zorder=19, linespacing=1.1)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground="#FFFFFF")])
    if y == 2025:
        for _, r in com[com.code.isin(new_poles)].iterrows():
            tt = ax.text(r.pt.x, r.pt.y - 1700, r.nom, fontsize=6.4, color="#8A3B00", ha="center", zorder=18)
            tt.set_path_effects([pe.withStroke(linewidth=2.2, foreground="#FFFFFF")])
    ax.text(X0 + 2500, YC + h / 2 - 4500, str(y), fontsize=34, color=WHITE, fontfamily=COND, fontweight="bold", zorder=30, bbox=dict(fc=NIGHT, ec="none", pad=1, alpha=.9))
    ax.text(X0 + 2500, YC + h / 2 - 8200, f"{len(p)} pôles · {fr(v.sum() / 1e6, 2, sign=False)} millions d'emplois salariés privés", fontsize=10.5, color="#374151", zorder=30, bbox=dict(fc=NIGHT, ec="none", pad=1.5, alpha=.9))
    if i == 1: compass(ax, X1 - 3500, YC + h / 2 - 5000); scalebar(ax, X0 + 2500, YC - h / 2 + 2200)

panel_title(fig, 0.83, "L'emploi francilien en chiffres")
def row(y, label, a, b, src, unit=""):
    fig.text(0.737, y, label, fontsize=10.2, color=WHITE, va="top", fontweight="bold")
    fig.text(0.737, y - 0.021, src, fontsize=8.3, color=MUTE, va="top")
    fig.text(0.958, y, f"{fr(a / 1000, 0, sign=False)} k  à  {fr(b / 1000, 0, sign=False)} k", fontsize=10, color=WHITE, va="top", ha="right")
    fig.text(0.958, y - 0.021, f"{fr((b / a - 1) * 100, 0)} %", fontsize=10.5, color="#D55E00" if b > a else "#0072B2", va="top", ha="right", fontfamily=COND, fontweight="bold")
row(0.785, "Emplois salariés privés", com.emploi_2015.sum(), com.emploi_2025.sum(), "Urssaf, fin 2015 à fin 2025")
row(0.735, "Emploi total (public compris)", INSEE["2017"][0], INSEE["2023"][0], "INSEE, recensement 2017 à 2023")
row(0.685, "dont non-salariés", INSEE["2017"][1], INSEE["2023"][1], "INSEE, recensement 2017 à 2023")
row(0.635, "Auto-entrepreneurs inscrits", AE["2015"][0], AE["2025"][0], "Urssaf, fin 2015 à fin 2025")
row(0.585, "Demandeurs d'emploi (A, B, C)", DEFM[0], DEFM[1], "France Travail / DARES, moyennes du 4e trimestre 2016 et 2024")
ptitle(fig, 0.525, "Lecture")
items = [Patch(facecolor=c, edgecolor="#D0CBC1", label=f"{l} emplois / km²") for *_, c, l in BINS]
items += [Line2D([], [], marker="o", ls="", mfc="#E69F00", mec="#A86F00", ms=10, alpha=.8, label="Pôle d'au moins 10 000 emplois"),
          Line2D([], [], marker="o", ls="", mfc="#E69F00", mec="#D55E00", mew=2, ms=10, label="Nouveau pôle depuis 2015"),
          Line2D([], [], color="#9AA0A8", lw=1.2, label="Réseau ferré de l'année")]
lg = fig.legend(handles=items, loc="upper left", bbox_to_anchor=(0.73, 0.515), frameon=False, fontsize=9.5, labelspacing=.6)
for t in lg.get_texts(): t.set_color(WHITE)
ptitle(fig, 0.345, "Premiers pôles hors Paris, emplois privés")
tp = com[com.code != "75056"].sort_values("emploi_2025", ascending=False).head(6); yy = 0.32
for _, r in tp.iterrows():
    fig.text(0.737, yy, r.nom, fontsize=9.6, color=WHITE, va="top")
    fig.text(0.958, yy, f"{fr(r.emploi_2015 / 1000, 0, sign=False)} k  à  {fr(r.emploi_2025 / 1000, 0, sign=False)} k", fontsize=9.6, color=WHITE, va="top", ha="right")
    yy -= 0.021
ptitle(fig, 0.185, "À retenir")
ptext(fig, 0.162, "Les grands pôles restent à l'ouest (La Défense) et au\nnord (Saint-Denis, Roissy). Les nouveaux pôles naissent\nen grande couronne (Brétigny, Lieusaint, Serris).\nLes auto-entrepreneurs ont été multipliés par 3.", 9.8)
footer(fig, "Sources : Urssaf — effectifs salariés du secteur privé par commune au 31/12/2015 et au 31/12/2025, auto-entrepreneurs par département (fin d'année) ; INSEE — recensement de la population, emploi au lieu de travail 2017 et 2023 (API Melodi) ; "
            "France Travail / DARES — demandeurs d'emploi A, B, C : moyennes du 4e trimestre, sommes de valeurs communales arrondies au multiple de 5 ; Île-de-France Mobilités — réseau ferré. Les chiffres 2026 ne sont pas encore publiés : fin 2025 est la donnée la plus récente. Pôle : commune d'au moins 10 000 emplois salariés privés.")
fig.savefig(PNG, dpi=300, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok")
