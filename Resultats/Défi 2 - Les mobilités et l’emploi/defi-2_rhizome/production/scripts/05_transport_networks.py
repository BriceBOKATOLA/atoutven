from export_paths import export_paths

PNG, PDF = export_paths("05_tous_reseaux_2015_2025")

from map_theme import *
from matplotlib.lines import Line2D

com, dep, riv, fer, gar = load()
f = fer[fer["mode"] != "TER"].copy(); f["L"] = f.length / 1000
g = gar[gar["mode"] != "TER"].copy()
# 5 familles, 5 couleurs franches (Okabe-Ito / Tol) : on ne joue pas sur des nuances d'une même couleur
MODES = [("TRAIN", "Train Transilien", "#6F6F6F", 1.2), ("RER", "RER", "#CC3311", 1.9), ("METRO", "Métro", "#0072B2", 1.5),
         ("TRAMWAY", "Tramway", "#009E73", 1.7), ("CABLE", "Câble et VAL", "#AA4499", 1.8)]
fam = lambda m: "CABLE" if m in ("CABLE", "NAVETTE", "VAL") else m
f["fam"] = f["mode"].map(fam); g["fam"] = g["mode"].map(fam)

fig = plt.figure(figsize=(18, 11.5), facecolor=NIGHT)
fig.text(0.03, 0.955, "05", fontsize=12, color=YEL, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.958, "Le réseau francilien en 2015 et en 2025", fontsize=30, color=WHITE, fontfamily=COND, fontweight="bold", va="top")
fig.text(0.055, 0.905, "Tous les réseaux ferrés de transport en commun : train, RER, métro, tramway, câble et VAL. En dix ans, le tramway a presque doublé.", fontsize=13.5, color="#4B5563", va="top")
from matplotlib.patches import FancyBboxPatch
fig.patches.append(FancyBboxPatch((0.72, 0.075), 0.255, 0.77, boxstyle="square,pad=0", transform=fig.transFigure, fc=PANEL, ec=FRAME, lw=1.2, zorder=-5))

X0, X1, YC = 619000, 686000, 6857000
for i, year in enumerate((2015, 2025)):
    ax = fig.add_axes([0.015 + i * 0.352, 0.075, 0.345, 0.77]); ax.set_facecolor(NIGHT); ax.set_axis_off()
    basemap(ax, com, dep)
    s = f[f.an <= year]; st = g[g.an <= year]
    for k, (m, lab, c, w) in enumerate(MODES):
        part = s[s.fam == m]
        if len(part):
            part.plot(ax=ax, color="#FFFFFF", linewidth=w + 1.4, zorder=3 + k * .1)
            part.plot(ax=ax, color=c, linewidth=w, zorder=3.05 + k * .1)
    if year == 2025:  # tronçons nouveaux : liseré noir fin pour les repérer
        nw = s[s.an > 2015]
        nw.plot(ax=ax, color=WHITE, linewidth=4.6, zorder=2.9)
    st.plot(ax=ax, color="#FFFFFF", edgecolor="#4B5563", markersize=1.6, linewidth=.3, zorder=4)
    ax.set_xlim(X0, X1); h = (X1 - X0) * (0.77 * 11.5) / (0.345 * 18); ax.set_ylim(YC - h / 2, YC + h / 2)
    ax.text(X0 + 2500, YC + h / 2 - 4500, str(year), fontsize=34, color=WHITE, fontfamily=COND, fontweight="bold", zorder=30, bbox=dict(fc=NIGHT, ec="none", pad=1, alpha=.9))
    km = s.groupby("fam").L.sum()
    ax.text(X0 + 2500, YC + h / 2 - 8200, f"{s.res_com.nunique()} lignes · {st.id_ref_zdc.nunique()} gares et stations", fontsize=10.5, color="#374151", zorder=30, bbox=dict(fc=NIGHT, ec="none", pad=1.5, alpha=.9))
    t = ax.text(651800, 6862200, "PARIS", fontsize=10, color=WHITE, ha="center", fontfamily=COND, fontweight="bold", zorder=19)
    t.set_path_effects([pe.withStroke(linewidth=3, foreground=NIGHT)])
    if i == 1: compass(ax, X1 - 3500, YC + h / 2 - 5000); scalebar(ax, X0 + 2500, YC - h / 2 + 2200)

