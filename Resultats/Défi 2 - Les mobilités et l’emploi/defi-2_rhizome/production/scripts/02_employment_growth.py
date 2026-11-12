from export_paths import export_paths

PNG, PDF = export_paths("02_emploi_progress")

from map_theme import *
from map_utils import CLEAN
from adjustText import adjust_text
from matplotlib.lines import Line2D
GAIN, LOSS = "#E69F00", "#0072B2"

com, dep, riv, fer, gar = load()
new = fer[(fer.an >= 2015) & (fer.an <= 2025) & (~fer.res_com.str.contains("TER"))].copy(); new["lg"] = new.res_com.map(short)
old = fer[fer.an < 2015]
COL = {}
for _, r in new.iterrows(): COL.setdefault(r.lg, "#" + (r.colourweb_hexa or "888888"))
grp = json.loads((CLEAN / "groupes_lignes.json").read_text(encoding="utf-8")); served = {c for v in grp.values() for c in v["codes"]}

X0, X1, Y0, Y1 = 619000, 692000, 6825000, 6885000
fig, ax = plate("02", "Où l'emploi a progressé depuis 2015",
                "L'Île-de-France a gagné 651 000 emplois salariés privés en dix ans. Hors Paris, les gains se concentrent à l'ouest, au nord et autour de Roissy.")
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect("equal", adjustable="datalim")
basemap(ax, com, dep)
com[com.code.isin(served)].plot(ax=ax, color="#D8D3C9", edgecolor=COMM_EDGE, linewidth=.3, zorder=0.6)
old.plot(ax=ax, color=OLDNET, linewidth=.8, zorder=3)
cased(ax, new, "#374151", 1.3, 4)

c = com.copy(); c["pt"] = c.geometry.representative_point()
c = c[(c.evol_abs.abs() >= 300) & (c.code != "75056")].sort_values("evol_abs", key=abs, ascending=False)
K = .045
for _, r in c.iterrows():
    col = GAIN if r.evol_abs > 0 else LOSS; s = abs(r.evol_abs) * K
    if r.evol_abs > 0: ax.scatter(r.pt.x, r.pt.y, s=s, color=col, alpha=.5, edgecolor="#A86F00", linewidth=.7, zorder=7)
    else: ax.scatter(r.pt.x, r.pt.y, s=s, facecolor="none", edgecolor=col, linewidth=1.3, zorder=7)
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)

lab = pd.concat([c[c.evol_abs > 0].head(10), c[c.evol_abs < 0].head(3)])
texts = []
for _, r in lab.iterrows():
    if X0 < r.pt.x < X1 and Y0 < r.pt.y < Y1:
        texts.append(yl(ax, r.pt.x, r.pt.y, f"{r.nom} | {fr(r.evol_abs, 0)}", 9.5, YEL if r.evol_abs > 0 else LOSS, ha="center"))
p = com[com.code == "75056"].iloc[0]
pt = ax.text(653000, 6860500, f"PARIS | {fr(p.evol_abs, 0)}\n(non dessiné)", fontsize=9, color=WHITE, ha="center", fontfamily=COND, fontweight="bold", zorder=19, linespacing=1.2)
pt.set_path_effects([pe.withStroke(linewidth=3, foreground=NIGHT)]); texts.append(pt)
adjust_text(texts, ax=ax, expand=(1.15, 1.35), max_move=(30, 30), arrowprops=dict(arrowstyle="-", color=MUTE, lw=.5))
compass(ax, X1 - 3500, Y1 - 5000); scalebar(ax, X0 + 2500, Y0 + 2200)

panel_title(fig, 0.83, "Emploi salarié privé, 2015-2025")
big(fig, 0.737, 0.775, "+651 000", "emplois en Île-de-France"); big(fig, 0.885, 0.775, "+14 %", "en dix ans")
ptitle(fig, 0.665, "Gain ou perte par commune")
lax = fig.add_axes([0.735, 0.47, 0.225, 0.17]); lax.set_axis_off(); lax.set_xlim(0, 10); lax.set_ylim(0, 10); lax.set_facecolor(PANEL)
for v, x in [(30000, 2.0), (10000, 5.4), (3000, 8.0)]:
    lax.scatter(x, 4.6, s=v * K, color=GAIN, alpha=.5, edgecolor="#A86F00", linewidth=.7)
    lax.text(x, .2, fr(v, 0, sign=False), color=WHITE, fontsize=9, ha="center")
lax.scatter(.7, 9.4, s=900 * K, color=GAIN, alpha=.5, edgecolor="#A86F00"); lax.text(1.3, 9.4, "Gain d'emplois", color=WHITE, fontsize=9.5, va="center")
lax.scatter(5.6, 9.4, s=900 * K, facecolor="none", edgecolor=LOSS, linewidth=1.1); lax.text(6.2, 9.4, "Perte d'emplois", color=WHITE, fontsize=9.5, va="center")
ptext(fig, 0.455, "Surface du cercle proportionnelle au nombre\nd'emplois gagnés ou perdus (communes avec\nau moins 300 emplois de variation).", 9.5, "#4B5563")
ptitle(fig, 0.36, "Lecture")
items = [(Line2D([], [], color="#374151", lw=2), "Ligne ouverte entre 2015 et 2025"),
         (Line2D([], [], color=OLDNET, lw=2), "Réseau existant avant 2015"),
         (Line2D([], [], marker="s", ls="", mfc="#D8D3C9", mec=COMM_EDGE, ms=11), "Commune ayant reçu une gare 2015-2025")]
lg = fig.legend([i[0] for i in items], [i[1] for i in items], loc="upper left", bbox_to_anchor=(0.73, 0.345), frameon=False, fontsize=10, labelspacing=.8)
for t in lg.get_texts(): t.set_color(WHITE)
ptitle(fig, 0.215, "À retenir")
ptext(fig, 0.19, "Certains grands pôles ont reçu une ligne récente\n(Métro 14 à Saint-Ouen, RER E à Nanterre),\nd'autres non (Issy, Neuilly, Levallois) :\nla desserte n'explique pas tout.", 10)
footer(fig, "Sources : Urssaf — effectifs salariés du secteur privé par commune au 31/12/2015 et au 31/12/2025 (open.urssaf.fr) ; Île-de-France Mobilités — tracés du réseau ferré. "
            "Champ : emploi salarié privé, hors fonction publique ; l'intérim est compté au lieu de l'agence. Paris est compté comme une seule commune ; son gain n'est pas dessiné pour garder la lisibilité.")
fig.savefig(PNG, dpi=300, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok")
