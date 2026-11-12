"""Print counterpart of NetworkMap.tsx, using its generated data snapshot.

The snapshot is authoritative for clipped/simplified geometry, annotations and
region-wide totals (15 lines, 125 station records and 118 km). T14 is existing
infrastructure; TER is excluded from openings; M11 extension sections lack dates and are excluded from the map and total.
No npm process or JavaScript dependency is needed to render this plate.

Regenerate the snapshot after changing source data:
    production/.venv/bin/python production/scripts/export-network.py
Render a review copy without replacing the published pitch files:
    production/.venv/bin/python production/scripts/01_transport_extensions.py \
        --output-dir /tmp/transport-review
Use --network-data to review an exporter snapshot generated in /tmp.
"""

import argparse
import json
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patheffects as pe
from matplotlib.collections import LineCollection, PatchCollection
from matplotlib.lines import Line2D
from matplotlib.patches import PathPatch, Rectangle
from matplotlib.path import Path as PlotPath

from export_paths import export_paths

NIGHT = "#F6F4EF"
SURFACE = "#FFFEFA"
MAP_GROUND = "#F1EFEA"
INK = "#0E1B2C"
TEXT = "#344052"
MUTED = "#526071"
RULE = "#D4D9DF"
OLD = "#8B929B"
DEPARTMENT = "#D9739F"
SYMBOLS = ("o", "s", "D")
DASHES = ("solid", (0, (3, 1)), (0, (1, 1)))
SNAPSHOT = Path(__file__).resolve().parents[1] / "web/public/data/rail-network.json"


def load_network(path=SNAPSHOT):
    """Read the same exported dataset used by the web map, without recomputing it."""
    with Path(path).open(encoding="utf-8") as source:
        return json.load(source)


def map_path(svg):
    """Read the exporter's M/L/Z paths and undo the SVG downward y axis."""
    tokens = iter(svg.split())
    vertices, codes = [], []
    start = None
    for command in tokens:
        if command in ("M", "L"):
            point = (float(next(tokens)), -float(next(tokens)))
            if command == "M":
                start = point
            vertices.append(point)
            codes.append(PlotPath.MOVETO if command == "M" else PlotPath.LINETO)
        elif command == "Z" and start is not None:
            vertices.append(start)
            codes.append(PlotPath.CLOSEPOLY)
        else:
            raise ValueError(f"Unsupported network path command: {command}")
    return PlotPath(vertices, codes)


def polygons(ax, shapes, color, edge, width, zorder):
    patches = [PathPatch(map_path(shape["path"])) for shape in shapes]
    ax.add_collection(PatchCollection(patches, facecolor=color, edgecolor=edge,
                                      linewidth=width, zorder=zorder))


def lines(ax, shapes, color, width, zorder, linestyle="solid"):
    paths = [map_path(shape["path"]).vertices for shape in shapes]
    ax.add_collection(LineCollection(paths, colors=color, linewidths=width,
                                     linestyles=linestyle, zorder=zorder))


def map_labels(ax, points, color, boxed=False):
    labels = []
    for point in points:
        label = ax.text(point["x"], -point["y"], point["name"], ha="center", va="bottom",
                        fontsize=8, color=color, weight="bold" if boxed else "normal",
                        zorder=20 if boxed else 18, clip_on=True,
                        bbox=dict(boxstyle="square,pad=.18", fc=SURFACE, ec="none") if boxed else None)
        if not boxed:
            label.set_path_effects([pe.withStroke(linewidth=2, foreground=MAP_GROUND)])
        labels.append(label)
    return labels


def hide_overlapping_labels(fig, ax, labels):
    """Approximate Highmaps' non-overlapping labels; keep exported positions fixed."""
    fig.canvas.draw()
    renderer = fig.canvas.get_renderer()
    occupied = []
    area = ax.get_window_extent(renderer)
    for label in labels:
        bounds = label.get_window_extent(renderer).expanded(1.04, 1.12)
        inside = area.contains(bounds.x0, bounds.y0) and area.contains(bounds.x1, bounds.y1)
        if not inside or any(bounds.overlaps(other) for other in occupied):
            label.set_visible(False)
        else:
            occupied.append(bounds)