panel_title(fig, 0.83, "Ce qui a changé en dix ans")
ptitle(fig, 0.78, "Longueur des lignes (km), 2015 et 2025")
k15 = f[f.an <= 2015].groupby("fam").L.sum(); k25 = f[f.an <= 2025].groupby("fam").L.sum()
n15 = f[f.an <= 2015].groupby("fam").res_com.nunique(); n25 = f[f.an <= 2025].groupby("fam").res_com.nunique()
yy = 0.745
for m, lab, c, w in MODES:
    a, b = k15.get(m, 0), k25.get(m, 0)
    fig.add_artist(Line2D([0.737, 0.757], [yy - 0.009, yy - 0.009], color=c, lw=5, transform=fig.transFigure, solid_capstyle="butt"))
    fig.text(0.763, yy, lab, fontsize=11, color=WHITE, va="top")
    fig.text(0.868, yy, f"{a:.0f}".replace(",", " "), fontsize=11, color=MUTE, va="top", ha="right")
    fig.text(0.882, yy, "à", fontsize=10, color=MUTE, va="top", ha="center")
    fig.text(0.918, yy, f"{b:.0f}", fontsize=11, color=WHITE, va="top", ha="right", fontweight="bold")
    d = (b / a - 1) * 100 if a else None
    fig.text(0.958, yy, "nouveau" if a == 0 else (f"{fr(d, 0)} %" if abs(d) >= .5 else "="), fontsize=11, color=c if (a == 0 or d >= .5) else MUTE,
             va="top", ha="right", fontfamily=COND, fontweight="bold")
    yy -= 0.034
ptitle(fig, 0.56, "Nombre de lignes de tramway")
big(fig, 0.737, 0.535, f"{n15.get('TRAMWAY', 0)} à {n25.get('TRAMWAY', 0)}", "lignes de tramway\nentre 2015 et 2025", color="#009E73")
big(fig, 0.885, 0.535, f"+{g[(g.an > 2015) & (g.an <= 2025)].id_ref_zdc.nunique()}", "gares et stations\nnouvelles", color=WHITE)
ptitle(fig, 0.385, "Lecture")
items = [(Line2D([], [], color=WHITE, lw=4.5), "Tronçon ouvert entre 2016 et 2025 (carte 2025)"),
         (Line2D([], [], marker="o", ls="", mfc="#FFFFFF", mec="#4B5563", ms=4), "Gare ou station"),
         (Line2D([], [], color="#D9739F", lw=1), "Limite départementale")]
lg = fig.legend([i[0] for i in items], [i[1] for i in items], loc="upper left", bbox_to_anchor=(0.73, 0.375), frameon=False, fontsize=10, labelspacing=.8)
for t in lg.get_texts(): t.set_color(WHITE)
ptitle(fig, 0.25, "À retenir")
ptext(fig, 0.225, "Le train et le RER, déjà très étendus, bougent peu.\nLa croissance vient du tramway et du métro,\nen petite couronne : de rocade en rocade,\nle réseau se densifie autour de Paris.", 10)
footer(fig, "Sources : Île-de-France Mobilités — tracés du réseau ferré et emplacement des gares, avec leurs dates de mise en service (jeux « traces-du-reseau-ferre-idf » et « emplacement-des-gares-idf »). "
            "Hors TER et hors bus (les lignes de bus n'ont pas de date de mise en service dans les données ouvertes). Longueurs : somme des tracés par mode ; un tronçon partagé par deux lignes compte deux fois.")
fig.savefig(PNG, dpi=300, facecolor=NIGHT); fig.savefig(PDF, facecolor=NIGHT)
print("ok")
