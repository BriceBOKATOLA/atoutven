from export_paths import export_paths

PNG, PDF = export_paths("03_avant_apres")

from map_theme import *
from map_utils import CLEAN
from matplotlib.lines import Line2D

E = json.load(open((CLEAN / "series_emploi_urssaf.json"))); Y = E["annees"]; ref = E["IDF hors communes desservies et Paris"]
G = json.load(open((CLEAN / "groupes_lignes.json")))
fer = load()[3]; fer["lg"] = fer.res_com.map(short)
COL = {}
for _, r in fer[fer.colourweb_hexa.notna()].iterrows(): COL.setdefault(r.lg, "#" + r.colourweb_hexa)
COL["M11"] = "#704B1C"
STAR = ["T11 (2017)", "M14 (2020)", "T4 (2019)"]
NAME = lambda k: {"M": "Métro ", "T": "Tram "}.get(G[k]["line"][0], "") + (G[k]["line"][1:] if G[k]["line"][0] == "M" else G[k]["line"]) if G[k]["line"] not in ("RER E", "Câble C1") else G[k]["line"]

def series(k):
    an = G[k]["an"]; b = Y.index(max(an - 1, 2015))
    return [(y - an, (E[k][i] / E[k][b] - ref[i] / ref[b]) * 100, y) for i, y in enumerate(Y)]

fig = plt.figure(figsize=(18, 11.5), facecolor=NIGHT)
fig.text(0.03, 0.955, "03", fontsize=12, color=YEL, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.958, "Le rail arrive, l'emploi suit. Plus tard.", fontsize=30, color=WHITE, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.905, "Écart de croissance de l'emploi entre les communes desservies et le reste de l'Île-de-France, selon le nombre d'années depuis l'ouverture de la ligne.", fontsize=13.5, color="#4B5563", va="top")
from matplotlib.patches import FancyBboxPatch
fig.patches.append(FancyBboxPatch((0.72, 0.075), 0.255, 0.77, boxstyle="square,pad=0", transform=fig.transFigure, fc=PANEL, ec=FRAME, lw=1.2, zorder=-5))

ax = fig.add_axes([0.07, 0.13, 0.6, 0.69]); ax.set_facecolor(NIGHT)
ax.axvspan(-3.5, 0, color="#ECE9E2", zorder=0)
ax.axhline(0, color=WHITE, lw=1.2, zorder=2); ax.axvline(0, color=WHITE, lw=1, ls=(0, (4, 3)), zorder=2)
for yv in range(-15, 20, 5): ax.axhline(yv, color="#E3DFD6", lw=.8, zorder=1)
gt = []
for k in G:
    if k in STAR: continue
    s = series(k); xs = [p[0] for p in s if p[0] >= -3]; ys = [p[1] for p in s if p[0] >= -3]
    pre = [(x, y) for x, y in zip(xs, ys) if x <= 0]; post = [(x, y) for x, y in zip(xs, ys) if x >= 0 or x == -1]
    ax.plot(*zip(*post), color="#BCC1CB", lw=1.4, zorder=3); ax.plot(*zip(*pre), color="#BCC1CB", lw=1, ls=(0, (2, 2)), zorder=3)
    ax.scatter(xs[-1], ys[-1], s=14, color="#9CA3AF", zorder=4)
    if 2025 - G[k]["an"] >= 3: gt.append(ax.text(xs[-1] + .15, ys[-1], f"{NAME(k)} {fr(ys[-1])}", fontsize=8.5, color="#6B7280", va="center", zorder=4))
for k in STAR:
    s = series(k); xs = [p[0] for p in s if p[0] >= -3]; ys = [p[1] for p in s if p[0] >= -3]; c = COL[G[k]["line"]]
    halo = lighten(c, .45) if lum(c) < .35 else c
    post = [(x, y) for x, y in zip(xs, ys) if x >= -1]; pre = [(x, y) for x, y in zip(xs, ys) if x <= -1]
    for w, a in ((10, .10), (5.5, .3)): ax.plot(*zip(*post), color=halo, lw=w, alpha=a, zorder=5, solid_capstyle="round")
    ax.plot(*zip(*post), color=halo, lw=3, zorder=6, solid_capstyle="round")
    if len(pre) > 1: ax.plot(*zip(*pre), color=halo, lw=1.6, ls=(0, (2, 2)), zorder=6)
    cov = [p for p in s if p[2] == 2020][0]
    if cov[0] >= -3: ax.scatter(cov[0], cov[1], s=40, facecolor=NIGHT, edgecolor=WHITE, lw=1.2, zorder=8)
    ax.scatter(xs[-1], ys[-1], s=60, color=halo, edgecolor=WHITE, lw=1, zorder=8)
    t = ax.text(xs[-1] + .2, ys[-1], f"{NAME(k)}{' nord' if k == 'M14 (2020)' else ''} | {fr(ys[-1])} pts", fontsize=12, color=YEL, fontfamily=COND, fontweight="bold", va="center", zorder=9)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground=NIGHT)])
