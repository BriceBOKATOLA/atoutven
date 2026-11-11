import os
from pathlib import Path
os.environ["QT_QPA_PLATFORM"] = "offscreen"
from qgis.core import *
from qgis.PyQt.QtGui import QColor, QFont
from qgis.PyQt.QtCore import Qt, QSize, QSizeF

app = QgsApplication([], False); app.initQgis()
O = Path(__file__).resolve().parent.parent / "datasets" / "clean"
BG, COMM, EDGE, PINK, INK, OLD, YEL, GOLD, LOSS = "#F6F4EF", "#E9E6DF", "#FBFAF7", "#FF2E88", "#0E1B2C", "#B5B0A5", "#FFD400", "#F2B800", "#FF2E88"
CRS = QgsCoordinateReferenceSystem("EPSG:2154")
EXT = QgsRectangle(619000, 6825000, 692000, 6885000)

def fill(color, edge=EDGE, w=0.15, style="solid"):
    return QgsFillSymbol.createSimple({"color": color, "outline_color": edge, "outline_width": str(w), "outline_style": style})
def outline(color, w, style="solid"):
    return QgsFillSymbol.createSimple({"color": "0,0,0,0", "outline_color": color, "outline_width": str(w), "outline_style": style})
def line(color, w):
    return QgsLineSymbol.createSimple({"line_color": color, "line_width": str(w), "capstyle": "round", "joinstyle": "round"})

def lay(proj, gpkg, name, title):
    l = QgsVectorLayer(f"{gpkg}|layername={name}", title, "ogr")
    assert l.isValid(), (gpkg, name)
    proj.addMapLayer(l, False); return l

def labels(l, expr, size=7, bg=YEL, txt=INK, filt=None, bold=True):
    s = QgsPalLayerSettings(); s.fieldName = expr; s.isExpression = True
    f = QgsTextFormat(); fo = QFont("Barlow Condensed"); fo.setBold(bold); f.setFont(fo); f.setSize(min(size, 7.5)); f.setColor(QColor(txt))
    if bg:
        b = QgsTextBackgroundSettings(); b.setEnabled(True); b.setFillColor(QColor(bg)); b.setStrokeWidth(0)
        b.setSizeType(QgsTextBackgroundSettings.SizeBuffer); b.setSize(QSizeF(0.4, 0.2)); f.setBackground(b)
    else:
        bu = QgsTextBufferSettings(); bu.setEnabled(True); bu.setColor(QColor(BG)); bu.setSize(0.8); f.setBuffer(bu)
    s.setFormat(f)
    if filt:
        s.dataDefinedProperties().setProperty(QgsPalLayerSettings.Show, QgsProperty.fromExpression(filt))
    l.setLabeling(QgsVectorLayerSimpleLabeling(s)); l.setLabelsEnabled(True)

from qgis.PyQt.QtCore import QSizeF

def base_fond(l, paris=True):
    r = QgsRuleBasedRenderer(fill(COMM)); root = r.rootRule(); root.removeChildAt(0)
    if paris: root.appendChild(QgsRuleBasedRenderer.Rule(fill("#DCD8CF"), filterExp="\"code\" = '75056'", label="Paris"))
    root.appendChild(QgsRuleBasedRenderer.Rule(fill(COMM), filterExp="ELSE", label="Commune"))
    l.setRenderer(r)

def deps(l):
    l.setRenderer(QgsSingleSymbolRenderer(outline("#D9739F", 0.3)))
    labels(l, "upper(\"nom_dep\")" if "nom_dep" in l.fields().names() else "upper(\"nom\")", 8, None, "#6B7280", "\"code" + ("_dep" if "code_dep" in l.fields().names() else "") + "\" <> '75'", False)

def lignes_couleur(l, w=1.1):
    s = line(INK, w); s.symbolLayer(0).setDataDefinedProperty(QgsSymbolLayer.PropertyStrokeColor, QgsProperty.fromField("couleur"))
    l.setRenderer(QgsSingleSymbolRenderer(s))

def gares(l, label=False):
    s = QgsMarkerSymbol.createSimple({"name": "circle", "color": "white", "outline_color": INK, "outline_width": "0.35", "size": "1.8"})
    l.setRenderer(QgsSingleSymbolRenderer(s))
    if label: labels(l, "\"nom_gares\"", 7, None, INK, None, False)

