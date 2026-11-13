from export_paths import export_paths

PNG, PDF = export_paths("04_demandeurs_emplois")

from map_theme import *
from map_utils import BASE, CLEAN
from adjustText import adjust_text
from matplotlib.lines import Line2D
from matplotlib.patches import Patch, Rectangle

com, dep, riv, fer, gar = load()
new = fer[(fer.an >= 2015) & (fer.an <= 2025) & (~fer.res_com.str.contains("TER"))].copy(); new["lg"] = new.res_com.map(short)
old = fer[fer.an < 2015]
ng = gar[(gar.an >= 2015) & (gar.an <= 2025)].copy()
d = {}
for t in (BASE / "defm_2016_2024.txt").read_text(encoding="utf-8").strip().split(","):
    c, a, b = t.split(":"); d[c] = (int(a), int(b))
com["d16"] = com.code.map(lambda c: d.get(c, (None, None))[0]); com["d24"] = com.code.map(lambda c: d.get(c, (None, None))[1])
com["pct"] = (com.d24 / com.d16 - 1) * 100
S = json.loads((CLEAN / "series_defm_dares.json").read_text(encoding="utf-8")); A = S["annees"]; i16, i24 = A.index(2016), A.index(2024)
ev = lambda k: (S[k][i24] / S[k][i16] - 1) * 100
idf, t4, rest = ev("IDF"), ev("T4 (2019)"), ev("IDF hors desservies et Paris")
G = json.loads((CLEAN / "groupes_lignes.json").read_text(encoding="utf-8")); served = {c for v in G.values() for c in v["codes"]}

bins = [(-1e9, -5, "#2C7FB8", "Baisse de plus de 5 %"), (-5, 0, "#A6CEE3", "Baisse de 0 à 5 %"), (0, 5, "#FBE6CC", "Hausse de 0 à 5 %"),
        (5, 15, "#F5AE6B", "Hausse de 5 à 15 %"), (15, 1e9, "#D9531E", "Hausse de plus de 15 %")]
def colr(v):
    if pd.isna(v): return "#F1EFEA"
    for a, b, c, _ in bins:
        if a <= v < b: return c
com["fill"] = com.pct.apply(colr)

X0, X1, Y0, Y1 = 619000, 692000, 6825000, 6885000
fig, ax = plate("04", "Plus d'emplois, pas forcément moins de chômeurs",
                "Évolution du nombre de demandeurs d'emploi (catégories A, B, C) par commune, entre les moyennes du 4e trimestre 2016 et 2024. Les emplois créés près des gares ne profitent pas toujours aux habitants.")
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect("equal", adjustable="datalim")
basemap(ax, com, dep, fill=com.fill)
old.plot(ax=ax, color="#9CA3AF", linewidth=.7, zorder=3)
new.plot(ax=ax, color="#FFFFFF", linewidth=3.4, zorder=4); new.plot(ax=ax, color=WHITE, linewidth=1.3, zorder=5)
ng.plot(ax=ax, color="#FFFFFF", edgecolor=WHITE, markersize=14, linewidth=.8, zorder=6)
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)

# encadré jaune sur le Tram T4
t4c = com[com.code.isin(G["T4 (2019)"]["codes"])]
bx0, by0, bx1, by1 = t4c.total_bounds; pad = 900
ax.add_patch(Rectangle((bx0 - pad, by0 - pad), bx1 - bx0 + 2 * pad, by1 - by0 + 2 * pad, fill=False, ec=WHITE, lw=1.6, ls=(0, (5, 3)), zorder=12))
yl(ax, bx1 + pad + 600, by1 + pad + 1400, f"TRAM T4 | emplois {fr(9.6)} pts, demandeurs {fr(t4)} %", 11, z=22)

lab = com[com.code.isin(served) & (com.d16 >= 2000) & ~com.code.isin(G["T4 (2019)"]["codes"])].copy()
lab["pt"] = lab.geometry.representative_point()
lab = lab.reindex(lab.pct.abs().sort_values(ascending=False).index).head(10)
texts = [yl(ax, r.pt.x, r.pt.y, f"{r.nom} | {fr(r.pct, 0)} %", 9.3, YEL, ha="center") for _, r in lab.iterrows() if X0 < r.pt.x < X1 and Y0 < r.pt.y < Y1]
p = com[com.code == "75056"].iloc[0]
pt = ax.text(652500, 6861500, f"PARIS | {fr(p.pct, 0)} %", fontsize=9, color=WHITE, ha="center", fontfamily=COND, fontweight="bold", zorder=19)
pt.set_path_effects([pe.withStroke(linewidth=3, foreground=NIGHT)]); texts.append(pt)
adjust_text(texts, ax=ax, expand=(1.1, 1.3), max_move=(30, 30), arrowprops=dict(arrowstyle="-", color=MUTE, lw=.5))
compass(ax, X1 - 3500, Y1 - 5000); scalebar(ax, X0 + 2500, Y0 + 2200)

panel_title(fig, 0.83, "Demandeurs d'emploi, 2016-2024")
big(fig, 0.737, 0.775, f"{fr(idf)} %", "en Île-de-France\n" + f"{fr(S['IDF'][i16], 0, False)} à {fr(S['IDF'][i24], 0, False)}", color="#D9531E")
big(fig, 0.885, 0.775, f"{fr(t4)} %", f"autour du Tram T4\n(reste : {fr(rest)} %)", color=YEL)
ptitle(fig, 0.665, "Évolution par commune")
h = [Patch(facecolor=c, edgecolor=COMM_EDGE, label=l) for *_, c, l in bins] + [Patch(facecolor="#F1EFEA", edgecolor=COMM_EDGE, label="Moins de 300 demandeurs en 2016")]
h += [Line2D([], [], color=WHITE, lw=2, label="Ligne ouverte entre 2015 et 2025"), Line2D([], [], color=WHITE, lw=1.6, ls=(0, (4, 2)), label="Communes du Tram T4")]
lg = fig.legend(handles=h, loc="upper left", bbox_to_anchor=(0.73, 0.655), frameon=False, fontsize=10, labelspacing=.7)
for t in lg.get_texts(): t.set_color(WHITE)
ptitle(fig, 0.415, "À retenir")
ptext(fig, 0.39, "Autour du Tram T4, l'emploi salarié a progressé\nplus vite que dans le reste de la région\n(+9,6 pts), mais les demandeurs d'emploi aussi.\nLes emplois créés vont-ils aux habitants ?\nLa ligne seule ne suffit pas : formation et\nrecrutement local comptent autant.", 10)
ptitle(fig, 0.215, "Précaution")
ptext(fig, 0.19, "2015 : rupture de série. 2025 : inscriptions\nautomatiques (loi pour le plein emploi).\nOn compare les moyennes du 4e trimestre\n2016 et 2024.", 9, MUTE)
footer(fig, "Sources : DARES / France Travail, « Inscrits à France Travail – données communales » (catégories A, B, C, données brutes arrondies au multiple de 5, moyennes du 4e trimestre 2016 et 2024), data.dares.travail-emploi.gouv.fr ; "
            "Île-de-France Mobilités, tracés du réseau ferré et emplacement des gares. Les agrégats régionaux sont des sommes de valeurs communales arrondies. Paris regroupe ses 20 arrondissements. Emploi salarié privé : Urssaf, effectifs par commune.")
fig.savefig(PNG, dpi=300, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok", round(idf, 1), round(t4, 1), round(rest, 1))
