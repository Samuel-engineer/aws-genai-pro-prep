"""Nettoie tous les caches du projet week-1."""

import argparse
import shutil
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent


def clean(include_sam: bool = False):
    removed = 0

    # __pycache__
    for d in ROOT.rglob("__pycache__"):
        shutil.rmtree(d, ignore_errors=True)
        print(f"  Supprimé: {d}")
        removed += 1

    # .pyc
    for f in ROOT.rglob("*.pyc"):
        f.unlink(missing_ok=True)
        print(f"  Supprimé: {f}")
        removed += 1

    # Dossiers de cache connus
    for name in [".pytest_cache", ".ruff_cache", ".mypy_cache"]:
        p = ROOT / name
        if p.exists():
            shutil.rmtree(p)
            print(f"  Supprimé: {p}")
            removed += 1

    # .aws-sam (optionnel)
    if include_sam:
        p = ROOT / ".aws-sam"
        if p.exists():
            shutil.rmtree(p)
            print(f"  Supprimé: {p}")
            removed += 1

    if removed == 0:
        print("  Rien à nettoyer.")
    else:
        print(f"\n{removed} élément(s) supprimé(s).")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nettoie les caches du projet")
    parser.add_argument("--all", action="store_true", help="Inclut aussi .aws-sam")
    args = parser.parse_args()

    print(f"Nettoyage dans : {ROOT}")
    clean(include_sam=args.all)