def finish(proj, layers, path, title):
    proj.setCrs(CRS); proj.setTitle(title)
    proj.setBackgroundColor(QColor(BG))
    root = proj.layerTreeRoot()
    for l in layers: root.addLayer(l)
    v = proj.viewSettings(); v.setDefaultViewExtent(QgsReferencedRectangle(EXT, CRS))
    proj.writeEntry("Paths", "/Absolute", False)
    assert proj.write(path), path
    print("ok", path)

# ---------- 01 réseau
p = QgsProject(); g = f"{O}/01_network/01_reseau.gpkg"
dep_ = lay(p, g, "departements", "Départements"); deps(dep_)
gar = lay(p, g, "gares_2015_2025", "Gares ouvertes 2015-2025"); gares(gar, True)
lig = lay(p, g, "lignes_2015_2025", "Lignes ouvertes 2015-2025 (couleur = période)")
lig.setRenderer(QgsRuleBasedRenderer(line(INK, 1)))
_root = lig.renderer().rootRule(); _root.removeChildAt(0)
for _a, _b, _c, _l in [(2015, 2018, "#009E73", "2015 – 2018"), (2019, 2021, "#0072B2", "2019 – 2021"), (2022, 2025, "#D55E00", "2022 – 2025")]:
    _root.appendChild(QgsRuleBasedRenderer.Rule(line(_c, 1.3), filterExp=f'"an" BETWEEN {_a} AND {_b}', label=_l))
labels(lig, "\"ligne\" || ' | ' || \"an\"", 9, YEL, INK)
_s = lig.labeling().settings(); _s.lineSettings().setMergeLines(True); _s.placement = Qgis.LabelPlacement.Horizontal; _s.priority = 10
gar.labeling().settings()
lig.setLabeling(QgsVectorLayerSimpleLabeling(_s))
old = lay(p, g, "reseau_avant_2015", "Réseau avant 2015"); old.setRenderer(QgsSingleSymbolRenderer(line(OLD, 0.35)))
pts = lay(p, g, "emplois_points", "Lueur des emplois 2025")
h = QgsHeatmapRenderer(); h.setRadius(9); h.setRadiusUnit(QgsUnitTypes.RenderMillimeters); h.setWeightExpression("if(\"code\"='75056', 0, sqrt(\"emploi_2025\"))")
ramp = QgsGradientColorRamp(QColor(110, 105, 98, 0), QColor(77, 72, 66, 90)); ramp.setStops([QgsGradientStop(0.5, QColor(110, 105, 98, 25))])
h.setColorRamp(ramp); pts.setRenderer(h); pts.setOpacity(0.8)
p.layerTreeRoot()
c = lay(p, g, "communes_emploi_2025", "Communes"); base_fond(c)
finish(p, [dep_, gar, lig, old, pts, c], f"{O}/01_network/01_reseau.qgz", "01 — Dix ans d'extension du réseau ferré")