def figure_text(fig, x, y, text, size=10, color=TEXT, weight="normal", **kwargs):
    return fig.text(x, y, text, fontsize=size, color=color, weight=weight,
                    va="top", linespacing=1.4, **kwargs)


def create_figure(data):
    """Build the desktop web composition without interactive controls."""
    plt.rcParams.update({"font.family": "sans-serif",
                         "font.sans-serif": ["Arial", "Liberation Sans", "DejaVu Sans"],
                         "pdf.fonttype": 42})
    fig = plt.figure(figsize=(18, 11.5), facecolor=NIGHT)
    figure_text(fig, .035, .955, "Dix ans d’extension du réseau ferré", 26, INK, "bold",
                fontfamily=["Arial Narrow", "Arial", "DejaVu Sans"])
    figure_text(fig, .965, .943, "2015 — 2025", 11, MUTED, ha="right")

    # Keep the full web map canvas, including any aspect-ratio letterboxing.
    map_rect = (.035, .295, .665, .585)
    fig.add_artist(Rectangle(map_rect[:2], map_rect[2], map_rect[3],
                             transform=fig.transFigure, fc=MAP_GROUND, ec=RULE, lw=.5, zorder=-1))
    ax = fig.add_axes(map_rect, facecolor=MAP_GROUND)
    ax.set_axis_off()
    x0, x1, svg_y0, svg_y1 = data["bounds"]
    ax.set_xlim(x0, x1)
    ax.set_ylim(-svg_y1, -svg_y0)
    ax.set_aspect("equal", adjustable="box")
    polygons(ax, data["communes"], "#E3E4DF", "#FFFFFF", .26, 0)
    polygons(ax, data["paris"], "#D4D9D4", "#FFFFFF", .26, 1)
    lines(ax, data["departments"], DEPARTMENT, .6, 2)
    lines(ax, data["existing"], OLD, .75, 3)
    for index, period in enumerate(data["periods"]):
        lines(ax, period["tracks"], "#FFFFFF", 3.75, 4 + index * 2)
        lines(ax, period["tracks"], period["color"], 1.95, 5 + index * 2, DASHES[index])
    for index, period in enumerate(data["periods"]):
        ax.scatter([point["x"] for point in period["stations"]],
                   [-point["y"] for point in period["stations"]],
                   marker=SYMBOLS[index], s=18, facecolors="#FFFFFF",
                   edgecolors=period["color"], linewidths=1.05, zorder=12)
    polygons(ax, [{"path": "M 69.5 -57.2 L 69.9 -55.4 L 71.7 -55 L 69.9 -54.6 L 69.5 -52.8 L 69.1 -54.6 L 67.3 -55 L 69.1 -55.4 Z"}], INK, INK, 0, 25)
    lines(ax, [{"path": "M 2.5 -2.2 L 5 -2.2"}], INK, 3, 25)
    lines(ax, [{"path": "M 5 -2.2 L 7.5 -2.2"}], "#6B7280", 3, 25)
    map_labels(ax, [{"name": "N", "x": 69.5, "y": -58},
                    {"name": "0", "x": 2.5, "y": -3},
                    {"name": "2,5", "x": 5, "y": -3},
                    {"name": "5 km", "x": 7.5, "y": -3}], INK)
    labels = map_labels(ax, data["labels"], INK, boxed=True)
    labels += map_labels(ax, data["termini"], TEXT)
    labels += map_labels(ax, data["departmentLabels"], MUTED)

    # White statistics panel with vertical rows, as in the desktop web version.
    fig.add_artist(Rectangle((.725, .49), .24, .39, transform=fig.transFigure,
                             fc="#FFFFFF", ec="#738578", lw=.5, zorder=-1))
    figure_text(fig, .743, .855, "Le réseau de 2015 à 2025", 15, INK, "bold",
                fontfamily=["Arial Narrow", "Arial", "DejaVu Sans"])
    summary = data["summary"]
    for y, value, caption in [(.802, str(summary["lines"]), "lignes créées\nou prolongées"),
                               (.721, str(summary["stations"]), "gares\nouvertes"),
                               (.640, f'{summary["kilometres"]} km', "de voies\nnouvelles")]:
        figure_text(fig, .743, y, value, 29, INK, "bold",
                    fontfamily=["Arial Narrow", "Arial", "DejaVu Sans"])
        figure_text(fig, .852, y - .004, caption, 10)
    fig.add_artist(Line2D([.743, .947], [.574, .574], transform=fig.transFigure, color=RULE, lw=.5))
    figure_text(fig, .743, .557, "La plupart des nouvelles lignes desservent\nla petite couronne, où se concentrent\nles emplois.", 10)

    # The legend belongs below the map, not inside the figures panel.
    figure_text(fig, .035, .272, "Ouvertures par période", 10, INK, "bold")
    y = .244
    for index, period in enumerate(data["periods"]):
        fig.add_artist(Line2D([.044], [y - .005], marker=SYMBOLS[index], markersize=6,
                              markerfacecolor=SURFACE, markeredgecolor=period["color"],
                              markeredgewidth=1.3, linestyle="", transform=fig.transFigure))
        figure_text(fig, .057, y, period["name"], 9.5, INK, "bold")
        openings = ", ".join(f'{opening["line"]} ({opening["year"]})' for opening in period["openings"])
        wrapped = textwrap.wrap(openings, 70)
        figure_text(fig, .057, y - .019, "\n".join(wrapped), 9, MUTED)
        y -= .035 + .017 * len(wrapped)
    figure_text(fig, .465, .272, "Lecture", 10, INK, "bold")
    for y, color, text in [(.238, OLD, "Réseau existant avant 2015"),
                             (.157, DEPARTMENT, "Limite départementale")]:
        fig.add_artist(Line2D([.466, .482], [y - .006, y - .006], color=color, lw=1,
                              transform=fig.transFigure))
        figure_text(fig, .490, y, text, 9)
    fig.add_artist(Line2D([.474], [.196], marker="o", markersize=5, markerfacecolor="#FFFFFF",
                          markeredgecolor=INK, linestyle="", transform=fig.transFigure))
    figure_text(fig, .490, .205, "Gare ouverte : forme et couleur\nselon la période", 9)

    fig.add_artist(Line2D([.035, .965], [.084, .084], color=RULE, lw=.5, transform=fig.transFigure))
    figure_text(fig, .035, .074, "Sources et notes", 9, INK, "bold")
    figure_text(fig, .035, .053, "Île-de-France Mobilités. Tracés du réseau ferré et gares par ligne,\nconsultés le 08/11/2026. IGN / INSEE. Limites administratives.", 8, MUTED)
    figure_text(fig, .495, .074, "Les tronçons du prolongement du métro 11 sont présents dans la source, mais non datés :\nils sont exclus de cette carte et du total ; ses gares de 2024 figurent sur la carte.\nLe T14, renommé en 2025, reprend une ligne ancienne et figure dans le réseau existant.", 8, MUTED)
    hide_overlapping_labels(fig, ax, labels)
    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--network-data", type=Path, default=SNAPSHOT)
    parser.add_argument("--output-dir", type=Path, help="Review directory instead of pitch/")
    args = parser.parse_args()
    data = load_network(args.network_data)
    fig = create_figure(data)
    if args.output_dir:
        args.output_dir.mkdir(parents=True, exist_ok=True)
        PNG = args.output_dir / "01_reseau_transport_extens.png"
        PDF = args.output_dir / "01_reseau_transport_extens.pdf"
    else:
        PNG, PDF = export_paths("01_reseau_transport_extens")
    fig.savefig(PNG, dpi=300, facecolor=NIGHT)
    fig.savefig(PDF, facecolor=NIGHT)
    print(f"{PNG}\n{PDF}")