ax.set_xlim(-3.5, 10.5)
from adjustText import adjust_text
adjust_text(gt, ax=ax, only_move={"text": "y"}, expand=(1.05, 1.4)); ax.set_ylim(-15, 18)
ax.set_xticks(range(-3, 10)); ax.set_xticklabels([("−" if v < 0 else "+" if v > 0 else "") + str(abs(v)) for v in range(-3, 10)])
ax.set_yticks(range(-15, 20, 5)); ax.set_yticklabels([("−" if v < 0 else "+" if v > 0 else "") + str(abs(v)) for v in range(-15, 20, 5)])
ax.tick_params(colors=MUTE, labelsize=10, length=0)
for s_ in ax.spines.values(): s_.set_visible(False)
ax.set_xlabel("Années depuis l'ouverture de la ligne", color=WHITE, fontsize=11, labelpad=10)
ax.set_ylabel("Écart avec le reste de la région (points)", color=WHITE, fontsize=11, labelpad=10)
ax.text(.1, 16.8, "Ouverture", color=WHITE, fontsize=11, fontfamily=COND, fontweight="bold")
ax.text(-1.75, 16.8, "AVANT L'OUVERTURE", color=MUTE, fontsize=9.5, fontfamily=COND, fontweight="semibold", ha="center")
ax.text(-3.3, 1.0, "Même rythme que la région", color=WHITE, fontsize=9, alpha=.8)
ax.annotate("Les communes décrochent\n2 à 5 ans après l'ouverture", xy=(3, 8.4), xytext=(.6, 12.5), color=YEL, fontsize=11, fontfamily=COND, fontweight="bold",
            arrowprops=dict(arrowstyle="-", color=YEL, lw=1))

panel_title(fig, 0.83, "Écart en 2025, ligne par ligne")
rows = sorted(G, key=lambda k: -series(k)[-1][1]); yy = 0.775
for k in rows:
    v = series(k)[-1][1]; rec = 2025 - G[k]["an"]
    fig.add_artist(Line2D([0.737, 0.749], [yy - 0.008, yy - 0.008], color=COL[G[k]["line"]], lw=4, transform=fig.transFigure))
    lab = G[k]["line"] + (f" · {G[k]['an']}" if G[k]["line"] == "M14" else "")
    fig.text(0.754, yy, lab, fontsize=10.5, color=WHITE, va="top")
    fig.text(0.835, yy, f"ouverte en {G[k]['an']}", fontsize=9, color=MUTE, va="top")
    fig.text(0.958, yy, f"{fr(v)} pts", fontsize=10.5, color=YEL if k in STAR else ("#4B5563" if v >= 0 else LOSS), va="top", ha="right", fontfamily=COND, fontweight="bold")
    yy -= 0.0262
ptitle(fig, 0.36, "Comment lire ce graphique")
ptext(fig, 0.335, "+13,4 pts pour le Tram T11 : ses communes ont\ngagné 13 emplois de plus pour 100 que le reste\nde la région, depuis l'année précédant l'ouverture.\n\nPointillés : avant l'ouverture, ces communes ne\nprogressaient pas plus vite que la région.\nCercle blanc : année 2020 (crise sanitaire).\n\nLes lignes ouvertes depuis 2021 ont trop peu\nde recul pour conclure (lignes grises\nsans étiquette, chiffres dans le tableau).", 9.8, "#4B5563")
footer(fig, "Méthode : communes contenant au moins une gare ouverte par la ligne cette année-là (Paris exclu). Écart = croissance de l'emploi des communes desservies − croissance du reste de l'Île-de-France (hors Paris et communes desservies), "
            "depuis l'année précédant l'ouverture. Corrélation, pas causalité : d'autres projets jouent aussi (ZAC, Jeux olympiques 2024). Sources : Urssaf, effectifs salariés privés par commune 2015-2025 ; Île-de-France Mobilités, dates de mise en service.")
fig.savefig(PNG, dpi=300, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok")