# ---------- 02 emploi
p = QgsProject(); g = f"{O}/02_employment_growth/02_emploi.gpkg"
dep_ = lay(p, g, "departements", "Départements"); deps(dep_)
cer = lay(p, g, "cercles_evolution_emploi", "Gain ou perte d'emplois 2015-2025")
gain = QgsMarkerSymbol.createSimple({"name": "circle", "color": "230,159,0,128", "outline_color": "#A86F00", "outline_width": "0.2"})
loss = QgsMarkerSymbol.createSimple({"name": "circle", "color": "0,0,0,0", "outline_color": "#0072B2", "outline_width": "0.35"})
size = QgsProperty.fromExpression("sqrt(abs(\"evol_abs\")) * 0.075")
for s in (gain, loss): s.setDataDefinedSize(size)
r = QgsRuleBasedRenderer(gain.clone()); root = r.rootRule(); root.removeChildAt(0)
root.appendChild(QgsRuleBasedRenderer.Rule(gain.clone(), filterExp="\"evol_abs\" >= 300 AND \"code\" <> '75056'", label="Gain d'emplois"))
root.appendChild(QgsRuleBasedRenderer.Rule(loss.clone(), filterExp="\"evol_abs\" <= -300", label="Perte d'emplois"))
cer.setRenderer(r)
labels(cer, "\"nom\" || ' | ' || if(\"evol_abs\">0,'+','') || format_number(\"evol_abs\",0)", 8.5, YEL, INK, "abs(\"evol_abs\") >= 8000 AND \"code\" <> '75056' AND abs(\"evol_abs\") >= 9900 OR \"evol_abs\" <= -4600")
lig = lay(p, g, "lignes_2015_2025", "Lignes ouvertes 2015-2025"); lig.setRenderer(QgsSingleSymbolRenderer(line("#374151", 0.5)))
old = lay(p, g, "reseau_avant_2015", "Réseau avant 2015"); old.setRenderer(QgsSingleSymbolRenderer(line(OLD, 0.3)))
c = lay(p, g, "communes_emploi", "Communes (desservies en bleu)")
r = QgsRuleBasedRenderer(fill(COMM)); root = r.rootRule(); root.removeChildAt(0)
root.appendChild(QgsRuleBasedRenderer.Rule(fill("#DCD8CF"), filterExp="\"code\" = '75056'", label="Paris (+244 627, non dessiné)"))
root.appendChild(QgsRuleBasedRenderer.Rule(fill("#D8D3C9"), filterExp="\"desservie_par\" IS NOT NULL", label="Commune ayant reçu une gare 2015-2025"))
root.appendChild(QgsRuleBasedRenderer.Rule(fill(COMM), filterExp="ELSE", label="Autre commune"))
c.setRenderer(r)
finish(p, [dep_, cer, lig, old, c], f"{O}/02_employment_growth/02_emploi.qgz", "02 — Où l'emploi a progressé depuis 2015")

# La planche 03 ne dispose pas de GeoPackage dans les données fournies.

# ---------- 04 demandeurs
p = QgsProject(); g = f"{O}/04_jobseekers/04_demandeurs.gpkg"
dep_ = lay(p, g, "departements", "Départements"); deps(dep_)
t4 = lay(p, g, "communes_tram_t4", "Communes du Tram T4"); t4.setRenderer(QgsSingleSymbolRenderer(outline(INK, 0.6, "dash")))
gar = lay(p, g, "gares_2015_2025", "Gares ouvertes 2015-2025"); gares(gar)
lig = lay(p, g, "lignes_2015_2025", "Lignes ouvertes 2015-2025"); lig.setRenderer(QgsSingleSymbolRenderer(line(INK, 0.6)))
d = lay(p, g, "communes_demandeurs", "Demandeurs d'emploi A, B, C — évolution 2016-2024")
cls = [(-100, -5, "#2C7FB8", "Baisse de plus de 5 %"), (-5, 0, "#A6CEE3", "Baisse de 0 à 5 %"), (0, 5, "#FBE6CC", "Hausse de 0 à 5 %"), (5, 15, "#F5AE6B", "Hausse de 5 à 15 %"), (15, 1000, "#D9531E", "Hausse de plus de 15 %")]
d.setRenderer(QgsGraduatedSymbolRenderer("defm_evol_pct", [QgsRendererRange(a, b, fill(c, "white", 0.15), l) for a, b, c, l in cls]))
labels(d, "\"nom\" || ' | ' || if(\"defm_evol_pct\">0,'+','') || format_number(\"defm_evol_pct\",0) || ' %'", 8, YEL, INK, "\"desservie_par\" IS NOT NULL AND \"defm_2016\" >= 2000")
c = lay(p, g, "communes_fond", "Communes (moins de 300 demandeurs)"); c.setRenderer(QgsSingleSymbolRenderer(fill("#F1EFEA")))
finish(p, [dep_, t4, gar, lig, d, c], f"{O}/04_jobseekers/04_demandeurs.qgz", "04 — Demandeurs d'emploi 2016-2024")

# ---------- 05 tous les réseaux 2015 / 2025
FAM = [("Train Transilien", "#6F6F6F", 0.35), ("RER", "#CC3311", 0.6), ("Métro", "#0072B2", 0.5), ("Tramway", "#009E73", 0.55), ("Câble et VAL", "#AA4499", 0.6)]
p = QgsProject(); g = f"{O}/05_all_networks_2015_2025/05_tous_reseaux.gpkg"
dep_ = lay(p, g, "departements", "Départements"); deps(dep_)
grp = []
for yr in (2025, 2015):
    gl = lay(p, g, f"gares_{yr}", f"Gares {yr}")
    gl.setRenderer(QgsSingleSymbolRenderer(QgsMarkerSymbol.createSimple({"name": "circle", "color": "white", "outline_color": "#4B5563", "outline_width": "0.15", "size": "0.8"})))
    rl = lay(p, g, f"reseau_{yr}", f"Réseau {yr}")
    rl.setRenderer(QgsCategorizedSymbolRenderer("famille", [QgsRendererCategory(n, line(c, w), n) for n, c, w in FAM]))
    grp.append((yr, gl, rl))
