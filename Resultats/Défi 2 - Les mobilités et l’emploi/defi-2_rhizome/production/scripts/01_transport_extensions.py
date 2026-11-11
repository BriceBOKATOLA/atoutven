from export_paths import export_paths

PNG, PDF = export_paths("01_reseau_transport_extens")

from map_theme import *
from itertools import combinations
from adjustText import adjust_text
from matplotlib.lines import Line2D

com, dep, riv, fer, gar = load()
old = fer[fer.an < 2015]
new = fer[(fer.an >= 2015) & (fer.an <= 2025) & (~fer.res_com.str.contains("TER"))].copy()
ng = gar[(gar.an >= 2015) & (gar.an <= 2025)].copy()
new["lg"] = new.res_com.map(short); ng["lg"] = ng.res_com.map(short)
COL = {}
for _, r in new.iterrows(): COL.setdefault(r.lg, "#" + (r.colourweb_hexa or "888888"))
COL.setdefault("M11", "#704B1C")
ouv = sorted(set(zip(new.lg, new.an.astype(int))) | set(zip(ng.lg, ng.an.astype(int))), key=lambda t: (t[1], t[0]))
km = new.length.sum() / 1000

X0, X1, Y0, Y1 = 619000, 692000, 6825000, 6885000
fig, ax = plate("01", "Dix ans d'extension du réseau ferré",
                "Entre 2015 et 2025, 16 lignes de métro, de tram, de RER et de câble ont été créées ou prolongées, surtout en petite couronne. Couleur = période d'ouverture.")
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1); ax.set_aspect("equal", adjustable="datalim")
basemap(ax, com, dep)
old.plot(ax=ax, color=OLDNET, linewidth=.9, zorder=3)
for an, g in new.groupby("an"): cased(ax, g, pcol(an), 2.4, 5)
ng.plot(ax=ax, color="#FFFFFF", edgecolor=[pcol(a) for a in ng.an], markersize=16, linewidth=1.2, zorder=9)
ax.set_xlim(X0, X1); ax.set_ylim(Y0, Y1)

texts, xs, ys = [], [], []
for l, a in ouv:
    g = new[(new.lg == l) & (new.an == a)]; s = ng[(ng.lg == l) & (ng.an == a)]
    geo = g.cx[X0:X1, Y0:Y1] if len(g) else s.cx[X0:X1, Y0:Y1]
    if not len(geo): continue
    u = geo.unary_union; pt = u.interpolate(.5, normalized=True) if u.geom_type == "LineString" else u.centroid
    t = yl(ax, pt.x + 1200, pt.y + 900, f"{l} | {a}" + ("*" if l == "M11" else ""))
    texts.append(t); xs.append(pt.x); ys.append(pt.y)
for l, a in ouv:
    pts = list(ng[(ng.lg == l) & (ng.an == a)].itertuples())
    if not pts: continue
    pair = max(combinations(pts, 2), key=lambda p: p[0].geometry.distance(p[1].geometry)) if len(pts) > 1 else pts
    for p in pair:
        x, y = p.geometry.x, p.geometry.y
        if X0 + 1500 < x < X1 - 1500 and Y0 + 1500 < y < Y1 - 1500:
            t = ax.text(x + 500, y - 300, p.nom_gares, fontsize=6.6, color="#374151", zorder=18)
            t.set_path_effects([pe.withStroke(linewidth=2.6, foreground=NIGHT)]); texts.append(t); xs.append(x); ys.append(y)
texts.append(dep_names(ax, dep, X0, X1, Y0, Y1))
adjust_text(texts, x=xs, y=ys, ax=ax, expand=(1.15, 1.35), max_move=(25, 25), force_points=(0.4, 0.6), arrowprops=dict(arrowstyle="-", color=MUTE, lw=.5))
compass(ax, X1 - 3500, Y1 - 5000); scalebar(ax, X0 + 2500, Y0 + 2200)

panel_title(fig, 0.83, "Le réseau de 2015 à 2025")
big(fig, 0.737, 0.775, "16", "lignes créées\nou prolongées"); big(fig, 0.81, 0.775, "125", "gares\nouvertes"); big(fig, 0.885, 0.775, f"{km:.0f} km", "de voies\nnouvelles")
ptitle(fig, 0.665, "Ouvertures par période")
by = {}
for l, an in ouv: by.setdefault(pcol(an), []).append(f"{l} ({an})")
yy = 0.635
for p0, p1, c, lab in PERIODS:
    fig.add_artist(Line2D([0.737, 0.757], [yy - 0.011, yy - 0.011], color=c, lw=5, transform=fig.transFigure, solid_capstyle="butt"))
    fig.text(0.763, yy, lab, fontsize=12, color=c, fontfamily=COND, fontweight="bold", va="top")
    fig.text(0.763, yy - 0.026, "\n".join(textwrap.wrap(", ".join(by[c]), 44)), fontsize=9.3, color="#374151", va="top", linespacing=1.4)
    yy -= 0.026 + 0.021 * len(textwrap.wrap(", ".join(by[c]), 44)) + 0.03
ptitle(fig, 0.325, "Lecture")
items = [(Line2D([], [], color=OLDNET, lw=2), "Réseau existant avant 2015"),
         (Line2D([], [], marker="o", ls="", mfc="#FFFFFF", mec="#0E1B2C", mew=1.2, ms=6), "Gare ouverte (contour = période)"),
         (Line2D([], [], color="#D9739F", lw=1), "Limite départementale")]
ptext(fig, 0.165, "La plupart des nouvelles lignes desservent\nla petite couronne, là où se concentrent\nles emplois (voir planche 02).", 10, "#4B5563")
lg = fig.legend([i[0] for i in items], [i[1] for i in items], loc="upper left", bbox_to_anchor=(0.73, 0.31), frameon=False, fontsize=10, labelspacing=.8)
for t in lg.get_texts(): t.set_color(WHITE)
footer(fig, "Sources : Île-de-France Mobilités — tracés du réseau ferré et emplacement des gares (dates de mise en service), consultés le 08/11/2026 ; IGN / INSEE — limites administratives. "
            "* Métro 11 : le prolongement de 2024 n'a pas de tracé dans le jeu IDFM, seules ses gares figurent. Tram T14 : ligne Esbly – Crécy-la-Chapelle (Seine-et-Marne). Noms de gares : terminus de chaque nouvelle section.")
fig.savefig(PNG, dpi=200, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok")
