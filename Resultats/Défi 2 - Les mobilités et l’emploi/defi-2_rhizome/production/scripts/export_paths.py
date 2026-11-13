"""Chemins des fichiers produits pour une planche."""

from pathlib import Path


def export_paths(name):
    pitch = Path(__file__).resolve().parents[2] / "pitch"
    png_dir = pitch / "png"
    pdf_dir = pitch / "PDF"
    png_dir.mkdir(parents=True, exist_ok=True)
    pdf_dir.mkdir(parents=True, exist_ok=True)
    return png_dir / f"{name}.png", pdf_dir / f"{name}.pdf"