c = lay(p, g, "communes", "Communes"); base_fond(c)
p.setCrs(CRS); p.setTitle("05 — Le réseau francilien en 2015 et en 2025"); p.setBackgroundColor(QColor(BG))
root = p.layerTreeRoot(); root.addLayer(dep_)
for yr, gl, rl in grp:
    gr = root.addGroup(f"Réseau {yr}"); gr.addLayer(gl); gr.addLayer(rl)
    if yr == 2015: gr.setItemVisibilityChecked(False)
root.addLayer(c)
p.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(600000, 6800000, 705000, 6915000), CRS))
p.writeEntry("Paths", "/Absolute", False); assert p.write(f"{O}/05_all_networks_2015_2025/05_tous_reseaux.qgz"); print("ok 05")

# ---------- 06 pôles d'emploi 2015 / 2025
p = QgsProject(); g = f"{O}/06_employment_centers_2015_2025/06_poles_emploi.gpkg"
dep_ = lay(p, g, "departements", "Départements"); deps(dep_)
D = [(0, 100, "#F1EFEA", "Moins de 100 emplois/km²"), (100, 500, "#DCE3EC", "100 à 500"), (500, 2000, "#B3C3D9", "500 à 2 000"), (2000, 1e7, "#7F9BC2", "Plus de 2 000")]
groups = []
for yr in (2025, 2015):
    po = lay(p, g, f"poles_{yr}", f"Pôles {yr} (10 000 emplois et plus)")
    s_ = QgsMarkerSymbol.createSimple({"name": "circle", "color": "230,159,0,190", "outline_color": "#A86F00", "outline_width": "0.2"})
    s_.setDataDefinedSize(QgsProperty.fromExpression(f'if("code"=\'75056\', 0, sqrt("emploi_{yr}") * 0.035)'))
    if yr == 2025:
        r_ = QgsRuleBasedRenderer(s_.clone()); rt = r_.rootRule(); rt.removeChildAt(0)
        nw = s_.clone(); nw.symbolLayer(0).setStrokeColor(QColor("#D55E00")); nw.symbolLayer(0).setStrokeWidth(0.6)
        rt.appendChild(QgsRuleBasedRenderer.Rule(nw, filterExp='"nouveau_pole"', label="Nouveau pôle depuis 2015"))
        rt.appendChild(QgsRuleBasedRenderer.Rule(s_.clone(), filterExp="ELSE", label="Pôle"))
        po.setRenderer(r_)
        labels(po, '"nom"', 6.5, None, "#8A3B00", '"nouveau_pole"', False)
    else:
        po.setRenderer(QgsSingleSymbolRenderer(s_))
    rl = lay(p, g, f"reseau_{yr}", f"Réseau ferré {yr}"); rl.setRenderer(QgsSingleSymbolRenderer(line("#9AA0A8", 0.2)))
    cm = lay(p, g, "communes_emploi", f"Densité d'emplois {yr}")
    cm.setRenderer(QgsGraduatedSymbolRenderer(f"densite_{yr}", [QgsRendererRange(a, b, fill(c_, "white", 0.1), l) for a, b, c_, l in D]))
    groups.append((yr, [po, rl, cm]))
p.setCrs(CRS); p.setTitle("06 — Les pôles d'emploi en 2015 et en 2025"); p.setBackgroundColor(QColor(BG))
root = p.layerTreeRoot(); root.addLayer(dep_)
for yr, ls in groups:
    gr = root.addGroup(f"Emploi {yr}")
    for l_ in ls: gr.addLayer(l_)
    if yr == 2015: gr.setItemVisibilityChecked(False)
p.viewSettings().setDefaultViewExtent(QgsReferencedRectangle(QgsRectangle(600000, 6800000, 705000, 6915000), CRS))
p.writeEntry("Paths", "/Absolute", False); assert p.write(f"{O}/06_employment_centers_2015_2025/06_poles_emploi.qgz"); print("ok 06")

app.exitQgis()
